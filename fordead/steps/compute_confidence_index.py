# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 16:40:16 2021

@author: Raphael Dutrieux
"""

from fordead.ImportData import import_stackedmaskedVI, import_decline_data, TileInfo, import_forest_mask, import_soil_data, import_coeff_model
import xarray as xr
import numpy as np
from fordead.writing_data import write_tif, vectorizing_confidence_class, compute_confidence_index
import time 
def classify_declining_area(
    data_directory,
    threshold_index
    ):
    print("Computing confidence index")
    start_time = time.time()
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"threshold_index" : threshold_index})
    
    tile.add_path("confidence_index", tile.data_directory / "Confidence_Index" / "confidence_index.tif")
    tile.add_path("confidence_class", tile.data_directory / "Confidence_Index" / "confidence_class.shp")
    tile.add_path("Nb_dates", tile.data_directory / "Confidence_Index" / "Nb_dates.tif")
    
    forest_mask = import_forest_mask(tile.paths["ForestMask"], chunks = 1280)
    valid_area = import_forest_mask(tile.paths["valid_area_mask"], chunks = 1280)
    soil_data = import_soil_data(tile.paths, chunks = 1280)
    decline_data = import_decline_data(tile.paths, chunks = 1280)

    relevant_area = (forest_mask & valid_area & decline_data["state"] & ~soil_data["state"]).compute()

    # if tile.paths["confidence_index"].exists():
    if False:
        confidence_index = xr.open_rasterio(tile.paths["confidence_index"]).squeeze(dim="band")
        Nb_dates = xr.open_rasterio(tile.paths["Nb_dates"]).squeeze(dim="band")
    else:
        coeff_model = import_coeff_model(tile.paths["coeff_model"], chunks = 1280)
        stack_vi, stack_masks = import_stackedmaskedVI(tile, min_date = tile.parameters["min_last_date_training"], chunks = 1280)
        
        confidence_index, Nb_dates = compute_confidence_index(stack_vi, stack_masks, decline_data, coeff_model, tile)

        write_tif(confidence_index, forest_mask.attrs,nodata = 0, path = tile.paths["confidence_index"])
        write_tif(Nb_dates, forest_mask.attrs,nodata = 0, path = tile.paths["Nb_dates"])
    
    confidence_class = vectorizing_confidence_class(confidence_index, Nb_dates, relevant_area, [threshold_index], np.array(["Stress/scolyte vert","scolyte rouge"]), tile.raster_meta["attrs"])
    confidence_class.to_file(tile.paths["confidence_class"])
    tile.save_info()
    print("Temps d execution : %s secondes ---" % (time.time() - start_time))
    
classify_declining_area("D:/Documents/Deperissement/Output/ZoneEtude",0.3)