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

def convert_dateindex_to_datenumber(dates_index, dates):
    array = xr.DataArray(range(dates.size), coords={"Time" : dates},dims=["Time"])   
    dateindex_flat = array[dates_index.data.ravel()]
    datenumber_flat = (pd.to_datetime(dateindex_flat.Time.data)-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
    date_number = np.reshape(np.array(datenumber_flat),dates_index.shape)
    return date_number