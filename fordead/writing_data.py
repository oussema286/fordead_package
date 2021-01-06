# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 17:32:26 2020

@author: admin
"""
import rioxarray
from numpy import uint8
import pandas as pd
import datetime

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
    return bins_as_date, bins_as_datenumber