import pandas as pd
from shapely.geometry import Polygon, Point
import json
import rasterio
import xarray as xr
import geopandas as gp
import pandas as pd
import ast
from pathlib import Path
from scipy.linalg import lstsq
import numpy as np
from rasterio.crs import CRS

from fordead.masking_vi import get_dict_vi
from fordead.masking_vi import compute_vegetation_index
from fordead.import_data import TileInfo, get_band_paths, get_raster_metadata


# import rasterio.sample
# =============================================================================
# PREPROCESS POLYGONS
# =============================================================================

def attribute_id_to_obs(obs, name_column):
    """
    Adds an ID column if it doesn't already exists. If column named after name_column parameter does not exist in the geodataframe, adds one with integers from 1 to the number of observations.

    Parameters
    ----------
    obs : geopandas GeoDataFrame
        Observation points or polygons
    name_column : str
        Name of the ID column.

    Returns
    -------
    obs : geopandas GeoDataFrame
        Observation points or polygons with added column named using parameter name_column if it doesn't already exist.

    """
    
    if name_column not in obs.columns:
        print("Creating " + name_column + " column")
        obs.insert(1, name_column, range(1,len(obs)+1))
    return obs

def buffer_obs(obs, buffer, name_column):
    """
    Applies a buffer to dilate or erode observations. Names of discarded observations too small compared to a eroding buffer are printed.

    Parameters
    ----------
    obs : geopandas GeoDataFrame
        Observation points or polygons with a column named name_column used to identify observations.
    buffer : int
        Length in meters of the buffer used to dilate (positive integer) or erode (negative integer) the observations. Some observations may disappear completely if a negative buffer is applied.
    name_column : str
        Name of the column used to identify observations.

    Returns
    -------
    obs : geopandas GeoDataFrame
        Observation polygons with the buffer applied.

    """
    
    obs['geometry']=obs.geometry.buffer(buffer)
    empty_obs = obs[obs.is_empty]
    if len(empty_obs) != 0:
        print(str(len(empty_obs)) + " observations were too small for the chosen buffer. \nIds are the following : \n" + ', '.join(map(str, empty_obs[name_column])) + " \n")
    obs=obs[~(obs.is_empty)]
    return obs


# =============================================================================
#   MAKE GRID POINTS
# =============================================================================

def get_grid_points(obs_polygons, sentinel_dir, name_column, list_tiles):
    """
    Generates points in a grid corresponding to the centroids of Sentinel-2 pixels inside the polygons.
    

    Parameters
    ----------
    obs_polygons : geopandas GeoDataFrame
        Observation polygons with a column named name_column used to identify observations.
    sentinel_dir : str
        Path of directory containing Sentinel-2 data.
    name_column : str
        Name of the column used to identify observations.
    list_tiles : list
        A list of names of Sentinel-2 directories. If this parameter is used, extraction is  limited to those directories.

    Returns
    -------
    grid_points : geopandas GeoDataFrame
        Points corresponding to the centroids of the Sentinel-2 pixels of each Sentinel-2 tile intersecting with the polygons.

    """
    
    sen_obs_intersection = get_sen_obs_intersection(obs_polygons, sentinel_dir, name_column, list_tiles)
    
    grid_points = polygons_to_grid_points(sen_obs_intersection, name_column)
    
    return grid_points
    

def get_sen_obs_intersection(obs_polygons, sentinel_dir, name_column, list_tiles):
    """
    Creates a Sentinel-2 tiles extent vector from existing Sentinel-2 data, then intersects it with observations polygons, adding their epsg and name.
    Polygons which do not fit enterely in at least one existing Sentinel-2 tile are removed.
    
    Parameters
    ----------
    obs_polygons : geopandas GeoDataFrame
        Observation polygons with ID column named after name_column parameter.
    sentinel_dir : str
        Path of directory containing Sentinel-2 data.
    name_column : str
        Name of the column used to identify observations.
    list_tiles : list
        A list of names of Sentinel-2 directories. If this parameter is used, extraction is  limited to those directories.

    Returns
    -------
    sen_intersection : geopandas GeoDataFrame
        Intersection of obs_polygons and Sentinel-2 tiles, adding 'area_name' and 'epsg' columns corresponding to the name of the tile, and the projection system respectively. 

    """
    
    sen_polygons = get_polygons_from_sentinel_dirs(sentinel_dir, list_tiles)
    
    sen_obs_intersection = get_sen_intersection(obs_polygons, sen_polygons, name_column)
    
    return sen_obs_intersection

