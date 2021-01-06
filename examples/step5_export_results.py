# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:32:57 2020

@author: Raphaël Dutrieux
"""



import argparse
from fordead.ImportData import import_decline_data, TileInfo, import_forest_mask, import_soil_data
# from fordead.writing_data import write_tif
# from fordead.decline_detection import detection_anomalies, prediction_vegetation_index, detection_decline
from fordead.writing_data import get_bins, convert_dateindex_to_datenumber

import numpy as np
import datetime
import xarray as xr
import pandas as pd
import rasterio
from affine import Affine
# import fiona
import geopandas as gp


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


def export_results(
    data_directory,
    start_date,
    end_date,
    frequency,
    export_soil,
    multiple_files
    # ExportAsShapefile = False,
    ):

    #global results / several files
    #Frequency (date sentinel / mois / plusieurs mois)
    #Résultats entre la fin du mois de start date et le début du mois de end_date (rajouter des bins ?)
    #Cut / not cut
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    decline_data = import_decline_data(tile.paths)
    tile.add_parameters({"start_date" : start_date,"end_date" : end_date, "frequency" : frequency, "export_soil" : export_soil, "multiple_files" : multiple_files})
    if tile.parameters["Overwrite"] : tile.delete_dirs("periodic_results_decline","result_files") #Deleting previous detection results if they exist
    
    bins_as_date, bins_as_datenumber = get_bins(start_date,end_date,frequency,tile.dates)

    first_date_number = convert_dateindex_to_datenumber(decline_data.first_date, tile.dates)
    first_date_number[~decline_data.state.data] = bins_as_datenumber[-1]+1
    inds_decline = np.digitize(first_date_number, bins_as_datenumber,right = True)
    
    forest_mask = import_forest_mask(tile.paths["ForestMask"])
    valid_area = import_forest_mask(tile.paths["valid_area_mask"])
    relevant_area = forest_mask & valid_area
                
    
    if export_soil:
        soil_data = import_soil_data(tile.paths)
        first_date_number_soil = convert_dateindex_to_datenumber(soil_data.first_date, tile.dates)
        inds_soil = np.digitize(first_date_number_soil, bins_as_datenumber, right = True)
        first_date_number_soil[~soil_data.state.data] = bins_as_datenumber[-1]+1
        
    if multiple_files:
        
        tile.add_dirpath("result_files", tile.data_directory / "Results")
        for date_bin_index, date_bin in enumerate(bins_as_date):
            state_code = first_date_number <= bins_as_datenumber[date_bin_index]
            if export_soil:
                state_code = state_code + 2*(first_date_number_soil <= bins_as_datenumber[date_bin_index])
            geoms_declined = list(
                        {'properties': {'state': v}, 'geometry': s}
                        for i, (s, v) 
                        in enumerate(
                            rasterio.features.shapes(state_code.astype("uint8"), mask =  np.logical_and(relevant_area.data,state_code!=0), transform=Affine(*decline_data.state.attrs["transform"]))))
            gp_results = gp.GeoDataFrame.from_features(geoms_declined)
            gp_results.crs = decline_data.state.crs.replace("+init=","")
            if not(gp_results.empty):
                gp_results.to_file(tile.paths["result_files"] / (date_bin.strftime('%Y-%m-%d')+".shp"))
                
            
    else:
        # vectorize_periodic_results(inds_decline, mask,transform)
        tile.add_path("periodic_results_decline", tile.data_directory / "Results" / "periodic_results_decline.shp")
        
        geoms_period_index = list(
                    {'properties': {'period_index': v}, 'geometry': s}
                    for i, (s, v) 
                    in enumerate(
                        rasterio.features.shapes(inds_decline.astype("uint16"), mask =  (relevant_area & (inds_decline!=0) &  (inds_decline!=len(bins_as_date))).data, transform=Affine(*decline_data.state.attrs["transform"]))))
      
        gp_results = gp.GeoDataFrame.from_features(geoms_period_index)
        gp_results.period_index=gp_results.period_index.astype(int)
        gp_results.insert(1,"period",(bins_as_date[gp_results.period_index-1] + pd.DateOffset(1)).strftime('%Y-%m-%d') + " - " + (bins_as_date[gp_results.period_index]).strftime('%Y-%m-%d'))        
        
        gp_results.crs = decline_data.state.crs.replace("+init=","")
        gp_results.to_file(tile.paths["periodic_results_decline"])
        
        if export_soil:
            tile.add_path("periodic_results_soil", tile.data_directory / "Results" / "periodic_results_soil.shp")
            
            geoms_period_index = list(
                        {'properties': {'period_index': v}, 'geometry': s}
                        for i, (s, v) 
                        in enumerate(
                            rasterio.features.shapes(inds_soil.astype("uint16"), mask =  (relevant_area & (inds_soil!=0) &  (inds_soil!=len(bins_as_date))).data , transform=Affine(*decline_data.state.attrs["transform"]))))
            gp_results = gp.GeoDataFrame.from_features(geoms_period_index)
            gp_results.period_index=gp_results.period_index.astype(int)
            gp_results.insert(1,"period",(bins_as_date[gp_results.period_index-1] + pd.DateOffset(1)).strftime('%Y-%m-%d') + " - " + (bins_as_date[gp_results.period_index]).strftime('%Y-%m-%d'))            
            gp_results.crs = decline_data.state.crs.replace("+init=","")
            gp_results.to_file(tile.paths["periodic_results_soil"])
    
    tile.save_info()



if __name__ == '__main__':
    dictArgs=parse_command_line()
    export_results(**dictArgs)
