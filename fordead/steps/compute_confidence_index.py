# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 16:40:16 2021

@author: Raphael Dutrieux
"""

from fordead.ImportData import import_stackedmaskedVI, import_decline_data, TileInfo, import_forest_mask, import_soil_data, import_coeff_model
from fordead.writing_data import write_tif, vectorizing_confidence_class, compute_confidence_index

import xarray as xr
import numpy as np

def classify_declining_area(
    data_directory,
    threshold_index,
    chunks = 1280
    ):
    print("Computing confidence index")
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"threshold_index" : threshold_index})
  
    tile.delete_dirs("confidence_index")

    tile.add_path("confidence_index", tile.data_directory / "Confidence_Index" / "confidence_index.tif")
    tile.add_path("confidence_class", tile.data_directory / "Confidence_Index" / "confidence_class.shp")
    tile.add_path("Nb_dates", tile.data_directory / "Confidence_Index" / "Nb_dates.tif")
    
    forest_mask = import_forest_mask(tile.paths["ForestMask"], chunks = chunks)
    valid_area = import_forest_mask(tile.paths["valid_area_mask"], chunks = chunks)
    soil_data = import_soil_data(tile.paths, chunks = chunks)
    decline_data = import_decline_data(tile.paths, chunks = chunks)

    relevant_area = (forest_mask & valid_area & decline_data["state"] & ~soil_data["state"]).compute()

    if tile.paths["confidence_index"].exists():
        confidence_index = xr.open_rasterio(tile.paths["confidence_index"]).squeeze(dim="band")
        Nb_dates = xr.open_rasterio(tile.paths["Nb_dates"]).squeeze(dim="band")
    else:
        coeff_model = import_coeff_model(tile.paths["coeff_model"], chunks = chunks)
        stack_vi, stack_masks = import_stackedmaskedVI(tile, min_date = tile.parameters["min_last_date_training"], chunks = chunks)
        
        confidence_index = compute_confidence_index(stack_vi, stack_masks, decline_data, coeff_model, relevant_area, tile).compute()

        write_tif(confidence_index.confidence_index, forest_mask.attrs,nodata = 0, path = tile.paths["confidence_index"])
        write_tif(confidence_index.Nb_dates, forest_mask.attrs,nodata = 0, path = tile.paths["Nb_dates"])
    
    confidence_class = vectorizing_confidence_class(confidence_index.confidence_index, confidence_index.Nb_dates, relevant_area, [threshold_index], np.array(["Stress/scolyte vert","scolyte rouge"]), tile.raster_meta["attrs"])
    confidence_class.to_file(tile.paths["confidence_class"])
    tile.save_info()
    
# classify_declining_area("D:/Documents/Deperissement/Output/ZoneEtude", 0.25)
import time
start_time = time.time()
classify_declining_area("E:/Deperissement/Out/ZoneStressLarge", 0.25)
print("Temps d execution : %s secondes ---" % (time.time() - start_time))
