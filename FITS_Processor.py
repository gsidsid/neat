from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.nddata import CCDData
from lblparser import lbl_parse
import ccdproc
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

flats_folder_format = 'flats'
darks_folder_format = 'darks'
lights_folder_format = 'obsdata'

geodss_data_volume = 'geodss/data'
tricam_data_volume = 'tricam/data'
tricam2_data_volume = 'tricam2/data'

sextractor_params = 'sexconf'
sextractor_output = 'sexout'
processed_volume = 'preprocessed'


def formFITSPaths(sample):
    """Use NEAT data conventions for mapping wget output locally to locations of files."""
    paths = dict()
    paths['darks'] = tricam_data_volume + \
        '/' + sample + '/' + darks_folder_format
    paths['flats'] = tricam_data_volume + \
        '/' + sample + '/' + flats_folder_format
    paths['lights'] = tricam_data_volume + \
        '/' + sample + '/' + lights_folder_format
    return paths


def findFITSFiles(sample):
    """Use paths to find all .fit samples and index samples accordingly."""
    paths = formFITSPaths(sample)
    files = dict()
    files['darks'] = glob.glob(paths['darks'] + '/*.fit')
    files['flats'] = glob.glob(paths['flats'] + '/*.fit')
    files['lights'] = glob.glob(paths['lights'] + '/*.fit')
    files['darks_lbl'] = glob.glob(paths['darks'] + '/*.lbl')
    files['flats_lbl'] = glob.glob(paths['flats'] + '/*.lbl')
    files['lights_lbl'] = glob.glob(paths['lights'] + '/*.lbl')
    return files


def preprocessSampleData(idx, FITSFiles, longid):
    """Use ccdproc to subtract out dark images and use flats to correct for vignetting.
       Write the processed file to the temporary preprocessed directory.
    """
    lights = FITSFiles['lights']
    dark = CCDData.read(FITSFiles['darks'][0], unit='adu')
    flat = CCDData.read(FITSFiles['flats'][0], unit='adu')
    lighted = CCDData.read(lights[idx], unit='adu')
    corr = flat.data - dark.data
    corr1 = lighted.data - dark.data
    lighted.data = corr1/flat.data
    flat_corrected = lighted
    path_plan = processed_volume + "/" + sample + "/"
    try:
        print("Attempting to build path...")
        os.makedirs(path_plan)
        print("Built!")
        print("Writing to file " + str(longid.split('.')[0]) + ".fits")
        flat_corrected.write(path_plan + str(longid.split('.')[0]) + '.fits')
    except Exception as e:
        print("Directory already exists. Writing to file " + str(longid.split('.')[0]) + ".fits")
        flat_corrected.write(path_plan + str(longid.split('.')[0]) + '.fits')
    return flat_corrected


def process(sample, idx, longid):
    preprocessSampleData(idx, findFITSFiles(sample), longid)

sample = ''
palomar = next(os.walk('tricam/data'))[1]

for s in palomar:
    sample = s
    y = [x for x in next(
            os.walk('tricam/data/' + s + '/obsdata'))[2] if x.endswith("fit")]
    for i in range(len(y)):
        try:
            print("Processing sample " + s + " #" + str(i) + "...")
            process(s, i, y[i])
            print("Done.")
        except Exception as e:
            print("Error processing. Either the file already exists, or the primary HDU is corrupted/unused.")
            pass
