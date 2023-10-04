# -*- coding: utf-8 -*-
# ===============================================================================
# PROGRAMMERS:
#
# Florian de Boissieu <fdeboiss@gmail.com>
#
#
# The code is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
#
# ===============================================================================

import zipfile
from path import Path
from rasterio.enums import Resampling
import geopandas as gpd
import numpy as np
import rioxarray as rxr
import xarray as xr
from pandas import to_datetime
import rasterio as rio
from rasterio.vrt import WarpedVRT

# other requirements:
# matplotlib # plot rasters
# descartes # plot vectors


def band_files(indir, type='FRE'):
    """
    Get band files of MAJA directory (downloaded from THEIA)
    Parameters
    ----------
    indir: str
        directory containing the raster band files
    type: str
        FRE or SRE, see notes for details.
    Returns
    -------
    list
        MAJA band files

    Notes
    -----

    SRE is for SUrface REflectance, i.e. corrected from atmospheric and environment effects.

    FRE is for Flat REflectance, adding to SRE the correction of slope effects.

    See https://labo.obs-mip.fr/multitemp/sentinel-2/theias-sentinel-2-l2a-product-format for more information.
    """
    expected_bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12']
    indir = Path(indir)
    # search for band files
    files = indir.glob('*_{}_B*.tif'.format(type))
    # sort files by band
    files = {f.name.split('_')[-1].replace('.tif',''):f for f in files}
    files = [files[b] for b in expected_bands if b in files.keys()]
    return files

def mask_file(indir, type='CLM', res=10):
    indir = Path(indir)
    mask_dir = indir / 'MASKS'
    file = mask_dir.glob('*_{}_R{}.tif'.format(type, int(res/10)))[0]
    return file


def gdf_from_else(x):
    if isinstance(x, str):
        if Path(x).isfile():
            print('Loading file: {}'.format(x))
            x = gpd.read_file(x)
        else:
            raise IOError('File not found: {}'.format(x))
    elif not isinstance(x, gpd.geodataframe.GeoDataFrame):
        raise IOError('x expected to be a GeoDataFrame or a polygon file')

    return x

def unzip(zfile, write_dir, overwrite=False):
    """
    Unzip file

    Parameters
    ----------
    zfile: str
        Zip file path
    write_dir: str
        Destination directory
    overwrite: bool

    Returns
    -------
    str
        Extracted directory path

    """
    zfile = Path(zfile)
    write_dir = Path(write_dir)

    if not zfile.isfile():
        raise IOError('File not found: {}'.format(zfile))

    if not write_dir.isdir():
        raise IOError('Directory not found: {}'.format(write_dir))

    with zipfile.ZipFile(zfile, 'r') as zf:
        outname = Path(zf.namelist()[0])
        if outname.startswith('/'):
            outname = outname.replace('/', '', 1)
        if outname.splitext()[1]!='':
            outname = outname.parent
        outdir = write_dir / outname

        if outdir.exists():
            if not overwrite:
                print('Unzipped directory already exist, set overwrite to remove existing: {}'.format(outdir))
                return outdir
            else:
                outdir.rmtree()

        zf.extractall(write_dir)

    if not outdir.isdir():
        raise Exception('Unzipped directory not found: ', outdir)

    return outdir

