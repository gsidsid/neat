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


def primaryHDU(file):
    """Opens the first (conventionally primary) Header Data Unit from a .fits file."""
    hdulist = fits.open(file)
    hdu = hdulist[0]
    return hdu


def HDU2CCD(hdu):
    """Converts HDU's into CCD objects for using the ccdproc preprocessing toolset."""
    CCD = CCDData(hdu.data[:, :], unit='adu')
    return CCD


def preprocessSampleData(idx, FITSFiles, longid):
    """Use ccdproc to subtract out dark images and use flats to correct for vignetting.
       Write the processed file to the temporary preprocessed directory.
    """
    sample_processed = []
    dark = HDU2CCD(primaryHDU(FITSFiles['darks'][0]))
    flat = HDU2CCD(primaryHDU(FITSFiles['flats'][0]))
    lights = FITSFiles['lights']
    #lighted = HDU2CCD(primaryHDU(lights[idx]))
    lighted = CCDData.read(lights[idx], unit='adu')
    dark_subtracted = ccdproc.subtract_dark(
        lighted,
        dark,
        dark_exposure=60 *
        u.second,
        data_exposure=60 *
        u.second,
        scale=True)
    flat_corrected = ccdproc.flat_correct(dark_subtracted, flat)
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
