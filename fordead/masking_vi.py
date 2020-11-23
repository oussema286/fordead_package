# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:29:17 2020

@author: admin
"""
from fordead.ImportData import import_forest_mask
from fordead.writing_data import write_tif
import xarray as xr

from path import Path
import json
from shapely.geometry import Polygon
import geopandas as gp
import pandas as pd
import rasterio

def get_forest_mask(forest_mask_path,
                    example_path = None, dep_path = None, bdforet_dirpath = None):
    """
    If a forest mask already exists at forest_mask_path, imports it.
    Else optional arguments need to be provided for the forest mask to be computed and written.

    Parameters
    ----------
    forest_mask_path : Path
        Path of the forest mask if it exists already, or path where it will be written
    example_path : Path, optional
        Path to a raster whose spatial attributes are used to compute the forest mask. Could be the path to a SENTINEL 10m band.
    dep_path : Path, optional
        Path to a shapefile containing french departements data, must contain variable code_insee 
    bdforet_dirpath : Path, optional
        Path of the directory containg a subdirectory for each departement (ex : BD_Foret_V2_Dep076_2015)
        Relevant bd foret data is selected base on subdirectories name. Other nomenclatures might cause bugs.

    Returns
    -------
    forest_mask : Array (x,y) (bool)
        Array containing True if 

    """
    if forest_mask_path.exists():
        print("Forest mask imported")
        forest_mask = import_forest_mask(forest_mask_path)
    else:
        print("Forest mask rasterized from BD Foret")

        forest_mask = rasterize_bdforet(example_path, dep_path, bdforet_dirpath)
        write_tif(forest_mask, forest_mask.attrs,nodata = 0, path = forest_mask_path)
    return forest_mask
        

def bdforet_paths_in_zone(example_raster, dep_path, bdforet_dirpath):
    lon_point_list = [example_raster.attrs["transform"][2], example_raster.attrs["transform"][2]+example_raster.sizes["x"]*10, example_raster.attrs["transform"][2]+example_raster.sizes["x"]*10, example_raster.attrs["transform"][2], example_raster.attrs["transform"][2]]
    lat_point_list = [example_raster.attrs["transform"][5], example_raster.attrs["transform"][5], example_raster.attrs["transform"][5]-10*example_raster.sizes["y"], example_raster.attrs["transform"][5]-10*example_raster.sizes["y"],example_raster.attrs["transform"][5]]
    
    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    tile_extent = gp.GeoDataFrame(index=[0], crs=example_raster.attrs["crs"], geometry=[polygon_geom])       

    departements=gp.read_file(dep_path)
    departements=departements.to_crs(crs=example_raster.attrs["crs"]) #Changing crs
    dep_in_zone=gp.overlay(tile_extent,departements)

    #Charge la BD FORET des départements concernés et filtre selon le peuplement
    bdforet_paths = [shp_path for shp_path in Path(bdforet_dirpath).glob("**/*.shp") if shp_path.split("_")[-2][-2:] in list(dep_in_zone.code_insee)]   
    return bdforet_paths, tile_extent

def rasterize_bdforet(example_path, dep_path, bdforet_dirpath, 
                      list_forest_type = ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"]):

    example_raster = xr.open_rasterio(example_path)
    example_raster=example_raster.sel(band=1)
    example_raster.attrs["crs"]=example_raster.attrs["crs"].replace("+init=","") #Remove "+init=" which it deprecated
        
    bdforet_paths, tile_extent = bdforet_paths_in_zone(example_raster, dep_path, bdforet_dirpath) #List of paths to relevant BD foret shapefiles. Can be replaced with home-made list if your data structure is different
    
    bd_list=[(gp.read_file(bd_path,bbox=tile_extent)) for bd_path in bdforet_paths]
    bd_foret = gp.GeoDataFrame( pd.concat( bd_list, ignore_index=True), crs=bd_list[0].crs)
    bd_foret=bd_foret[bd_foret['CODE_TFV'].isin(list_forest_type)]
    bd_foret=bd_foret.to_crs(crs=example_raster.attrs["crs"]) #Changing crs
    bd_foret=bd_foret["geometry"]
    
    #Transforme le geopanda en json pour rasterisation
    bd_foret_json_str = bd_foret.to_json()
    bd_foret_json_dict = json.loads(bd_foret_json_str)
    bd_foret_json_mask = [feature["geometry"] for feature in bd_foret_json_dict["features"]]
    
    #Rasterisation de la BDFORET pour créer le masque
    forest_mask=rasterio.features.rasterize(bd_foret_json_mask,
                                                  out_shape =example_raster.shape,
                                                  default_value = 1, fill = 0,
                                                  transform =example_raster.attrs["transform"])
    forest_mask=forest_mask.astype("bool")
    forest_mask = xr.DataArray(forest_mask, coords=example_raster.coords)
    forest_mask.attrs = example_raster.attrs
    
    return forest_mask