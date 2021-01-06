# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:32:57 2020

@author: Raphaël Dutrieux
"""



import argparse
from fordead.ImportData import import_decline_data, TileInfo, import_forest_mask, import_soil_data
# from fordead.writing_data import write_tif
# from fordead.decline_detection import detection_anomalies, prediction_vegetation_index, detection_decline
from fordead.writing_data import get_bins

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
    parser.add_argument("--frequency", dest = "frequency",type = str,default = 'M', help = "Frequency used to aggregate results, as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)")
    parser.add_argument("--export_soil", dest = "export_soil", action="store_true",default = True, help = "If activated, results relating to soil detection are exported. Results of soil detection have to be computed and written in previous steps")
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
    
    # tile.add_parameters({"threshold_anomaly" : threshold_anomaly})
    # if tile.parameters["Overwrite"] : tile.delete_dirs("AnomaliesDir","state_decline") #Deleting previous detection results if they exist
    # tile.add_path("state_decline", tile.data_directory / "DataDecline" / "state_decline.tif")


    
    bins_as_date, bins_as_datenumber = get_bins(start_date,end_date,frequency,tile.dates)

    decline_data = import_decline_data(tile.paths)
    
    array = xr.DataArray(range(tile.dates.size), coords={"Time" : tile.dates},dims=["Time"])   
    first_dateindex_flat = array[decline_data.first_date.data.ravel()]
    first_datenumber_flat = (pd.to_datetime(first_dateindex_flat.Time.data)-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
    first_date_number = np.reshape(np.array(first_datenumber_flat),decline_data.first_date.shape)
    inds_decline = np.digitize(first_date_number, bins_as_datenumber,right = True)
    
    forest_mask = import_forest_mask(tile.paths["ForestMask"])
    valid_area = import_forest_mask(tile.paths["valid_area_mask"])
    relevant_area = np.logical_and(np.logical_and((forest_mask & valid_area  & decline_data.state).data,inds_decline!=0),inds_decline!=len(bins_as_date)) #Areas in the forest mask, valid area, in decline within start date and end date
    
    # bins_as_date[np.logical_and(bins_as_datenumber >= np.min(first_date_number[relevant_area]),bins_as_datenumber <= np.max(first_date_number[relevant_area]))]
    
    
    if export_soil:
        soil_data = import_soil_data(tile.paths)
        first_dateindex_flat_soil = array[soil_data.first_date.data.ravel()]
        first_datenumber_flat_soil = (pd.to_datetime(first_dateindex_flat_soil.Time.data)-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
        first_date_number_soil = np.reshape(np.array(first_datenumber_flat_soil),soil_data.first_date.shape)
        inds_soil = np.digitize(first_date_number_soil, bins_as_datenumber, right = True)
        
        
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
                            rasterio.features.shapes(state_code.astype("uint8"), mask =  relevant_area & (state_code!=0), transform=Affine(*decline_data.state.attrs["transform"]))))
            gp_results = gp.GeoDataFrame.from_features(geoms_declined)
            
            gp_results.crs = decline_data.state.crs.replace("+init=","")
            if not(gp_results.empty):
                gp_results.to_file(tile.paths["result_files"] / (date_bin.strftime('%Y-%m-%d')+".shp"))
                
            
    else:
        geoms_period_index = list(
                    {'properties': {'period_index': v}, 'geometry': s}
                    for i, (s, v) 
                    in enumerate(
                        rasterio.features.shapes(inds_decline.astype("uint16"), mask =  relevant_area , transform=Affine(*decline_data.state.attrs["transform"]))))
      
        gp_results = gp.GeoDataFrame.from_features(geoms_period_index)
        gp_results.period_index=gp_results.period_index.astype(int)

        gp_results.insert(1,"period",(bins_as_date[gp_results.period_index-1] + pd.DateOffset(1)).strftime('%Y-%m-%d') + " - " + (bins_as_date[gp_results.period_index]).strftime('%Y-%m-%d'))
        # gp_results.insert(1,"month",bins_as_date[gp_results.period_index.astype(int)].month)
        # gp_results.insert(1,"year",bins_as_date[gp_results.month_index.astype(int)].year)
        
        
        tile.add_path("periodic_results_decline", tile.data_directory / "Results" / "periodic_results_decline.shp")
        gp_results.crs = decline_data.state.crs.replace("+init=","")
        gp_results.to_file(tile.paths["periodic_results_decline"])
        
        if export_soil:
            geoms_period_index = list(
                        {'properties': {'period_index': v}, 'geometry': s}
                        for i, (s, v) 
                        in enumerate(
                            rasterio.features.shapes(inds_soil.astype("uint16"), mask =  relevant_area , transform=Affine(*decline_data.state.attrs["transform"]))))
          
            gp_results = gp.GeoDataFrame.from_features(geoms_period_index)
            gp_results.period_index=gp_results.period_index.astype(int)
    
            gp_results.insert(1,"period",(bins_as_date[gp_results.period_index-1] + pd.DateOffset(1)).strftime('%Y-%m-%d') + " - " + (bins_as_date[gp_results.period_index]).strftime('%Y-%m-%d'))
            # gp_results.insert(1,"month",bins_as_date[gp_results.period_index.astype(int)].month)
            # gp_results.insert(1,"year",bins_as_date[gp_results.month_index.astype(int)].year)
            
            
            tile.add_path("periodic_results_soil", tile.data_directory / "Results" / "periodic_results_soil.shp")
            gp_results.crs = decline_data.state.crs.replace("+init=","")
            gp_results.to_file(tile.paths["periodic_results_soil"])
    
    tile.save_info()



if __name__ == '__main__':
    dictArgs=parse_command_line()
    export_results(**dictArgs)
