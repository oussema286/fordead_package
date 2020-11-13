# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 17:32:26 2020

@author: admin
"""
import rioxarray
from numpy import int8

def write_tif(data_array, attributes, path, nodata = None):
    data_array.attrs=attributes
    
    args={}
    
    if data_array.dtype==bool:
        data_array=data_array.astype(int8)
        args["nbits"] = 1
    if nodata != None:
        data_array.attrs["nodata"]=nodata
        
    if len(data_array.dims)==3:
        data_array=data_array.transpose(data_array.dims[2], 'y', 'x')
        data_array.attrs["scales"]=data_array.attrs["scales"]*data_array.shape[0]
        data_array.attrs["offsets"]=data_array.attrs["offsets"]*data_array.shape[0]

    data_array.rio.to_raster(path, **args)

