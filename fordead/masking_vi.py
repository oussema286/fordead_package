# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:29:17 2020

@author: Raphael Dutrieux
"""
import xarray as xr
import numpy as np
import re
from pathlib import Path
import json
from shapely.geometry import Polygon
import geopandas as gp
import pandas as pd
import rasterio
from scipy import ndimage

def bdforet_paths_in_zone(example_raster, dep_path, bdforet_dirpath):
    """
    Returns list of shapefile in the zone given by the raster, as well as the polygon extent of the raster

    Parameters
    ----------
    example_raster : xarray DataArray
        Raster from which to copy the extent and resolution for the mask
    dep_path : str
        Path to shapefile containg departements with code_insee column.
    bdforet_dirpath : str
        Path to directory containing IGN's BDFORET with one directory per departements.

    Returns
    -------
    bdforet_paths : list
        List of paths to BDFORET shapefiles of departements intersecting the example_raster
    tile_extent : geopandas GeoDataFrame
        Polygon of the extent of the example_raster

    """
    
    lon_point_list = [example_raster.attrs["transform"][2], example_raster.attrs["transform"][2]+example_raster.sizes["x"]*10, example_raster.attrs["transform"][2]+example_raster.sizes["x"]*10, example_raster.attrs["transform"][2], example_raster.attrs["transform"][2]]
    lat_point_list = [example_raster.attrs["transform"][5], example_raster.attrs["transform"][5], example_raster.attrs["transform"][5]-10*example_raster.sizes["y"], example_raster.attrs["transform"][5]-10*example_raster.sizes["y"],example_raster.attrs["transform"][5]]
    
    polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
    tile_extent = gp.GeoDataFrame(index=[0], crs=example_raster.attrs["crs"], geometry=[polygon_geom])       

    departements=gp.read_file(dep_path)
    departements=departements.to_crs(crs=example_raster.attrs["crs"]) #Changing crs
    dep_in_zone=gp.overlay(tile_extent,departements)

    #Charge la BD FORET des départements concernés et filtre selon le peuplement
    bdforet_paths = [shp_path for shp_path in Path(bdforet_dirpath).glob("**/*.shp") if str(shp_path).split("_")[-2][-2:] in list(dep_in_zone.code_insee)]   
    return bdforet_paths, tile_extent


def rasterize_bdforet(example_path, dep_path, bdforet_dirpath, 
                      list_forest_type = ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"]):
    """
    Creates forest mask from IGN's BDFORET

    Parameters
    ----------
    example_path : str
        Path to a raster from which to copy the extent and resolution for the mask
    dep_path : str
        Path to shapefile containg departements with code_insee column.
    bdforet_dirpath : str
        Path to directory containing IGN's BDFORET with one directory per departements.
    list_forest_type : list, optional
        List of forest types to be kept in the forest mask, corresponds to the CODE_TFV of the BDFORET. The default is ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"].

    Returns
    -------
    forest_mask : xarray DataArray
        Boolean DataArray containing True where pixels are in the selected forest types.

    """
    example_raster = xr.open_rasterio(example_path)
    example_raster=example_raster.sel(band=1)
    example_raster.attrs["crs"]=example_raster.crs.replace("+init=","") #Remove "+init=" which it deprecated
        
    bdforet_paths, tile_extent = bdforet_paths_in_zone(example_raster, dep_path, bdforet_dirpath) #List of paths to relevant BD foret shapefiles. Can be replaced with home-made list if your data structure is different
    
    bd_list=[(gp.read_file(bd_path,bbox=tile_extent)) for bd_path in bdforet_paths] #Warning ?
    bd_foret = gp.GeoDataFrame( pd.concat( bd_list, ignore_index=True), crs=bd_list[0].crs)
    bd_foret=bd_foret[bd_foret['CODE_TFV'].isin(list_forest_type)]    
    
    forest_mask = rasterize_polygons_binary(bd_foret, example_raster)
    return forest_mask

def rasterize_polygons_binary(polygons, example_raster):
    """
    Rasterizes polygons into binary raster

    Parameters
    ----------
    polygons : geopandas GeoDataFrame
        Polygons to rasterize
    example_raster : xarray DataArray
        Raster from which to copy the extent and resolution and crs for the mask

    Returns
    -------
    forest_mask : xarray DataArray
        Boolean DataArray containing True where pixels are inside the polygons.

    """
    
    polygons=polygons.to_crs(crs=example_raster.attrs["crs"]) #Changing crs
    polygons=polygons["geometry"]
    
    #Transforme le geopanda en json pour rasterisation
    polygons_json_str = polygons.to_json()
    polygons_json_dict = json.loads(polygons_json_str)
    polygons_json_mask = [feature["geometry"] for feature in polygons_json_dict["features"]]
    
    #Rasterisation de la BDFORET pour créer le masque
    forest_mask=rasterio.features.rasterize(polygons_json_mask,
                                            out_shape =example_raster.shape,
                                            default_value = 1, fill = 0,
                                            transform =example_raster.attrs["transform"])
    forest_mask=forest_mask.astype("bool")
    forest_mask = xr.DataArray(forest_mask, coords=example_raster.coords)
    forest_mask.attrs = example_raster.attrs
    
    return forest_mask

def clip_oso(path_oso, path_example_raster, list_code_oso):
    """
    Creates binary mask from CESBIO's soil occupation map (http://osr-cesbio.ups-tlse.fr/~oso/) by clipping it using a given raster's extent and filtering on listed values.

    Parameters
    ----------
    path_oso : str
        Path to CESBIO's OSO map.
    path_example_raster : str
        Path to raster used for clipping.
    list_code_oso : list
        List of codes used for filtering

    Returns
    -------
    forest_mask : xarray DataArray
        Boolean DataArray containing True where pixels's values in CESBIO's OSO map are in the list list_code_oso.

    """
    
    example_raster = xr.open_rasterio(path_example_raster)
    OSO = xr.open_rasterio(path_oso)
    example_raster.attrs["nodata"] = 0 #Avoids bug in reproject when nodata = nan and dtype = int
    reprojected_corner1 = example_raster.isel(x=[0,1],y=[0,1]).rio.reproject(OSO.crs).isel(x=0,y=0)
    reprojected_corner2 = example_raster.isel(x=[-2,-1],y=[-2,-1]).rio.reproject(OSO.crs).isel(x=-1,y=-1)
    clipped_OSO = OSO.rio.clip_box(
                                minx=float(reprojected_corner1.x),
                                miny=float(reprojected_corner2.y),
                                maxx=float(reprojected_corner2.x),
                                maxy=float(reprojected_corner1.y),
                                )
    reprojected_clipped_OSO = clipped_OSO.rio.reproject(example_raster.crs)
    forest_mask_data = reprojected_clipped_OSO.isin(list_code_oso)
    forest_mask = example_raster
    forest_mask.data = forest_mask_data
    # forest_mask.attrs = example_raster.attrs
    forest_mask=forest_mask.sel(band=1)
    return forest_mask

def raster_full(path_example_raster, fill_value, dtype = None):
    """
    Creates a raster with extent, resolution and projection system corresponding to a given raster, filled with a single value.

    Parameters
    ----------
    path_example_raster : str
        Path to raster used as a model.
    fill_value : int or float
        Value used to fill the raster
    dtype : type, optional
        Type of the fill_value. The default is None.

    Returns
    -------
    filled_raster : xarray DataArray
        Raster filled with a single value.

    """
    
    filled_raster = xr.open_rasterio(path_example_raster).sel(band=1)
    filled_raster[:,:]=fill_value
    filled_raster.attrs["crs"]=filled_raster.crs.replace("+init=","") #Remove "+init=" which it deprecated
    if dtype!= None : filled_raster = filled_raster.astype(dtype)
    return filled_raster

def get_pre_masks(stack_bands):   
    """
    Compute pre-masks from single date SENTINEL data

    Parameters
    ----------
    stack_bands : xarray DataArray
        3D xarray with band dimension

    Returns
    -------
    soil_anomaly : xarray DataArray
        Binary DataArray, holds True where soil anomalies are detected
    shadows : xarray DataArray
        Binary DataArray, holds True where shadows are detected
    outside_swath : xarray DataArray
        Binary DataArray, holds True where pixels are outside swath
    invalid : xarray DataArray
        Binary DataArray, aggregates shadows, very visible clouds and pixels outside swath

    """
    
    soil_anomaly = compute_vegetation_index(stack_bands, formula = "(B11 > 1250) & (B2 < 600) & ((B3 + B4) > 800)")
    # soil_anomaly = compute_vegetation_index(stack_bands, formula = "(B11 > 1250) & (B2 < 600) & (B4 > 600)")
    # soil_anomaly = compute_vegetation_index(stack_bands, formula = "(B4 + B2 - B3)/(B4 + B2 + B3)") #Bare soil index

    shadows = (stack_bands==0).any(dim = "band")
    outside_swath = stack_bands.isel(band=0)<0
    
    invalid = shadows | outside_swath | (stack_bands.sel(band = "B2") >= 600)
    
    return soil_anomaly, shadows, outside_swath, invalid


def detect_soil(soil_data, soil_anomaly, invalid, date_index):
    """
    Updates soil detection using soil anomalies from a new date

    Parameters
    ----------
    soil_data : xarray DataSet
        DataSet where variable "state" is True where pixels are detected as cut, variable "count" gives the number of successive soil anomalies, and "first_date" gives the date index of the first anomaly
    soil_anomaly : xarray DataArray
        Binary DataArray, holds True where soil anomalies are detected
    invalid : xarray DataArray
        Binary DataArray, aggregates shadows, very visible clouds and pixels outside swath
    date_index : int
        Index of the date

    Returns
    -------
    soil_data : xarray DataSet
        Updated soil_data DataSet

    """
    
    soil_data["count"]=xr.where(~invalid & soil_anomaly,soil_data["count"]+1,soil_data["count"])
    soil_data["count"]=xr.where(~invalid & ~soil_anomaly,0,soil_data["count"])
    soil_data["state"] = xr.where(soil_data["count"] == 3, True, soil_data["state"])
    soil_data["first_date"] = xr.where(~invalid & (soil_data["count"] == 1) & ~soil_data["state"],date_index,soil_data["first_date"]) #Keeps index of first soil detection
    
    return soil_data


def detect_clouds(stack_bands, soil_state, soil_anomaly):
    """
    Detects clouds, is meant to detect even faint clouds in resinous forest by removing detected soil and using a 3 pixels dilation

    Parameters
    ----------
    stack_bands : xarray DataArray
        3D xarray with band dimension
    soil_state : xarray DataArray
        DataArray which holds True where pixels are detected as cut
    soil_anomaly : xarray DataArray
        Binary DataArray, holds True where soil anomalies are detected

    Returns
    -------
    clouds : xarray DataArray
        Binary DataArray mask, holds True where clouds are detected

    """
    
    # NG = stack_bands.sel(band = "B3")/(stack_bands.sel(band = "B8A")+stack_bands.sel(band = "B4")+stack_bands.sel(band = "B3"))
    NG = compute_vegetation_index(stack_bands, formula = "B3/(B8A+B4+B3)")
    cond1 = NG > 0.15
    cond2 = stack_bands.sel(band = "B2") > 400
    cond3 = stack_bands.sel(band = "B2") > 700
    cond4 =  ~(soil_state | soil_anomaly) #Not detected as soil
    
    clouds = cond4 & (cond3 | (cond1 & cond2))    
    clouds[:,:] = ndimage.binary_dilation(clouds,iterations=3,structure=ndimage.generate_binary_structure(2, 1)) # 3 pixels dilation of cloud mask
    return clouds



def compute_masks(stack_bands, soil_data, date_index):
    """
    Computes mask from SENTINEL data, includes updated soil detection, clouds, shadows and pixels outside swath

    Parameters
    ----------
    stack_bands : xarray DataArray
        3D xarray with band dimension
    soil_data : xarray DataSet
        DataSet where variable "state" is True where pixels are detected as cut, variable "count" gives the number of successive soil anomalies, and "first_date" gives the date index of the first anomaly
    date_index : int
        Index of the date

    Returns
    -------
    mask : xarray DataArray
        Binary DataArray, holds True where pixels are masked

    """
    
    
    soil_anomaly, shadows, outside_swath, invalid = get_pre_masks(stack_bands)
    
    # Compute soil
    soil_data = detect_soil(soil_data, soil_anomaly, invalid, date_index)
        
    # Compute clouds
    clouds = detect_clouds(stack_bands, soil_data["state"], soil_anomaly)
    
    #Combine all masks
    mask = shadows | clouds | outside_swath | soil_data['state'] | soil_anomaly
    # mask.plot()
    
    return mask

def get_dict_vi(path_dict_vi = None):
    """
    Imports dictionnary containing formula of vegetation indices, as well as the way it changes in case of decline

    Parameters
    ----------
    path_dict_vi : str, optional
        Path of the text file. 
        Each line of the text file corresponds to an index, in the format "INDEX_NAME FORMULA SIGN".
        FORMULA corresponds to a formula as can be used in the function compute_vegetation_index, SIGN can be - or +. The default is None.

    Returns
    -------
    dict_vi : dict
        Dictionnary containing formula of vegetation indices, as well as the way it changes in case of decline

    """
    
    dict_vi = {"CRSWIR" : {'formula': 'B11/(B8A+((B12-B8A)/(2185.7-864))*(1610.4-864))', 'decline_change_direction': '+'},
                "NDVI" : {'formula': '(B8-B4)/(B8+B4)', 'decline_change_direction': '-'},
                "BSI" : {"formula" : '(B4 + B2 - B3)/(B4 + B2 + B3)', 'decline_change_direction' : '-'},
                "NDWI" : {"formula" : '(B8A-B11)/(B8A+B11)', 'decline_change_direction' : '-'}}
    if path_dict_vi is not None:
        d = {}
        with open(path_dict_vi) as f:
            for line in f:
                list_line = line.split()
                d[list_line[0]]={"formula" : list_line[1], "decline_change_direction" : list_line[2]}
                
        dict_vi.update(d)
    return dict_vi

def get_bands_and_formula(vi, path_dict_vi,forced_bands = []):
    formula = get_dict_vi(path_dict_vi)[vi]["formula"]
    match_string = "B(\d{1}[A-Z]|\d{2}|\d{1})"    
    bands = list(set(forced_bands + ["B"+band for band in re.findall(match_string, formula)]))
    return bands, formula
    

def compute_vegetation_index(stack_bands, vi = "CRSWIR", formula = None, path_dict_vi = None):
    """
    Computes vegetation index

    Parameters
    ----------
    stack_bands : xarray DataArray
        3D xarray with band dimension
    vi : str, optional
        Name of vegetation index, see get_dict_vi documentation to know available vegetation indices. A formula can be given instead The default is "CRSWIR".
    formula : str, optional
        Formula used to calculate the vegetation index. Bands can be called by their name. All operations on xarrays and using numpy functions are possible.
        Examples :
            NDVI : formula = '(B8-B4)/(B8+B4)'
            Squared-root of B2 : formula = 'np.sqrt(B2)'
            Logical operations :  formula = '(B2 > 600) & (B11 > 1000) | ~(B3 <= 500)'
            The default is None.
    path_dict_vi : str, optional
        Path to a text file containing vegetation indices formulas so they can be used using 'vi' parameter. See get_dict_vi documentation. The default is None.

    Returns
    -------
    xarray DataArray
        Computed vegetation index

    """
    if formula is None:
        dict_vegetation_index = get_dict_vi(path_dict_vi)
        formula = dict_vegetation_index[vi]["formula"]

    match_string = "B(\d{1}[A-Z]|\d{2}|\d{1})" # B + un chiffre + une lettre OU B + deux chiffres OU B + un chiffre
    p = re.compile(match_string)
    code_formula = p.sub(r'stack_bands.sel(band= "B\1")', formula)
    
    return eval(code_formula)

