# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 17:32:26 2020

@author: admin
"""
import rioxarray
from numpy import uint8
import pandas as pd
import datetime
import numpy as np
import xarray as xr
import rasterio
from affine import Affine
import geopandas as gp

def write_tif(data_array, attributes, path, nodata = None):
    data_array.attrs=attributes
    data_array.attrs["crs"]=data_array.crs.replace("+init=","") #Remove "+init=" which it deprecated

    args={}
    if data_array.dtype==bool: #Bool rasters can't be written, so they have to be converted to int8, but they can still be written in one bit with the argument nbits = 1
        data_array=data_array.astype(uint8)
        args["nbits"] = 1
    if nodata != None:
        data_array.attrs["nodata"]=nodata
        
    if len(data_array.dims)==3: #If data_array has several bands
        for dim in data_array.dims:
            if dim != "x" and dim != "y":
                data_array=data_array.transpose(dim, 'y', 'x') #dimension which is not x or y must be first
        data_array.attrs["scales"]=data_array.attrs["scales"]*data_array.shape[0]
        data_array.attrs["offsets"]=data_array.attrs["offsets"]*data_array.shape[0]

    data_array.rio.to_raster(path,windowed = False, **args, tiled = True)

def get_bins(start_date,end_date,frequency,dates):
    if frequency == "sentinel":
        bins_as_date = pd.DatetimeIndex(dates)
    else:
        bins_as_date=pd.date_range(start=start_date, end = end_date, freq=frequency)
    bins_as_date = bins_as_date.insert(0,datetime.datetime.strptime(start_date, '%Y-%m-%d'))
    bins_as_date = bins_as_date.insert(len(bins_as_date),datetime.datetime.strptime(end_date, '%Y-%m-%d'))
    bins_as_datenumber = (bins_as_date-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days  
    
    bin_min = max((datetime.datetime.strptime(start_date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days, (datetime.datetime.strptime(dates[0], '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days)
    bin_max = min((datetime.datetime.strptime(end_date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days, (datetime.datetime.strptime(dates[-1], '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days)
    
    bins_as_date = bins_as_date[np.logical_and(bins_as_datenumber>=bin_min,bins_as_datenumber<=bin_max)]
    bins_as_datenumber = bins_as_datenumber[np.logical_and(bins_as_datenumber>=bin_min,bins_as_datenumber<=bin_max)]

    return bins_as_date, bins_as_datenumber

def convert_dateindex_to_datenumber(data, dates):

    array = xr.DataArray(range(dates.size), coords={"Time" : dates},dims=["Time"])   
    dateindex_flat = array[data.first_date.data.ravel()]
    datenumber_flat = (pd.to_datetime(dateindex_flat.Time.data)-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
    date_number = np.reshape(np.array(datenumber_flat),data.first_date.shape)
    date_number[~data.state.data] = 99999999
    return date_number


def get_periodic_results_as_shapefile(first_date_number, bins_as_date, bins_as_datenumber, relevant_area, attrs):
    inds_soil = np.digitize(first_date_number, bins_as_datenumber, right = True)
    geoms_period_index = list(
                {'properties': {'period_index': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    rasterio.features.shapes(inds_soil.astype("uint16"), mask =  (relevant_area & (inds_soil!=0) &  (inds_soil!=len(bins_as_date))).data , transform=Affine(*attrs["transform"]))))
    gp_results = gp.GeoDataFrame.from_features(geoms_period_index)
    gp_results.period_index=gp_results.period_index.astype(int)
    gp_results.insert(1,"period",(bins_as_date[gp_results.period_index-1] + pd.DateOffset(1)).strftime('%Y-%m-%d') + " - " + (bins_as_date[gp_results.period_index]).strftime('%Y-%m-%d'))            
    gp_results.crs = attrs["crs"].replace("+init=","")
    return gp_results

def get_state_at_date(state_code,relevant_area,attrs):
    geoms = list(
                {'properties': {'state': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    rasterio.features.shapes(state_code.astype("uint8"), mask =  np.logical_and(relevant_area.data,state_code!=0), transform=Affine(*attrs["transform"]))))
    period_end_results = gp.GeoDataFrame.from_features(geoms)
    period_end_results.crs = attrs["crs"].replace("+init=","")
    return period_end_results