def get_polygons_from_sentinel_dirs(sentinel_dir, list_tiles):
    """
    Creates a Sentinel-2 tiles extent vector from existing Sentinel-2 data

    Parameters
    ----------
    sentinel_dir : str
        Path of directory containing Sentinel-2 data.
    list_tiles : list
        A list of names of Sentinel-2 directories. If this parameter is used, extraction is  limited to those directories.

    Returns
    -------
    concat_areas : geopandas GeoDataFrame
        Vector containing the extent of Sentinel-2 tiles contained in sentinel_dir directory, with 'epsg' and 'area_name' columns corresponding to the projection system and the name of the tile derived from the name of the directory containing its data.

    """
    
    list_dir = [x for x in sentinel_dir.iterdir() if x.is_dir()]
    dict_example_raster = {}
    for directory in list_dir :
        if list_tiles is None or directory.stem in list_tiles:
        # for directory in list_dir :
            tile = TileInfo(directory)
            tile.getdict_datepaths("Sentinel",directory) #adds a dictionnary to tile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands
            tile.paths["Sentinel"] = get_band_paths(tile.paths["Sentinel"]) #Replaces the paths to the directories for each date with a dictionnary where keys are the bands, and values are their paths
            if len(tile.paths["Sentinel"]) >= 1:
                dict_example_raster[directory.stem] = list(list(tile.paths["Sentinel"].values())[0].values())[0]
    if len(dict_example_raster) == 0 :
        raise Exception("No Sentinel-2 data to extract")
    for area_index,area in enumerate(dict_example_raster):
        raster_metadata = get_raster_metadata(dict_example_raster[area])
        
        lon_point_list = [raster_metadata["extent"][0],raster_metadata["extent"][2],raster_metadata["extent"][2],raster_metadata["extent"][0]]
        lat_point_list = [raster_metadata["extent"][1],raster_metadata["extent"][1],raster_metadata["extent"][3],raster_metadata["extent"][3]]
        # lon_point_list = [raster_metadata["transform"][2], raster_metadata["transform"][2]+raster_metadata["sizes"]["x"]*10, raster_metadata["transform"][2]+raster_metadata["sizes"]["x"]*10, raster_metadata["transform"][2], raster_metadata["transform"][2]]
        # lat_point_list = [raster_metadata["transform"][5], raster_metadata["transform"][5], raster_metadata["transform"][5]-10*raster_metadata["sizes"]["y"], raster_metadata["transform"][5]-10*raster_metadata["sizes"]["y"],raster_metadata["transform"][5]]
        polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
        polygon = gp.GeoDataFrame(index=[0], crs=raster_metadata["crs"], geometry=[polygon_geom])
        polygon.insert(1, "area_name", area)
        polygon.insert(2, "epsg", raster_metadata["crs"].to_epsg())
        
        if area_index == 0:
            concat_areas = polygon
        else:
            if concat_areas.crs != polygon.crs:
                polygon = polygon.to_crs(concat_areas.crs)
            concat_areas = pd.concat([concat_areas,polygon])
    # concat_areas.to_file("E:/fordead/Data/Vecteurs/aa_concat_areas.shp")
    return concat_areas

def get_sen_intersection(obs_polygons, sen_polygons, name_column):
    """
    Observations polygons are intesected with Sentinel-2 tiles extent vector. Intersections where the observation polygon did not entirely fit in the sentinel-2 tile are removed.
    Observation polygons which intersect no Sentinel-2 tiles are removed and their IDs are printed.


    Parameters
    ----------
    obs_polygons : geopandas GeoDataFrame
        Polygons of observations.
    sen_polygons : geopandas GeoDataFrame
        Polygons of Sentinel-2 tiles extent with 'area_name' and 'epsg' columns corresponding to the name of the tile, and the projection system respectively.
    name_column : str
        Name of the ID column.

    Returns
    -------
    geopandas GeoDataFrame
        Intersection of obs_polygons and sen_polygons, with incomplete intersections removed.

    """
    
    obs_polygons = obs_polygons.to_crs(sen_polygons.crs)
    obs_area_tot = obs_polygons[[name_column]]
    obs_area_tot.insert(1, "area_tot", obs_polygons.area)
    
    obs_polygons = obs_polygons.merge(obs_area_tot, on= name_column, how='left')
    obs_intersection = gp.overlay(obs_polygons, sen_polygons)
    
    obs_intersection.insert(1, "area_intersect", obs_intersection.area)
    obs_intersection = obs_intersection[obs_intersection["area_tot"].round(3) == obs_intersection['area_intersect'].round(3)]
    
    unvalid_obs = obs_polygons[~obs_polygons[name_column].isin(obs_intersection[name_column])]
    if len(unvalid_obs) != 0:
        print("Observations not fitting entirely on one tile found.\nThey are removed from the dataset. \nIds are the following : \n" + ', '.join(map(str, unvalid_obs[name_column])) + " \n")
    
    # return obs_intersection[[name_column,"area_name","epsg"]]
    return obs_intersection.drop(columns = ["area_intersect","area_tot"])


