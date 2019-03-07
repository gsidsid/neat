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

sample = ''
proc = next(os.walk('preprocessed'))[1]

for s in proc:
    sample = s
    y = [x for x in next(os.walk('preprocessed/' + sample))[2]]
    for light_id in y:
        file = processed_volume + "/" + sample + "/" + str(light_id)
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
        " -PARAMETERS_NAME sex_outcols.txt -STARNNW_NAME default_nnw.txt -c wisesex_params.txt -SATUR_LEVEL 2500 -DETECT_THRESH 2 -GAIN 4.445378 -WEIGHT_GAIN N,N -CATALOG_NAME " +
        sample + '-' + light_id[:-5] +
        "-sex-cat.txt -DEBLEND_NTHRESH 32 -DEBLEND_MINCONT 0.0001 -BACK_SIZE 130")

os.system(
    "cd " +
    sextractor_params +
    " && mv *-cat.txt ../" +
    sextractor_output)
os.system("cd " + sextractor_params + " && mv *.fits ../" + sextractor_output)

print("Finished. Catalog created at " + sextractor_output + " folder.")
print("---------------------")
