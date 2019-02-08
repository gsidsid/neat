from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.nddata import CCDData
import ccdproc
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

sextractor_params = 'sexconf'
sextractor_output = 'sexout'
processed_volume = 'preprocessed'

sample = 'p20020109'
light_id = '20020109022041d'

file = processed_volume + "/" + sample + "/" + str(light_id) + ".fits"
print(
    "Analyzing processed sample " +
    sample +
    ". Light ID is " +
    light_id +
    ". Running sextractor on " +
    file +
    " using parameters defined in " +
    sextractor_params +
    " folder.")

os.system(
    "cd " +
    sextractor_params +
    " && sex ../" +
    file +
    " -PARAMETERS_NAME sex_outcols.txt -FILTER_NAME gauss_5.0_9x9_conv.txt -STARNNW_NAME default_nnw.txt -c wisesex_params.txt -MAG_ZEROPOINT 20.5 -SATUR_LEVEL 2500 -DETECT_THRESH 2 -GAIN 1.0e+20 -WEIGHT_GAIN N,N -CATALOG_NAME " +
    sample + '-' + light_id +
    "-sex-cat.txt -CHECKIMAGE_TYPE -OBJECTS,BACKGROUND -CHECKIMAGE_NAME obj.fits,bck.fits -DEBLEND_NTHRESH 32 -DEBLEND_MINCONT 0.0001 -BACK_SIZE 130")
os.system(
    "cd " +
    sextractor_params +
    " && mv *-cat.txt ../" +
    sextractor_output)
os.system("cd " + sextractor_params + " && mv *.fits ../" + sextractor_output)

print("Finished. Catalog created at " + sextractor_output + " folder.")
print("---------------------")
