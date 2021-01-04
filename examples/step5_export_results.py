# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:32:57 2020

@author: Raphaël Dutrieux
"""



import argparse
from fordead.ImportData import import_decline_data, TileInfo, import_forest_mask
# from fordead.writing_data import write_tif
# from fordead.decline_detection import detection_anomalies, prediction_vegetation_index, detection_decline
# import time
import numpy as np
import datetime
import xarray as xr
import pandas as pd
import rasterio
from affine import Affine
import fiona
import geopandas as gp


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection/ZoneTest", help = "Dossier avec les données")
    parser.add_argument("--start_date", dest = "start_date",type = str,default = '2015-06-23', help = "Date de début pour l'export des résultats")
    parser.add_argument("--end_date", dest = "end_date",type = str,default = "2021-01-04", help = "Date de fin pour l'export des résultats")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def export_results(
    data_directory,
    start_date,
    end_date
    # ExportAsShapefile = False,
    ):

    #global results / several files
    #Frequency
    #Résultats entre la fin du mois de start date et le début du mois de end_date (rajouter des bins ?)
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    
    # tile.add_parameters({"threshold_anomaly" : threshold_anomaly})
    # if tile.parameters["Overwrite"] : tile.delete_dirs("AnomaliesDir","state_decline") #Deleting previous detection results if they exist
    # tile.add_path("state_decline", tile.data_directory / "DataDecline" / "state_decline.tif")
    
    decline_data = import_decline_data(tile.paths)
    
    
    array = xr.DataArray(range(tile.dates.size), coords={"Time" : tile.dates},dims=["Time"])   
    # array = array.assign_coords(year_month = ("Time",[str(day)[:7] for day in tile.dates]))
    # .strftime('%Y-%m')
    first_dateindex_flat = array[decline_data.first_date.data.ravel()]
    first_datenumber_flat = (pd.to_datetime(first_dateindex_flat.Time.data)-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
    first_date_number = np.reshape(np.array(first_datenumber_flat),decline_data.first_date.shape)
    
    bins_as_date=pd.date_range(start=start_date, end = end_date, freq="M")
    bins_as_datenumber = (bins_as_date-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days    
    inds = np.digitize(first_date_number, bins_as_datenumber,right = True)
    
    forest_mask = import_forest_mask(tile.paths["ForestMask"])
    valid_area = import_forest_mask(tile.paths["valid_area_mask"])
    
    geoms_month_index = list(
                {'properties': {'month_index': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    rasterio.features.shapes(inds.astype("uint16"), mask = (forest_mask & valid_area & decline_data.state & inds!= 0).data, transform=Affine(*decline_data.state.attrs["transform"]))))
  
    gp_results = gp.GeoDataFrame.from_features(geoms_month_index)
    # [str(bin_end)[:7] for bin_end in bins_as_date[gpd_results.month_index.astype(int)]]
    gp_results.insert(1,"month",bins_as_date[gp_results.month_index.astype(int)].month)
    gp_results.insert(1,"year",bins_as_date[gp_results.month_index.astype(int)].year)
        
    tile.add_path("monthly_results", tile.data_directory / "Results" / "monthly_results.shp")
    gp_results.crs = decline_data.state.crs.replace("+init=","")
    gp_results.to_file(tile.paths["monthly_results"])
    
    # SchemaAtteint= {'properties': {'month_index': 'int:18'},'geometry': 'Polygon'}
    # with fiona.open(tile.paths["monthly_results"], "w",crs=decline_data.state.crs,driver='ESRI Shapefile', schema=SchemaAtteint) as output:
    #     for poly in geoms_month_index:
    #         print(poly)
    #         output.write(poly)


    # for dateIndex in range(FirstDateDiff,stackAtteint.shape[0]):
    # #SCOLYTES
    #     if not(os.path.isfile(os.getcwd()+"/Out/Results/"+"V"+Version+"/Atteint/"+tuile+"/Atteint_"+Dates[dateIndex]+".tif")):
    #         writingMode="w"
    #     else:
    #         writingMode="r+"
    #     write_window=rasterio.windows.Window.from_slices((Bornes[x], Bornes[x+1]), (Bornes[y], Bornes[y+1]))
    #     ProfileSave=MetaProfile.copy()
    #     ProfileSave["dtype"]=stackAtteint.dtype
    #     ProfileSave["tiled"]=True
    #     ProfileSave["nodata"]=5
    #     with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Atteint/"+tuile+"/Atteint_"+Dates[dateIndex]+".tif", writingMode, nbits=3, **ProfileSave) as dst:
    #         dst.write(stackAtteint[dateIndex,:,:], indexes=1, window=write_window)

    
    # np.reshape(decline_data.first_date,-1)
    # all_dates_as_number = np.array(range(dates_as_number[0],dates_as_number[-1]+32))
    # all_dates = [np.datetime64(datetime.datetime.strptime("2015-06-23", '%Y-%m-%d').date()+ datetime.timedelta(days=int(day)))  for day in all_dates_as_number]
    # array = xr.DataArray(all_dates_as_number, coords={"Time" : all_dates},dims=["Time"])   
    # array = array.assign_coords(year_month = ("Time",[str(day)[:7] for day in all_dates]))

    # bins = array.groupby("year_month").min()
    # bins = [0, 25, 50,100]
    # decline_data.first_date.groupby_bins(bins = bins)
    # array = array.assign_coords(year = ("Time",pd.DatetimeIndex(array.Time.data).year))
    # array = array.assign_coords(month = ("Time",pd.DatetimeIndex(array.Time.data).month))
    
    # all_dates[0].year
    
    # stack_vi["DateNumber"] = ("Time", np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in tile.dates]))
    # tile.dates
        
                               
    # write_tif(decline_data["count"], first_detection_date_index.attrs,tile.paths["count_decline"],nodata=0)

        # print("Détection du déperissement")
    tile.save_info()



if __name__ == '__main__':
    dictArgs=parse_command_line()
    export_results(**dictArgs)
