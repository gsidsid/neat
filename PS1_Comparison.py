from astropy.io import ascii
from astropy.table import Table

import sys
import os
import re
import numpy as np
import json
import requests
import math

from lblparser import lbl_parse
from urllib.parse import quote as urlencode
from urllib.request import urlretrieve

import http.client as httplib


def ps1cone(ra,dec,radius,table="mean",release="dr1",format="csv",columns=None,
           baseurl="https://catalogs.mast.stsci.edu/api/v0.1/panstarrs", verbose=False,
           **kw):
    """Do a cone search of the PS1 catalog
    
    Parameters
    ----------
    ra (float): (degrees) J2000 Right Ascension
    dec (float): (degrees) J2000 Declination
    radius (float): (degrees) Search radius (<= 0.5 degrees)
    table (string): mean, stack, or detection
    release (string): dr1 or dr2
    format: csv, votable, json
    columns: list of column names to include (None means use defaults)
    baseurl: base URL for the request
    verbose: print info about request
    **kw: other parameters (e.g., 'nDetections.min':2)
    """
    
    data = kw.copy()
    data['ra'] = ra
    data['dec'] = dec
    data['radius'] = radius
    return ps1search(table=table,release=release,format=format,columns=columns,
                    baseurl=baseurl, verbose=verbose, **data)


def ps1search(table="mean",release="dr1",format="csv",columns=None,
           baseurl="https://catalogs.mast.stsci.edu/api/v0.1/panstarrs", verbose=False,
           **kw):
    """Do a general search of the PS1 catalog (possibly without ra/dec/radius)
    
    Parameters
    ----------
    table (string): mean, stack, or detection
    release (string): dr1 or dr2
    format: csv, votable, json
    columns: list of column names to include (None means use defaults)
    baseurl: base URL for the request
    verbose: print info about request
    **kw: other parameters (e.g., 'nDetections.min':2).  Note this is required!
    """
    
    data = kw.copy()
    if not data:
        raise ValueError("You must specify some parameters for search")
    checklegal(table,release)
    if format not in ("csv","votable","json"):
        raise ValueError("Bad value for format")
    url = "{baseurl}/{release}/{table}.{format}".format(**locals())
    if columns:
        # check that column values are legal
        # create a dictionary to speed this up
        dcols = {}
        for col in ps1metadata(table,release)['name']:
            dcols[col.lower()] = 1
        badcols = []
        for col in columns:
            if col.lower().strip() not in dcols:
                badcols.append(col)
        if badcols:
            raise ValueError('Some columns not found in table: {}'.format(', '.join(badcols)))
        # two different ways to specify a list of column values in the API
        # data['columns'] = columns
        data['columns'] = '[{}]'.format(','.join(columns))

# either get or post works
#    r = requests.post(url, data=data)
    r = requests.get(url, params=data)

    if verbose:
        print(r.url)
    r.raise_for_status()
    if format == "json":
        return r.json()
    else:
        return r.text


def checklegal(table,release):
    """Checks if this combination of table and release is acceptable
    
    Raises a VelueError exception if there is problem
    """
    
    releaselist = ("dr1", "dr2")
    if release not in ("dr1","dr2"):
        raise ValueError("Bad value for release (must be one of {})".format(', '.join(releaselist)))
    if release=="dr1":
        tablelist = ("mean", "stack")
    else:
        tablelist = ("mean", "stack", "detection")
    if table not in tablelist:
        raise ValueError("Bad value for table (for {} must be one of {})".format(release, ", ".join(tablelist)))


def ps1metadata(table="mean",release="dr1",
           baseurl="https://catalogs.mast.stsci.edu/api/v0.1/panstarrs"):
    """Return metadata for the specified catalog and table
    
    Parameters
    ----------
    table (string): mean, stack, or detection
    release (string): dr1 or dr2
    baseurl: base URL for the request
    
    Returns an astropy table with columns name, type, description
    """
    
    checklegal(table,release)
    url = "{baseurl}/{release}/{table}/metadata".format(**locals())
    r = requests.get(url)
    r.raise_for_status()
    v = r.json()
    # convert to astropy table
    tab = Table(rows=[(x['name'],x['type'],x['description']) for x in v],
               names=('name','type','description'))
    return tab


def mastQuery(request):
    """Perform a MAST query.

    Parameters
    ----------
    request (dictionary): The MAST request json object

    Returns head,content where head is the response HTTP headers, and content is the returned data
    """
    
    server='mast.stsci.edu'

    # Grab Python Version 
    version = ".".join(map(str, sys.version_info[:3]))

    # Create Http Header Variables
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain",
               "User-agent":"python-requests/"+version}

    # Encoding the request as a json string
    requestString = json.dumps(request)
    requestString = urlencode(requestString)
    
    # opening the https connection
    conn = httplib.HTTPSConnection(server)

    # Making the query
    conn.request("POST", "/api/v0/invoke", "request="+requestString, headers)

    # Getting the response
    resp = conn.getresponse()
    head = resp.getheaders()
    content = resp.read().decode('utf-8')

    # Close the https connection
    conn.close()

    return head,content


