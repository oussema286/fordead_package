# -*- coding: utf-8 -*-
"""
Created on Wed Dec  7 16:25:24 2022

@author: rdutrieux
"""

"D:/fordead/Data/Sentinel/zone_feuillu/SENTINEL2A_20151207-104805-033_L2A_T31TGN_D_V1-1/SENTINEL2A_20151207-104805-033_L2A_T31TGN_D_V1-1_FRE_B2.tif"


#%% ===========================================================================
#   LIBRAIRIES
# =============================================================================
import click
import geopandas as gp
import numpy as np
from pathlib import Path
import pandas as pd
from shapely.geometry import Polygon, Point
import time

from rasterio.crs import CRS
#%% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================
from fordead.import_data import TileInfo, get_band_paths, get_raster_metadata

from fordead.validation_tests import attribute_area_to_obs, attribute_id_to_obs, buffer_obs

#%% ===========================================================================
#   FONCTIONS
# =============================================================================

def get_metadata_from_sentinel_dirs(input_directory):
    list_dir = [x for x in input_directory.iterdir() if x.is_dir()]
    dict_example_raster = {}
    for directory in list_dir:
        tile = TileInfo(directory)
        tile.getdict_datepaths("Sentinel",directory) #adds a dictionnary to tile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands
        tile.paths["Sentinel"] = get_band_paths(tile.paths["Sentinel"]) #Replaces the paths to the directories for each date with a dictionnary where keys are the bands, and values are their paths
        if len(tile.paths["Sentinel"]) >= 1:
            dict_example_raster[directory.stem] = list(list(tile.paths["Sentinel"].values())[0].values())[0]

    if len(dict_example_raster) == 0 :
        raise Exception("No directory containing Sentinel data in input_directory")
        
    for area_index, area in enumerate(dict_example_raster):
        raster_metadata = get_raster_metadata(dict_example_raster[area])
        return raster_metadata
        # lon_point_list = [raster_metadata["extent"][0],raster_metadata["extent"][2],raster_metadata["extent"][2],raster_metadata["extent"][0]]
        # lat_point_list = [raster_metadata["extent"][1],raster_metadata["extent"][1],raster_metadata["extent"][3],raster_metadata["extent"][3]]
        # # lon_point_list = [raster_metadata["transform"][2], raster_metadata["transform"][2]+raster_metadata["sizes"]["x"]*10, raster_metadata["transform"][2]+raster_metadata["sizes"]["x"]*10, raster_metadata["transform"][2], raster_metadata["transform"][2]]
        # # lat_point_list = [raster_metadata["transform"][5], raster_metadata["transform"][5], raster_metadata["transform"][5]-10*raster_metadata["sizes"]["y"], raster_metadata["transform"][5]-10*raster_metadata["sizes"]["y"],raster_metadata["transform"][5]]
        # polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
        # polygon = gp.GeoDataFrame(index=[0], crs=raster_metadata["crs"], geometry=[polygon_geom])
        # polygon.insert(1, "area_name", area)
        # if area_index == 0:
        #     concat_areas = polygon
        # else:
        #     if concat_areas.crs != polygon.crs:
        #         polygon = polygon.to_crs(concat_areas.crs)
        #     concat_areas = pd.concat([concat_areas,polygon])
    # concat_areas.to_file("E:/fordead/Data/Vecteurs/aa_concat_areas.shp")
    # 

def get_bounds(obs, crs):
    obs = obs.to_crs(crs)
    bounds = obs["geometry"].total_bounds 
    bounds[[0,1]] = bounds[[0,1]] - bounds[[0,1]] % 10 - 5
    bounds[[2,3]] = bounds[[2,3]] - bounds[[2,3]] % 10 + 15
    bounds = bounds.astype(int)
    return bounds

def polygons_to_point_grid(obs_shape, align_crs, name_column):
    grid_list = []
    for obs_index in range(obs_shape.shape[0]):
        print(obs_index)
        obs = obs_shape.iloc[obs_index:(obs_index+1)]
        
        bounds = get_bounds(obs, CRS.from_epsg(align_crs))
        
        obs_grid = gp.GeoDataFrame(
            geometry=[
                Point(x, y)
                for x in np.arange(bounds[0], bounds[2], 10)
                for y in np.arange(bounds[1], bounds[3], 10)
            ],
            crs=CRS.from_epsg(align_crs),
        ).to_crs(obs_shape.crs)
        
        obs_grid = gp.clip(obs_grid, obs)
        
        obs_grid.insert(0,"id_obs",obs[name_column].iloc[0])
        obs_grid.insert(1,"id_pixel",range(len(obs_grid)))
        grid_list += [obs_grid]
        
    final_grid = gp.GeoDataFrame( pd.concat(grid_list, ignore_index=True), crs=grid_list[0].crs)
    return final_grid

def create_grid(input_directory,path_shape, buffer, name_column, export_path, align_crs = 32631):
    # sentinel_tiles_path = "E:/fordead/Data/Vecteurs/TilesSentinel.shp"
    input_directory = Path(input_directory)
    
    raster_metadata = get_metadata_from_sentinel_dirs(input_directory)
    # areas = gp.read_file(sentinel_tiles_path).rename(columns={"Name": "area_name"})
    obs_shape = gp.read_file(path_shape).to_crs(raster_metadata["crs"])
    
    
    # obs_shape = obs_shape
    obs_shape = attribute_id_to_obs(obs_shape, name_column)
    # obs_shape = attribute_area_to_obs(obs_shape, areas, name_column)
    if buffer is not None:
        obs_shape = buffer_obs(obs_shape, buffer, name_column)

    grid = polygons_to_point_grid(obs_shape, align_crs, name_column)

    grid.to_file(export_path)
    

if __name__ == '__main__':
    start_time_debut = time.time()

    # create_grid(
    #     path_shape = "D:/fordead/Data/Validation/Validation_data/Feuillu/livrable.shp",
    #     name_column = "id",
    #     buffer = -10,
    #     input_directory = "D:/fordead/Data/Sentinel", 
    #     export_path = "D:/fordead/Data/Vecteurs/processed_livrable.shp")

    create_grid(
        path_shape = "D:/fordead/Data/Validation/Validation_data/Scolytes/ValidatedScolytes.shp",
        name_column = "Id",
        buffer = -10,
        input_directory = "D:/fordead/Data/Sentinel", 
        export_path = "D:/fordead/Data/Test_programme/grid_scolytes.shp")

    print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))