# =============================================================================


def polygons_to_grid_points(polygons, name_column):
    """
    Converts polygons to points corresponding to the centroids of the Sentinel-2 pixels of each Sentinel-2 tile intersecting with the polygons.
    Prints polygons with no pixels centroids inside of them.  
    
    Parameters
    ----------
    polygons : geopandas GeoDataFrame
        Observation polygons with 'area_name' and 'epsg' columns, corresponding to the name of a Sentinel-2 tile and its CRS respectively.
    name_column : str
        Name of the ID column.

    Returns
    -------
    grid_points : geopandas GeoDataFrame
        Points corresponding to the centroids of the Sentinel-2 pixels of each Sentinel-2 tile intersecting with the polygons.

    """
    
    # polygons = obs_polygons.merge(polygon_area_crs, on= name_column, how='inner') 
    
    grid_list = []
    for epsg in np.unique(polygons.epsg):
        print("epsg : " + str(epsg))
        
        polygons_epsg = polygons[polygons.epsg == epsg]
        polygons_epsg = polygons_epsg.to_crs(epsg = epsg)
        
        for area_name in np.unique(polygons.area_name):
            polygons_area = polygons_epsg[polygons_epsg.area_name == area_name]
        
            for polygon_index in range(polygons_area.shape[0]):
                polygon = polygons_area.iloc[polygon_index:(polygon_index+1)]
                
                bounds = get_bounds(polygon)
                
                obs_grid = gp.GeoDataFrame(
                    geometry=[
                        Point(x, y)
                        for x in np.arange(bounds[0], bounds[2], 10)
                        for y in np.arange(bounds[1], bounds[3], 10)
                    ],
                    crs=CRS.from_epsg(epsg),
                ).to_crs(CRS.from_epsg(epsg))
                
                obs_grid = gp.clip(obs_grid, polygon)
                
                obs_grid.insert(0,name_column,polygon[name_column].iloc[0])
                obs_grid.insert(1,"id_pixel",range(1,len(obs_grid)+1))
                obs_grid.insert(0,"area_name",area_name)
                obs_grid.insert(0,"epsg",epsg)
                obs_grid = obs_grid.to_crs(polygons.crs)
                
                if len(obs_grid) == 0:
                    print("Polygon " + str(polygon.iloc[0][name_column]) + " contains no pixel centroid")
                
                grid_list += [obs_grid]
                
        
    try:
        grid_points = gp.GeoDataFrame( pd.concat(grid_list, ignore_index=True), crs=grid_list[0].crs)
    except ValueError:
        raise Exception("It is probable that none of the observations intersect with the Sentinel-2 data available")
        
    return grid_points

def get_bounds(obs):
    """
    Get bounds of around of a polygons so it matches the limits of Sentinel-2 pixels
    
    Parameters
    ----------
    obs : geopandas GeoDataFrame
        A polygon

    Returns
    -------
    bounds : 1D array
        Bounds around the polygon

    """
    
    bounds = obs["geometry"].total_bounds 
    bounds[[0,1]] = bounds[[0,1]] - bounds[[0,1]] % 10 - 5
    bounds[[2,3]] = bounds[[2,3]] - bounds[[2,3]] % 10 + 15
    bounds = bounds.astype(int)
    return bounds


# =============================================================================
#   GET REFLECTANCE AT POINTS
# =============================================================================


