# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:32:57 2020

@author: Raphaël Dutrieux
"""



import argparse
from fordead.ImportData import import_decline_data, TileInfo, import_forest_mask, import_soil_data
# from fordead.writing_data import write_tif
# from fordead.decline_detection import detection_anomalies, prediction_vegetation_index, detection_decline
from fordead.writing_data import get_bins, convert_dateindex_to_datenumber, get_periodic_results_as_shapefile, get_state_at_date

# import numpy as np
# import datetime
# import xarray as xr
# import pandas as pd
# import rasterio
# from affine import Affine
# import fiona
# import geopandas as gp


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection/ZoneTest", help = "Dossier avec les données")
    parser.add_argument("--start_date", dest = "start_date",type = str,default = '2015-06-23', help = "Date de début pour l'export des résultats")
    parser.add_argument("--end_date", dest = "end_date",type = str,default = "2022-01-01", help = "Date de fin pour l'export des résultats")
    parser.add_argument("--frequency", dest = "frequency",type = str,default = 'M', help = "Frequency used to aggregate results, if value is 'sentinel', then periods correspond to the period between sentinel dates used in the detection, or it can be the frequency as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)")
    parser.add_argument("--export_soil", dest = "export_soil", action="store_true",default = False, help = "If activated, results relating to soil detection are exported. Results of soil detection have to be computed and written in previous steps")
    parser.add_argument("--multiple_files", dest = "multiple_files", action="store_true",default = False, help = "If activated, one shapefile is exported for each period containing the areas in decline at the end of the period. Else, a single shapefile is exported containing declined areas associated with the period of decline")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs





#     return gp_results
def export_results(
    data_directory,
    start_date,
    end_date,
    frequency,
    export_soil,
    multiple_files
    # ExportAsShapefile = False,
    ):

    tile = TileInfo(data_directory)
    tile = tile.import_info()
    decline_data = import_decline_data(tile.paths)
    tile.add_parameters({"start_date" : start_date,"end_date" : end_date, "frequency" : frequency, "export_soil" : export_soil, "multiple_files" : multiple_files})
    if tile.parameters["Overwrite"] : tile.delete_dirs("periodic_results_decline","result_files") #Deleting previous detection results if they exist
    
    bins_as_date, bins_as_datenumber = get_bins(start_date,end_date,frequency,tile.dates)
    first_date_number = convert_dateindex_to_datenumber(decline_data, tile.dates)
    if export_soil:
        soil_data = import_soil_data(tile.paths)
        first_date_number_soil = convert_dateindex_to_datenumber(soil_data, tile.dates)
        
    forest_mask = import_forest_mask(tile.paths["ForestMask"])
    valid_area = import_forest_mask(tile.paths["valid_area_mask"])
    relevant_area = forest_mask & valid_area
        
    if multiple_files:
        tile.add_dirpath("result_files", tile.data_directory / "Results")
        for date_bin_index, date_bin in enumerate(bins_as_date):
            state_code = first_date_number <= bins_as_datenumber[date_bin_index]
            if export_soil:
                state_code = state_code + 2*(first_date_number_soil <= bins_as_datenumber[date_bin_index])
            period_end_results = get_state_at_date(state_code,relevant_area,decline_data.state.attrs)
            if not(period_end_results.empty):
                period_end_results.to_file(tile.paths["result_files"] / (date_bin.strftime('%Y-%m-%d')+".shp"))
                
    else:
        # vectorize_periodic_results(inds_decline, mask,transform)
        tile.add_path("periodic_results_decline", tile.data_directory / "Results" / "periodic_results_decline.shp")
        periodic_results = get_periodic_results_as_shapefile(first_date_number, bins_as_date, bins_as_datenumber, relevant_area, decline_data.state.attrs)
        periodic_results.to_file(tile.paths["periodic_results_decline"])
        
        if export_soil:
            tile.add_path("periodic_results_soil", tile.data_directory / "Results" / "periodic_results_soil.shp")
            periodic_results = get_periodic_results_as_shapefile(first_date_number_soil, bins_as_date, bins_as_datenumber, relevant_area, soil_data.state.attrs)
            periodic_results.to_file(tile.paths["periodic_results_soil"])
    
    tile.save_info()



if __name__ == '__main__':
    dictArgs=parse_command_line()
    export_results(**dictArgs)
