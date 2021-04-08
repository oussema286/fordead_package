# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 16:40:16 2021

@author: Raphael Dutrieux
"""

from fordead.ImportData import import_stackedmaskedVI, import_decline_data, TileInfo, import_forest_mask, import_soil_data, import_coeff_model

import xarray as xr
import dask.array as da
import numpy as np
from fordead.writing_data import write_tif
from fordead.decline_detection import prediction_vegetation_index
import rasterio
from affine import Affine
import geopandas as gp


def compute_confidence_index(
    data_directory,
    threshold_index
    ):
    
    bins_classes = [threshold_index]
    classes = np.array(["Stress/scolyte vert","scolyte rouge"])
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"threshold_index" : threshold_index})
    if tile.parameters["Overwrite"] : 
        tile.delete_dirs("confidence_index") #Deleting previous detection results if they exist
    
    tile.add_path("confidence_index", tile.data_directory / "Confidence_Index" / "confidence_index.tif")
    tile.add_path("confidence_class", tile.data_directory / "Confidence_Index" / "confidence_class.shp")
 
    forest_mask = import_forest_mask(tile.paths["ForestMask"])
    valid_area = import_forest_mask(tile.paths["valid_area_mask"])
    relevant_area = forest_mask & valid_area
    
    soil_data = import_soil_data(tile.paths)
    decline_data = import_decline_data(tile.paths)
        
    coeff_model = import_coeff_model(tile.paths["coeff_model"], chunks = 1280)
    stack_vi, stack_masks = import_stackedmaskedVI(tile, chunks = 1280)
        
    indexes = xr.DataArray(da.ones(stack_masks.shape,dtype=np.uint16, chunks=stack_masks.chunks), stack_masks.coords) * xr.DataArray(range(stack_masks.sizes["Time"]), coords={"Time" : stack_masks.Time},dims=["Time"])   
    decline_dates = (indexes > decline_data["first_date"])

    
    predicted_vi=prediction_vegetation_index(coeff_model,tile.dates)
    
    # stack_vi.where(relevant_area & decline_data["state"] & ~soil_data["state"] & ~stack_masks & decline_dates).mean(dim="Time").compute().plot()
    confidence_index = (stack_vi - predicted_vi).where(relevant_area & decline_data["state"] & ~soil_data["state"] & ~stack_masks & decline_dates).mean(dim="Time").compute()
    Nb_dates = (~stack_masks).where(relevant_area & decline_data["state"] & ~soil_data["state"] & ~stack_masks & decline_dates).sum(dim="Time").compute()
    
    
    digitized = np.digitize(confidence_index,bins_classes)
    digitized[Nb_dates==3]=0
    geoms_class = list(
                {'properties': {'class_index': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    rasterio.features.shapes(digitized.astype(np.uint8), 
                                             mask =  (relevant_area & decline_data["state"] & ~soil_data["state"]).data , 
                                             transform=Affine(*tile.raster_meta["attrs"]["transform"]))))
    
    gp_results = gp.GeoDataFrame.from_features(geoms_class)
    gp_results.class_index=gp_results.class_index.astype(int)
    gp_results.insert(1,"class",classes[gp_results.class_index])
    gp_results.crs = tile.raster_meta["attrs"]["crs"].replace("+init=","")
    gp_results = gp_results.drop(columns=['class_index'])

    write_tif(confidence_index, forest_mask.attrs,nodata = 0, path = tile.paths["confidence_index"])
    gp_results.to_file(tile.paths["confidence_class"])
    tile.save_info()
    