def resolve(name):
    """Get the RA and Dec for an object using the MAST name resolver
    
    Parameters
    ----------
    name (str): Name of object

    Returns RA, Dec tuple with position"""

    resolverRequest = {'service':'Mast.Name.Lookup',
                       'params':{'input':name,
                                 'format':'json'
                                },
                      }
    headers,resolvedObjectString = mastQuery(resolverRequest)
    resolvedObject = json.loads(resolvedObjectString)
    # The resolver returns a variety of information about the resolved object, 
    # however for our purposes all we need are the RA and Dec
    try:
        objRa = resolvedObject['resolvedCoordinate'][0]['ra']
        objDec = resolvedObject['resolvedCoordinate'][0]['decl']
    except IndexError as e:
        raise ValueError("Unknown object '{}'".format(name))
    return (objRa, objDec)

def getConeParams(lbl_filepath):
    lab = lbl_parse(lbl_filepath)
    world_ra = float(lab['RIGHT_ASCENSION'].partition('<')[0])
    world_dec = float(lab['DECLINATION'].partition('<')[0])
    hor_fov_arcsec = float(lab['HORIZONTAL_PIXEL_FOV'].partition('<')[0])
    radius = 0.18
    return (world_ra, world_dec, radius)

def parseConeQuery(result):
    if len(result) > 0:
        res_tab = ascii.read(result)
        res_tab.sort('rApMag')
        for filter in 'gr':
            col = filter+'ApMag'
            try:
                res_tab[col].format = ".4f"
                res_tab[col][res_tab[col] == -999.0] = np.nan
            except KeyError:
                print("{} not found".format(col))
    return res_tab

def starMatcher(ps1_catalog, se_catalog, error_pos, error_mag):
    ps1_ra_dec_list = list(zip(list(ps1_catalog['raMean']), list(ps1_catalog['decMean'])))
    se_ra_dec_list = list(zip(list(se_catalog['ALPHAWIN_J2000']), list(se_catalog['DELTAWIN_J2000'])))
    idx = 0
    near_list = []
    se_mags = []
    for coord in se_ra_dec_list:
        nearest_ps1 = min(ps1_ra_dec_list, key=lambda c: math.hypot(c[0] - coord[0], c[1] - coord[1]));
        if math.hypot(nearest_ps1[0]-coord[0], nearest_ps1[1]-coord[1]) < error_pos:
            print("MATCH SE-PS1 DETECT AT: " + str(nearest_ps1))
            near_list.append(ps1_ra_dec_list[idx])
            se_mags.append(float(list(se_catalog['MAG_AUTO'])[idx]))
        idx += 1
    return near_list, se_mags

search_dict = dict()
scolumns = """raMean,decMean,gApMag,rApMag""".split(',')
scolumns = [x.strip() for x in scolumns]
scolumns = [x for x in scolumns if x and not x.startswith('#')]

for catalog in [x for x in next(os.walk('sexout'))[2] if x.endswith("txt")]:
    sample_dir = catalog.partition("-")
    search_dict[catalog] = "tricam/data/" + sample_dir[0] + "/obsdata/" + sample_dir[2].partition(".")[0].partition("-")[0] + ".lbl"
    ra, dec, radius = getConeParams(search_dict[catalog])
    print("RA: " + str(ra) + ", DEC:" + str(dec))
    cat_tab = ascii.read("sexout/"+catalog)
    cat_tab.sort("MAG_AUTO");
    #top_5p = float(np.percentile(cat_tab["MAG_AUTO"], 5))
    sconstraints = {'primaryDetection':1,'rApMag.min':15, 'rApMag.max':22}
    res = ps1cone(ra,dec,radius, table="stack", release="dr2", columns=scolumns, verbose=True, **sconstraints)
    res_tab = parseConeQuery(res)
    nl,semg = starMatcher(res_tab, cat_tab, 0.003, 1)
    valid_errs = []
    for i in range(len(nl)):
        speci = list(res_tab['raMean']).index(nl[i][0])
        rmag = float(res_tab['rPSFMag'][speci])
        ourmag = float(semg[i])
        err = rmag - ourmag
        if rmag > 16 and abs(err) < 40:
            valid_errs.append(err)
    print("ADVISED MAGSHIFT: " + str(np.mean(valid_errs)))