def read_maja(indir, shapefile=None, res=10, resampling=Resampling.cubic,
              chunks={'x': 1024, 'y': 1024, 'band': -1}, with_vrt=False, vrt_ram=64):
    """
    Read MAJA data: FRE bands and mask bbox clipped and resampled

    Parameters
    ----------
    indir: str
        MAJA file directory.
    shapefile: str
        Region of interest polygon file (1 polygon expected)
    res: float
        Target resolution.
    resampling_method: int
        rasterio.enums.Resampling method
    chunks: dict
        chunks to read/process in parallel
    with_vrt: bool
        If True uses WarpedVRT and dask delayed procesing, chunking, parallelisation for reprojection task.
    vrt_ram: int
        warp_mem_limit, see https://rasterio.readthedocs.io/en/latest/api/rasterio.vrt.html#rasterio.vrt.WarpedVRT

    Returns
    -------
    (rioxarray.DataArray, rioxarray.DataArray)
        (bands, mask)
        mask has values:
        - 0 : invalid pixel,
        - 1 : valid pixel

    """
    files = band_files(indir)
    if len(files) == 0:
        return None
    band_names = [f.splitext()[0].split('_')[-1] for f in files]

    if with_vrt:
        bands = {b: resample_raster(f, resampling=resampling, res=res, chunks=chunks, ram=vrt_ram) for b, f in
                 zip(band_names, files)}
    else:
        bands = {b: rrioxarray.open_rasterio(f, chunks=chunks) for b, f in zip(band_names, files)}

    crs = list(bands.values())[0].spatial_ref.crs_wkt

    if not (res in [10, 20]):
        mfile = mask_file(indir, res=10)
    else:
        mfile = mask_file(indir, res=res)
    mask = rrioxarray.open_rasterio(mfile, chunks=chunks).squeeze().drop('band')

    bands.update({'mask': mask})

    # bbox clip
    if shapefile is not None:
        shape = gdf_from_else(shapefile)
        s = shape.to_crs(crs)
        minx, miny, maxx, maxy = s.bounds._values[0]
        clip_bands = {}
        for bn, b in bands.items():
            new_b = b.rio.clip_box(minx, miny, maxx, maxy)
            clip_bands.update({bn: new_b})
    else:
        clip_bands = bands

    # regrid
    regrid_bands = {}
    for bn, b in clip_bands.items():
        if np.diff(b.x.data[0:2])[0] == res:
            new_b = b
        else:
            new_b = b.rio.reproject(crs, resolution=res, resampling=resampling)
        regrid_bands.update({bn: new_b})

    # convert mask values to valid=1 invalid=NA
    regrid_bands['mask'] = (regrid_bands['mask'] == 0).astype('uint8').fillna(0)
    # clip mask
    if shapefile is not None:
        geom = s.geometry.iloc[0]  # take only first polygon
        # convert mask to 1:valid, 0:invalid, and clip
        regrid_bands['mask'] = regrid_bands['mask'].rio.clip([geom], drop=False, invert=False)

    # stack
    cube = xr.concat(list(regrid_bands.values())[:-1], 'band')
    cube = cube.assign_coords(band=band_names)
    # cube.coords.update({'band': ('band', bands)})
    date_str = files[0].name.split('_')[1].split('-')[0]
    cube["time"] = to_datetime(date_str)

    return cube, regrid_bands['mask']

def resample_raster(raster_path, resampling=Resampling.cubic, res=10,
                    chunks={'x': 1024, 'y': 1024, 'band': -1}, ram=1024):
    """
    Resample raster using WarpVRT and rioxarray

    Parameters
    ----------
    raster_path: str
    resampling: int
        Method from rasterio.enums.Resampling
    res: float
        Should be a divider of raster extent.
    chunks: dict
        chunks of the output rioxarray
    ram:
        warp_mem_limit, see https://rasterio.readthedocs.io/en/latest/api/rasterio.vrt.html#rasterio.vrt.WarpedVRT

    Returns
    -------
    rioxarray.DataArray

    Notes
    -----
    Inspired of:
        - https://github.com/corteva/rioxarray/issues/119
        - https://gist.github.com/rmg55/875a2b79ee695007a78ae615f1c916b2

    """
    with rio.open(raster_path) as r:
        rx, ry = r.res
        scale_x, scale_y = rx/res, ry/res
        width, height = r.width * scale_x, r.height * scale_y
        if not (height.is_integer() and width.is_integer()):
            raise IOError('Resolution must be a divider of raster extent.')
        transform = r.transform * r.transform.scale(1 / scale_x, 1 / scale_y)
        with WarpedVRT(r, warp_mem_limit=ram, transform=transform,
                       height=height, width=width,
                       resampling=Resampling.cubic,
                       warp_extras={'NUM_THREADS': 2}) as vrt:
            ds = rrioxarray.open_rasterio(vrt).chunk(chunks)

    return ds