def get_reflectance_at_points(grid_points,sentinel_dir, extracted_reflectance, name_column, bands_to_extract, tile_selection):
    reflectance_list = []
    
    if tile_selection is not None:
        grid_points = grid_points[grid_points["area_name"].isin(tile_selection)]
        if len(grid_points) == 0:
            raise Exception("No observations in selected tiles")
    
    for epsg in np.unique(grid_points.epsg):
        print("epsg : " + str(epsg))
        points_epsg = grid_points[grid_points.epsg == epsg]
        points_epsg = points_epsg.to_crs(epsg = epsg)
        
        for area_name in np.unique(points_epsg.area_name):
            print("area_name : " + area_name)
            points_area = points_epsg[points_epsg.area_name == area_name]
            
            if extracted_reflectance is not None:
                extracted_reflectance_area = extracted_reflectance[extracted_reflectance["area_name"] == area_name]
            else:
                extracted_reflectance_area = None
            
            raster_values = extract_raster_values(points_area, sentinel_dir / area_name, extracted_reflectance_area, name_column, bands_to_extract)
            
            if raster_values is not None:
                reflectance_list += [raster_values]
    # reflectance = gp.GeoDataFrame(pd.concat(reflectance_list, ignore_index=True), crs=reflectance_list[0].crs)
    if len(reflectance_list) != 0:
        reflectance = pd.concat(reflectance_list, ignore_index=True)
        if "Mask" in bands_to_extract:
            reflectance["Mask"] = reflectance["Mask"].astype(np.uint8)
    else:
        reflectance = None
        
    return reflectance

def extract_raster_values(points, tile_coll, extracted_reflectance, name_column, bands_to_extract):
    """
    Sample raster values for each XY points

    - points: <geodataframe> observation points
    - tile_coll: <pystac object> item_collection filtered according to S2 Tile
    - extracted_reflectance: <dataframe> table of sampled raster value
    - name_column: <string> column name

    return: <dataframe> table of sampled raster value
    """
    #"""Must have the same crs"""
    # tile = TileInfo(sentinel_dir)
    # tile.getdict_datepaths("Sentinel",sentinel_dir) #adds a dictionnary to tile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands
    # tile.paths["Sentinel"] = get_band_paths(tile.paths["Sentinel"]) #Replaces the paths to the directories for each date with a dictionnary where keys are the bands, and values are their paths
    
    coord_list = [(x,y) for x,y in zip(points['geometry'].x , points['geometry'].y)]
    points = points.drop(columns='geometry')
    date_band_value_list = []
    
    if extracted_reflectance is not None:
        #Determiner les dates qui restent.
        to_extract_reflectance = points[["area_name", name_column]].drop_duplicates()
        #Supprimer duplicates id_pixel
        
        #inner_join extracted_reflectance avec marqueur
        extracted_reflectance = to_extract_reflectance.merge(extracted_reflectance, on= ["area_name", name_column], how='left', indicator = True) 
        # to_extract_reflectance = to_extract_reflectance.merge(extracted_reflectance, on= ["area_name", name_column], how='left', indicator = True) 
        #list_dates de unique dates
    
    for item in tile_coll:
        
        date = item.properties["datetime"].split('T')[0]
        # print(date)
        

        # print('\r', date, " | ", len(tile.paths["Sentinel"])-date_index-1, " remaining       ", sep='', end='', flush=True) if date_index != (len(tile.paths["Sentinel"]) -1) else print('\r', '                                              ', '\r', sep='', end='', flush=True)
        extraction = points.copy()
        if extracted_reflectance is not None:
            #Filter les points selon la date
            extracted_reflectance_date = extracted_reflectance[extracted_reflectance["Date"] == date]
            
            #Filter extracted_reflectance avec les date
            extraction = extraction[~extraction[name_column].isin(extracted_reflectance_date[name_column])]
            
        if len(extraction) != 0:
            print('\r', date , sep='', end='', flush=True)
            extraction.insert(4,"Date",date)
            # len(extraction.columns)-1
            for band in bands_to_extract:
                image = item.assets[band].href
            
                with rasterio.open(image) as raster:
                    extraction[band] = [x[0] for x in raster.sample(coord_list)]
                
            date_band_value_list += [extraction]
    print('\r', "               \n" , sep='', end='', flush=True)
    # reflectance = gp.GeoDataFrame(pd.concat(date_band_value_list, ignore_index=True), crs=date_band_value_list[0].crs)
    if len(date_band_value_list) != 0:
        reflectance = pd.concat(date_band_value_list, ignore_index=True)
        return reflectance
    else:
        return None

    

