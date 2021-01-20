# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 10:28:16 2021

This program aims at automated data processing 

@author: de Boissieu F, Feret JB
"""

# import libraries
import os, sys
from path import Path
import fordead
from fordead.masking_vi import compute_vegetation_index
import maja_fun as maja
import matplotlib as plot

###############################################################################
##                           download from THEIA                             ##
###############################################################################
# type in cmd prompt
# python Libraries/theia_download-master/theia_download.py -t T31UGP -c SENTINEL2 -a Libraries/theia_download-master/config_theia.cfg -d 2017-08-22 -f 2017-08-24 --write_dir ..\\01_DATA\\RASTER\\THEIA
# python Libraries/theia_download-master/theia_download.py -t T31UGP -c SENTINEL2 -a Libraries/theia_download-master/config_theia.cfg -d 2018-08-22 -f 2018-08-24 --write_dir ..\\01_DATA\\RASTER\\THEIA

###############################################################################
##       define location for image data, vector data & results directory     ##
###############################################################################
# define path for the zipped THEIA images
THEIA_file = [Path('../01_DATA/RASTER/THEIA/SENTINEL2B_20170823-103018-461_L2A_T31UGP_D.zip').expanduser()]

# define path for results and create directory
outdir = Path('../03_RESULTS/maja_preprocess').expanduser()
outdir.mkdir_p()

# define shapefile corresponding to the study area
shape = Path('../01_DATA/VECTOR/ZoneEtude.shp').expanduser()

###############################################################################
## process data: unzip, crop, compute spectral indices, stack & write images ##
###############################################################################
### unzip
file = maja.unzip(THEIA_file[0], outdir, overwrite=False)
file.glob('*')

### read raster & crop based spatial extent defined in vector file 
bands, mask = maja.read_maja(indir=file, shapefile=shape)

### Create a dataset including the different products resulting from processing
ds = bands.to_dataset(name='bands')
ds['mask']=mask

### compute indices: NDVI & CR_SWIR
ndvi = compute_vegetation_index(ds.bands, 'NDVI').rename('NDVI')
crswir = compute_vegetation_index(ds.bands, 'CRSWIR').rename('CRSWIR')

### produce figures
# plot of bbox
ds.bands.sel(band=['B4', 'B3', 'B2']).plot.imshow(rgb='band', vmin=0, vmax=1000)
# plot after masking
ds.bands.sel(band=['B4', 'B3', 'B2']).where(ds.mask).plot.imshow(rgb='band', vmin=0, vmax=1000)
# plot spectral indices
ndvi.plot()
crswir.where(crswir>0.5).where(crswir<1.5).plot()

# Add indices to dataset
ds['NDVI'] = ndvi
ds['CRSWIR'] = crswir

# save dataset to netcdf file
outfile = outdir / outdir.name + '.nc'
ds.to_netcdf(outfile)
# in case tifs are wanted:
ds.bands.rio.to_raster(outfile.replace('.nc', '_bands.tif'))
ds.mask.rio.to_raster(outfile.replace('.nc', '_mask.tif'))
ds.NDVI.rio.to_raster(outfile.replace('.nc', '_NDVI.tif'))
ds.CRSWIR.rio.to_raster(outfile.replace('.nc', '_CRSWIR.tif'))
