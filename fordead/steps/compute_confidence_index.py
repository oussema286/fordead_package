# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 16:40:16 2021

@author: Raphael Dutrieux
"""

from fordead.ImportData import import_masked_vi, import_decline_data, TileInfo, import_forest_mask, import_soil_data, import_confidence_data, import_coeff_model, initialize_confidence_data
from fordead.writing_data import write_tif, vectorizing_confidence_class
from fordead.masking_vi import get_dict_vi
from fordead.ModelVegetationIndex import correct_vi_date, prediction_vegetation_index

import numpy as np
import click

@click.command(name='ind_conf')
@click.option("-o", "--data_directory", type = str, help = "Path of the output directory")
@click.option("--threshold", type = float, default = 0.265, help = "Threshold used to classify declining stages", show_default=True)
@click.option("--chunks", type = int, default = None, help = "Chunk size for dask computation", show_default=True)
def cli_classify_declining_area(
    data_directory,
    threshold,
    chunks = None
    ):
    classify_declining_area(data_directory,threshold,chunks)

def classify_declining_area(
    data_directory,
    threshold_confidence_index,
    chunks = None
    ):
    # print("Computing confidence index")
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"threshold_confidence_index" : threshold_confidence_index})
  
    tile.add_path("confidence_index", tile.data_directory / "Confidence_Index" / "confidence_index.tif")
    tile.add_path("confidence_class", tile.data_directory / "Confidence_Index" / "confidence_class.shp")
    tile.add_path("nb_dates", tile.data_directory / "Confidence_Index" / "nb_dates.tif")
    
    forest_mask = import_forest_mask(tile.paths["ForestMask"], chunks = chunks)
    valid_area = import_forest_mask(tile.paths["valid_area_mask"], chunks = chunks)
    soil_data = import_soil_data(tile.paths, chunks = chunks)
    decline_data = import_decline_data(tile.paths, chunks = chunks)

    relevant_area = (forest_mask & valid_area & decline_data["state"] & ~soil_data["state"]).compute()
    dict_vi = get_dict_vi(tile.parameters["path_dict_vi"])
    nb_dates, sum_diff = initialize_confidence_data(forest_mask.shape,forest_mask.coords)

    coeff_model = import_coeff_model(tile.paths["coeff_model"], chunks = chunks)
    
    first_date = decline_data["first_date"].where(relevant_area).min().compute()
    # Importing = (tile.dates[-1] == tile.last_date_confidence_index) if hasattr(tile, "last_date_confidence_index") else False
    Importing = False
    if  Importing:
        print("Importing confidence index")
        confidence_index, nb_dates = import_confidence_data(tile.paths)
    else:
        print("Computing confidence index")
        for date_index, date in enumerate(tile.dates):
            if date_index >= first_date:
                masked_vi = import_masked_vi(tile.paths,date,chunks = chunks)
                if tile.parameters["correct_vi"]:
                    masked_vi["vegetation_index"], tile.correction_vi = correct_vi_date(masked_vi,forest_mask, tile.large_scale_model, date, tile.correction_vi)
                predicted_vi=prediction_vegetation_index(coeff_model,[date])
                
                if dict_vi[tile.parameters["vi"]]["decline_change_direction"] == "+":
                    diff = (masked_vi["vegetation_index"] - predicted_vi).squeeze("Time").compute()
                elif dict_vi[tile.parameters["vi"]]["decline_change_direction"] == "-":
                    diff = (predicted_vi - masked_vi["vegetation_index"]).squeeze("Time").compute()
                
                
                declining_pixels = ((decline_data["first_date"] <= date_index) & ~masked_vi["mask"]).compute()
                print(date_index)
                print(decline_data["first_date"].sel(x = 721093, y = 5447298,method = "nearest"))
                print(declining_pixels.sel(x = 721093, y = 5447298,method = "nearest"))
                print(~masked_vi["mask"].sel(x = 721093, y = 5447298,method = "nearest"))

                nb_dates = nb_dates + declining_pixels
                sum_diff = sum_diff + diff*declining_pixels*nb_dates #Try compare with where
                del masked_vi, predicted_vi, diff, declining_pixels
                print('\r', date, " | ", len(tile.dates)-date_index-1, " remaining       ", sep='', end='', flush=True) if date_index != (len(tile.dates) -1) else print('\r', '                                              ', '\r', sep='', end='', flush=True)

            
        confidence_index = sum_diff/(nb_dates*(nb_dates+1)/2)
        tile.last_date_confidence_index = date
        write_tif(confidence_index, forest_mask.attrs,nodata = 0, path = tile.paths["confidence_index"])
        write_tif(nb_dates, forest_mask.attrs,nodata = 0, path = tile.paths["nb_dates"])
    
    confidence_class = vectorizing_confidence_class(confidence_index, nb_dates, relevant_area, [threshold_confidence_index], np.array(["Stress/scolyte vert","scolyte rouge"]), tile.raster_meta["attrs"])
    confidence_class.to_file(tile.paths["confidence_class"])
    tile.save_info()
    
if __name__ == '__main__':
    cli_classify_declining_area()
