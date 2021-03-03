# -*- coding: utf-8 -*-

# Created on Tue Jan 12 10:28:16 2021

# This program aims at automated data processing 

# @author: de Boissieu F, Feret JB


# import libraries
from path import Path
from fordead.masking_vi import compute_vegetation_index
import fordead.maja_fun as maja
# import matplotlib as plot
# Cluster specification, here is an example for a local cluster (e.g. your personal computer)
# from dask.distributed import LocalCluster,Client,performance_report
# cluster = LocalCluster(n_workers=4,threads_per_worker=2, # typical values for i7 quad core: 4 cores, 2 threads/core
#                      dashboard_address=':8785', # follow processing at http://localhost:8785
#                      processes=True, # multithreaded (instead of fork)
#                      memory_limit='2GB', # memory limit by worker
#                      local_dir=Path('~/dask-worker-space').expanduser()) # temporary directory used in case of memory overload, best is on SSD drive
# cl = Client(cluster)
# cl

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
THEIA_file = Path('../../../../A_DATA/RASTER/THEIA/SENTINEL2A_20180823-103535-335_L2A_T31UGP_D.zip').abspath()
THEIA_file.isfile()
# THEIA_file = Path('../../../../A_DATA/RASTER/THEIA/SENTINEL2B_20170823-103018-461_L2A_T31UGP_D.zip').abspath()
# Get name of the image
ImName = THEIA_file.name.splitext()[0]
# define path for results and create directory
outdir = Path('../../../../C_RESULTS/maja_preprocess'/ ImName).abspath()
outdir.parent.mkdir_p()
outdir.mkdir_p()

# define shapefile corresponding to the study area
shape = Path('../../../../A_DATA/VECTOR/ZoneEtude.shp').abspath()

###############################################################################
## process data: unzip, crop, compute spectral indices, stack & write images ##
###############################################################################
### unzip
outdir_UnZip = outdir / 'Unzip'
outdir_UnZip.mkdir_p()
file = maja.unzip(THEIA_file, outdir_UnZip, overwrite=False)
file.glob('*')

### read raster & crop based spatial extent defined in vector file 
# bands, mask = maja.read_maja(indir=file, shapefile=shape, with_vrt=True) # reproject with dask chunking and parallelization, much faster for large areas.
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
outdir_preprocess = outdir / 'Subsets'
outdir_preprocess.mkdir_p()
outfile = outdir_preprocess / outdir.name + '.nc'
ds.to_netcdf(outfile,engine = 'netcdf4')
# in case tifs are wanted:
ds.bands.rio.to_raster(outfile.replace('.nc', '_bands.tif'))
ds.mask.rio.to_raster(outfile.replace('.nc', '_mask.tif'))
ds.NDVI.rio.to_raster(outfile.replace('.nc', '_NDVI.tif'))
ds.CRSWIR.rio.to_raster(outfile.replace('.nc', '_CRSWIR.tif'))