# ==========================================================================================================================================================

# =============================================================================
#   process_points
# =============================================================================

def process_points(points, sentinel_dir, name_column, list_tiles):
    """
    Creates a Sentinel-2 tiles extent vector from existing Sentinel-2 data, then intersects it with observations points, adding their epsg and name.

    Parameters
    ----------
    points : geopandas GeoDataFrame
        Points used to intersect with Sentinel-2 tiles.
    sentinel_dir : str
        Path of directory containing Sentinel-2 data.
    name_column : str
        Name of the ID column in points.
    list_tiles : list
        A list of names of Sentinel-2 directories. If this parameter is used, extraction is limited to those directories.

    Returns
    -------
    geopandas GeoDataFrame
        Points with added 'epsg', 'area_name' and 'id_pixel' columns.

    """
    
    #Check if already has name_area
    # sen_polygons = get_points_area_crs(points, sentinel_dir, name_column)
    
    sen_polygons = get_polygons_from_sentinel_dirs(sentinel_dir, list_tiles)
    
    sen_intersection_points = get_sen_intersection_points(points, sen_polygons, name_column)
    
    return sen_intersection_points[["epsg","area_name",name_column,"id_pixel","geometry"]]
    

def get_sen_intersection_points(points, sen_polygons, name_column):
    """
    Intersects observation points with Sentinel-2 tiles extent vector.
    Adds an 'id_pixel' column filled with 0 so the resulting vector can be used in export_reflectance function.
    Points outside of available Sentinel-2 tiles are detected and their IDs are printed.
    
    Parameters
    ----------
    points : geopandas GeoDataFrame
        Observation points used for intersection
    sen_polygons : geopandas GeoDataFrame
        Polygons of Sentinel-2 tiles extent with 'area_name' and 'epsg' columns corresponding to the name of the tile, and the projection system respectively.
    name_column : str
        Name of the ID column in points

    Returns
    -------
    obs_intersection : geopandas GeoDataFrame
        Intersection of points and sen_polygons, with added 'id_pixel' columns

    """
    
    sen_polygons = sen_polygons.to_crs(points.crs)
    obs_intersection = gp.overlay(points, sen_polygons)
    # obs_intersection["id_pixel"] = 0
    obs_intersection.insert(1,"id_pixel",1) #Insert column
    
    outside_points = points[~points[name_column].isin(obs_intersection[name_column])]
    
    if len(outside_points) != 0:
        print(str(len(outside_points)) + " point observations were outside available Sentinel-2 tiles.\nThey are removed from the dataset. \nIds are the following : \n" + ', '.join(map(str, outside_points[name_column])) + " \n")

    if len(obs_intersection) == 0 :
        raise Exception("No available Sentinel-2 tiles at point locations")
    
    return obs_intersection
    

def get_already_extracted(export_path, obs, obs_path, name_column):
    """
    
    Returns already extracted acquisition dates for each observation and each tile.
    Detects if the number of observations changed since last extraction and warns the user.

    """
    
    if export_path.exists():
        reflectance = pd.read_csv(export_path)
        if name_column not in reflectance.columns:
            # raise Exception("name_column '"+ name_column + "' not in reflectance.csv found in " + str(export_dir))
            raise Exception("name_column '"+ name_column + "' not in " + str(export_path))

        extracted_reflectance = reflectance[["area_name", name_column,"Date"]].drop_duplicates()
        
        obs_extracted = np.unique(extracted_reflectance[name_column])
        obs_to_extract = np.unique(obs[name_column])
        
        diff_nb_obs = len(obs_extracted) != len(obs_to_extract)
        missing_obs = not(all(item in obs_to_extract for item in obs_extracted))
        added_obs = not(all(item in obs_extracted for item in obs_to_extract))
        
        if diff_nb_obs or missing_obs or added_obs:
            print("Changes to "+ str(obs_path) + " have been detected since last extracting reflectances to " + str(export_path))
            if diff_nb_obs:
                print("Different number of observations detected")
            if missing_obs:
                print("Some observations are missing, already extracted reflectance will stay untouched")
            if added_obs:
                print("Some observations were added, their reflectance will be extracted")
            answer = input("Do you want to continue ? (yes/no)")
            if answer != "yes":
                raise Exception("Extraction of reflectance stopped")

        return extracted_reflectance
    else:
        return None
    
    
