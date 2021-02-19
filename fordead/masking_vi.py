# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 17:29:17 2020

@author: Raphael Dutrieux
"""
import xarray as xr
import re
from pathlib import Path
import json
from shapely.geometry import Polygon
import geopandas as gp
import pandas as pd
import rasterio
from scipy import ndimage

def bdforet_paths_in_zone(example_raster, dep_path, bdforet_dirpath):
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
    filled_raster = xr.open_rasterio(path_example_raster).sel(band=1)
    filled_raster[:,:]=fill_value
    filled_raster.attrs["crs"]=filled_raster.crs.replace("+init=","") #Remove "+init=" which it deprecated
    if dtype!= None : filled_raster = filled_raster.astype(dtype)
    return filled_raster

def get_pre_masks(stack_bands):   
    
    soil_anomaly = compute_vegetation_index(stack_bands, formula = "(B11 > 1250) & (B2 < 600) & ((B3 + B4) > 800)")
    # soil_anomaly = compute_vegetation_index(stack_bands, formula = "(B11 > 1250) & (B2 < 600) & (B4 > 600)")
    # soil_anomaly = compute_vegetation_index(stack_bands, formula = "(B4 + B2 - B3)/(B4 + B2 + B3)") #Bare soil index

    shadows = (stack_bands==0).any(dim = "band")
    outside_swath = stack_bands.isel(band=0)<0
    
    invalid = shadows | outside_swath | (stack_bands.sel(band = "B2") >= 600)
    
    return soil_anomaly, shadows, outside_swath, invalid


def detect_soil(soil_data, premask_soil, invalid, date_index):
    soil_data["count"]=xr.where(~invalid & premask_soil,soil_data["count"]+1,soil_data["count"])
    soil_data["count"]=xr.where(~invalid & ~premask_soil,0,soil_data["count"])
    soil_data["state"] = xr.where(soil_data["count"] == 3, True, soil_data["state"])
    soil_data["first_date"] = xr.where(~invalid & (soil_data["count"] == 1) & ~soil_data["state"],date_index,soil_data["first_date"]) #Keeps index of first soil detection
    
    return soil_data


def detect_clouds(stack_bands, outside_swath, soil_data, premask_soil):
    # NG = stack_bands.sel(band = "B3")/(stack_bands.sel(band = "B8A")+stack_bands.sel(band = "B4")+stack_bands.sel(band = "B3"))
    NG = compute_vegetation_index(stack_bands, formula = "B3/(B8A+B4+B3)")
    cond1 = NG > 0.15
    cond2 = stack_bands.sel(band = "B2") > 400
    cond3 = stack_bands.sel(band = "B2") > 700
    cond4 =  ~(soil_data["state"] | premask_soil) #Not detected as soil
    
    clouds = cond4 & (cond3 | (cond1 & cond2))    
    clouds[:,:] = ndimage.binary_dilation(clouds,iterations=3,structure=ndimage.generate_binary_structure(2, 1)) # 3 pixels dilation of cloud mask
    return clouds



def compute_masks(stack_bands, soil_data, date_index):
    
    premask_soil, shadows, outside_swath, invalid = get_pre_masks(stack_bands)
    
    # Compute soil
    soil_data = detect_soil(soil_data, premask_soil, invalid, date_index)
        
    # Compute clouds
    clouds = detect_clouds(stack_bands, outside_swath, soil_data, premask_soil)
    
    #Combine all masks
    mask = shadows | clouds | outside_swath | soil_data['state'] | premask_soil
    # mask.plot()
    
    return mask

def get_dict_vi(path_dict_vi = None):
    dict_vi = {"CRSWIR" : {'formula': 'B11/(B8A+((B12-B8A)/(2185.7-864))*(1610.4-864))', 'decline_change_direction': '+'},
                "NDVI" : {'formula': '(B8-B4)/(B8+B4)', 'decline_change_direction': '-'},
                "BSI" : {"formula" : '(B4 + B2 - B3)/(B4 + B2 + B3)', 'decline_change_direction' : '-'}}
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
    
    if formula is None:
        dict_vegetation_index = get_dict_vi(path_dict_vi)
        formula = dict_vegetation_index[vi]["formula"]

    match_string = "B(\d{1}[A-Z]|\d{2}|\d{1})" # B + un chiffre + une lettre OU B + deux chiffres OU B + un chiffre
    p = re.compile(match_string)
    code_formula = p.sub(r'stack_bands.sel(band= "B\1")', formula)
    
    return eval(code_formula)