### with rasterio
# import tempfile
# import rasterio as rio
# import pandas as pd
# from rasterio.mask import mask
# from shapely.geometry import box
# def bbox_clip(indir, shape, outdir, overwrite=False):
#     """
#     crop to extent of shapefile
#     Parameters
#     ----------
#     indir: str
#         directory containing the rasters to crop
#     shape: str | geopandas.geodataframe.GeoDataFrame
#         Shape to clip raster with.
#     outdir: str
#         Output directory where clipped files are written.
#
#     Returns
#     -------
#     list
#         List of clipped files
#
#     """
#     outdir = Path(outdir)
#     indir = Path(indir)
#     infiles = band_files(indir)
#     outfiles = band_files(outdir)
#
#     innames = [f.name for f in infiles]
#     outnames = [f.name for f in outfiles]
#     already_exist = all([(f in outnames) for f in innames])
#     if already_exist and not overwrite:
#         print('bbox_clip not processed, files already exists: {}'.format(outfiles))
#         return outfiles
#
#     if overwrite:
#         files_to_crop = infiles
#     else:
#         files_to_crop = [f for n, f in zip(innames, infiles) if n not in outnames]
#
#
#     shape = gdf_from_else(shape)
#
#     with tempfile.TemporaryDirectory() as tmpdir:
#         tmpdir_path = Path(tmpdir)
#
#         metas = []
#         for f in files_to_crop:
#             with rio.open(f) as r:
#                 metas.append(r.meta)
#
#         metas = pd.DataFrame(metas) # convert to dataframe
#         metas['path']=files_to_crop
#         metas['res'] = [m[0] for i, m in metas['transform'].iteritems()]
#         metas['crop_path'] = [tmpdir_path / p.name for p in metas.path.to_list()]
#
#         ref_meta = metas.loc[metas.res == max(metas.res)].iloc[0]
#
#         with rio.open(ref_meta.path) as r:
#             arr, transform = mask(r, [box(*shape.to_crs(r.crs).total_bounds)], crop=True)
#
#         shape60m = bbox(arr, transform)
#
#         try:
#             for m in metas.itertuples():
#                 with rio.open(m.path) as r:
#                     arr, transform = mask(r, [shape60m], crop=True)
#                     if bbox(arr, transform) != shape60m:
#                         print('Different extent/grid: {}'.format(m.crop_path))
#                     meta = r.meta.copy()
#                     meta['transform'] = transform
#                     meta['width'] = arr.shape[-1]
#                     meta['height'] = arr.shape[-2]
#                     with rio.open(m.crop_path, 'w', **meta) as r1:
#                         r1.write(arr)
#         except Exception as e:
#             print('Crop went wrong: {}'.format(indir))
#             print('Removes temporary directory:{}'.format(tmpdir_path))
#             raise e
#
#         if outdir.isdir():
#             for m in metas.itertuples():
#                 outfile = outdir / m.crop_path.name
#                 m.crop_path.move(outfile)
#         else:
#             tmpdir_path.move(outdir)
#         outfiles = [outdir / f for f in innames]
#
#     return(outfiles)
#
# def clip(indir, shape, outdir, overwrite=False):
#     """
#     crop to extent of shapefile
#     Parameters
#     ----------
#     indir: str
#         directory containing the rasters to crop
#     shape: str | geopandas.geodataframe.GeoDataFrame
#         Shape to clip raster with.
#     outdir: str
#         Output directory where clipped files are written.
#
#     Returns
#     -------
#     list
#         List of clipped files
#     """
#     # indir = abspath('./data/S2/22KGV/S2B_MSIL1C_20190808T132239_N0208_R038_T22KGV_20190808T163402.SAFE/GRANULE/L1C_T22KGV_A012648_20190808T132736/IMG_DATA')
#     # shapefile = abspath('./data/SHP/tile_10km_sp_confidencial/base_sp.shp')
#     # outdir = abspath('./data/test')
#     outdir = Path(outdir)
#     indir = Path(indir)
#     infiles = band_files(indir)
#     outfiles = band_files(outdir)
#
#     innames = [f.name for f in infiles]
#     outnames = [f.name for f in outfiles]
#     already_exist = all([(f in outnames) for f in innames])
#     if already_exist and not overwrite:
#         print('Clip not processed, files already exists: {}'.format(outfiles))
#         return outfiles
#
#     with tempfile.TemporaryDirectory() as tmpdir:
#         tmpdir_path = Path(tmpdir)
#         files_to_clip = bbox_clip(indir, shape, tmpdir_path, overwrite=overwrite)
#
#     # if overwrite:
#     #     files_to_clip = infiles
#     # else:
#     #     files_to_clip = [f for n, f in zip(innames, infiles) if n not in outnames]
#
#         shape = gdf_from_else(shape)
#
#         with tempfile.TemporaryDirectory() as tmpdir2:
#             tmpdir_path2 = Path(tmpdir2)
#
#             metas = []
#             for f in files_to_clip:
#                 with rio.open(f) as r:
#                     metas.append(r.meta)
#
#             metas = pd.DataFrame(metas) # convert to dataframe
#             metas['path']=files_to_clip
#             metas['res'] = [m[0] for i, m in metas['transform'].iteritems()]
#             metas['clip_path'] = [tmpdir_path / p.name for p in metas.path.to_list()]
#
#             try:
#                 for m in metas.itertuples():
#                     with rio.open(m.path) as r:
#                         arr, transform = mask(r, shape.to_crs(r.crs).geometry.to_list())
#                         meta = r.meta.copy()
#                         meta['transform'] = transform
#                         meta['width'] = arr.shape[-1]
#                         meta['height'] = arr.shape[-2]
#                         with rio.open(m.clip_path, 'w', **meta) as r1:
#                             r1.write(arr)
#             except Exception as e:
#                 print('Clip went wrong: {}'.format(indir))
#                 print('Removes temporary directory:{}'.format(tmpdir_path))
#                 raise e
#
#             if outdir.isdir():
#                 for m in metas.itertuples():
#                     outfile = outdir / m.clip_path.name
#                     m.clip_path.move(outfile)
#             else:
#                 tmpdir_path.move(outdir)
#             outfiles = [outdir / f for f in innames]
#
#     return(outfiles)
#
# def bbox(arr, transform):
#     """
#     Get the bounding box of raster
#     Parameters
#     ----------
#     arr: numpy.array
#     transform: rasterio.transform
#
#     Returns
#     -------
#     shapely.geometry.box
#     """
#     return box(*(list(transform * [0, 0]) + list(transform * reversed(list(arr.shape)[-2:]))))
#
#
# def resample_raster(raster_path, outfile='', resampling=Resampling.nearest, res=10, overwrite=False):
#     """
#     Resample a raster file
#
#     Parameters
#     ----------
#     raster_path: str
#         Path to the raster file.
#     outfile: str
#         Path to the outputfile. If empty, data and transform are returned.
#     resampling: rasterio.enums.Resampling method
#     res: int
#         Final resolution
#     overwrite: bool
#
#     Returns
#     -------
#     str or (numpy.array, rasterio.transform)
#
#     """
#
#     outfile = Path(outfile)
#     if outfile.isfile() and not overwrite:
#         print('Resample not processed, directory already exists: {}'.format(outfile))
#         return outfile
#     with rio.open(raster_path) as r:
#         # resample data to target shape
#         rx, ry = r.res
#         # if (rx==res) and (ry==res) and outfile==raster_path:
#         #     print(f'Resample not processed, resolution is already {res}')
#         #     if outfile=='':
#         #         return
#         #     return outfile
#
#         raster_meta = r.meta
#         raster_data = r.read(
#             out_shape=(
#                 r.count,
#                 int(r.height * ry/res),
#                 int(r.width * rx/res)
#             ),
#             resampling=resampling
#         )
#
#         # scale image transform
#         raster_transform = r.transform * r.transform.scale(
#             (r.width / raster_data.shape[-1]),
#             (r.height / raster_data.shape[-2])
#         )
#         raster_meta['width'] = raster_data.shape[-1]
#         raster_meta['height'] = raster_data.shape[-2]
#         raster_meta['transform'] = raster_transform
#
#         if outfile != '':
#             tmpfile = Path(tempfile.NamedTemporaryFile(suffix=outfile.ext).name)
#             with rio.open(tmpfile, 'w', **raster_meta) as rw:
#                 rw.write(raster_data)
#             tmpfile.move(outfile)
#             return outfile
#
#         return raster_data, raster_meta

