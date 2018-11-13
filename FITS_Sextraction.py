from astropy.io import fits
from astropy import units as u
from astropy.wcs import WCS
from astropy.nddata import CCDData
import ccdproc
import numpy as np
import matplotlib.pyplot as plt
import glob, os

sextractor_params='sexconf'
sextractor_output='sexout'
processed_volume='preprocessed'

sample='g19960516'
light_id = 0

file = processed_volume+"/"+sample+"/"+str(light_id)+".fits"
print("Analyzing processed sample " + sample + ". Light ID is " + str(light_id)+". Running sextractor on " + file + " using parameters defined in " + sextractor_params + " folder.")

os.system("cd " + sextractor_params + " && sex -c asteroid.sex ../" + file)
os.system("cd " + sextractor_params + " && mv *.cat ../"+sextractor_output)
os.system("cd " + sextractor_params + " && mv *.fits ../"+sextractor_output)

print("Finished. Catalog created at " + sextractor_output + " folder.")
print("---------------------")