# def stack(band_files, outputfile, res=10, resampling=Resampling.nearest, overwrite=False, verbose=False):
#     """
#     Stack bands into an only file.
#
#     Parameters
#     ----------
#     band_files: list
#         list of file paths to stack into the output file.
#     outputfile: str
#         file path to be written (with the correct extension)
#     verbose: bool
#         if True, it gives a message when files are written.
#
#     Returns
#     -------
#
#     """
#
#     outputfile = Path(outputfile)
#     if outputfile.exists() and not overwrite:
#         print('Stacking not processed, file already exists: {}'.format(outputfile))
#         return outputfile
#
#     if verbose:
#         print('Resampling bands...')
#
#     bandlist = []
#     dst_meta_list = []
#     for bf in band_files:
#         raster_data, raster_meta = resample_raster(bf, resampling=resampling, res=res)
#         bandlist.append(raster_data[0,:,:])
#         dst_meta_list.append(raster_meta)
#
#     if any([m!=dst_meta_list[0] for m in dst_meta_list]):
#         raise IOError('Metadata are not uniform and cannot be stacked.')
#
#     dst_meta = dst_meta_list[0]
#
#     if verbose:
#         print('Stacking bands...')
#     # write bands in file
#     dst_meta['count'] = len(bandlist)
#     # dst_meta['driver'] = driver
#     with rio.open(outputfile, 'w', **dst_meta) as dst:
#         dst.write(np.array(bandlist))
#         # for i, band in enumerate(bandlist, 1):
#         #     dst.write(band, indexes=i)
#
#     if verbose:
#         print('Bands stacked into: {}'.format(outputfile))
#
#     return outputfile

# def preprocess_maja(infile, shape, outdir, res=10, overwrite=False, verbose=True):
#     infile = Path(infile)
#     outdir = Path(outdir)
#
#     outdir.mkdir_p()
#
#     ### clip
#     clip_dir = outdir / 'clipped' / infile.name
#     clip_dir.parent.mkdir_p()
#     # outfile = bbox_clip(outfile, shape, clip_dir, overwrite=overwrite)
#     outfiles = clip(infile, shape, clip_dir, overwrite=overwrite)
#
#     ### Resample
#     resampled_dir = outdir / 'resampled' / infile.name
#     resampled_dir.parent.mkdir_p()
#     resampled_dir.mkdir_p()
#     routfiles=[]
#     for f in outfiles:
#         outfile = resample_raster(f, resampled_dir / f.name, res=10)
#         routfiles.append(outfile)
#
#     ### stack
#     stack_file = outdir / 'stacked' / clip_dir.name + '_{}m.tif'.format(res)
#     stack_file.parent.mkdir_p()
#     stack(outfiles, stack_file, res=res, overwrite=overwrite)
#
#     return stack_file
