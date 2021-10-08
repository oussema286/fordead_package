# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 17:32:26 2020

@author: Raphael Dutrieux
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
import dask.array as da
from fordead.model_vegetation_index import prediction_vegetation_index
from fordead.masking_vi import get_dict_vi
from scipy import ndimage


def write_tif(data_array, attributes, path, nodata = None):
    """
    Writes raster to the disk

    Parameters
    ----------
    data_array : xarray DataArray
        Object to be written
    attributes : dict
        Dictionnary containing attributes used to write the data_array ("crs","nodata","scales","offsets")
    path : str
        Path of the file to which data will be written
    nodata : int or float, optional
        Number used as nodata. If None, the nodata attribute of the object will be kept. The default is None.

    Returns
    -------
    None.

    """
    data_array.attrs=attributes
    data_array.attrs["crs"]=data_array.crs.replace("+init=","") #Remove "+init=" which it deprecated

    args={}
    if data_array.dtype==bool: #Bool rasters can't be written, so they have to be converted to int8, but they can still be written in one bit with the argument nbits = 1
        data_array=data_array.astype(uint8)
        args["nbits"] = 1
    if nodata != None:
        data_array.attrs["nodata"]=nodata
        
    if len(data_array.dims)>=3: #If data_array has several bands
        for dim in data_array.dims:
            if dim != "x" and dim != "y":
                data_array=data_array.transpose(dim, 'y', 'x') #dimension which is not x or y must be first
        data_array.attrs["scales"]=data_array.attrs["scales"]*data_array.shape[0]
        data_array.attrs["offsets"]=data_array.attrs["offsets"]*data_array.shape[0]
    
    # data_array.attrs["nodatavals"]=(0,)
    # data_array.attrs["scales"]=(0,)
    # data_array.attrs["offsets"]=(0,)

    data_array.rio.to_raster(path,windowed = False, **args, tiled = True)



def get_bins(start_date,end_date,frequency,dates):
    """
    Creates bins from the start_date (or first used SENTINEL date if it is later than the start date) to the end_date (or last used SENTINEL date if it is earlier than the end_date) with specified frequency

    Parameters
    ----------
    start_date : str
        Date in the format 'YYYY-MM-DD'
    end_date : str
        Date in the format 'YYYY-MM-DD'
    frequency : str
        Frequency as used in pandas.date_range (https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.date_range.html), e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days). It can also be 'sentinel', then bins correspond to the list given as parameter 'dates'
    dates : list
        List of dates used for detection

    Returns
    -------
    bins_as_date : numpy array
        Bins as an array of dates in the format 'YYYY-MM-DD'
    bins_as_datenumber : numpy array
        Bins as an array of integers corresponding to the number of days since "2015-01-01"

    """
    
    if frequency == "sentinel":
        bins_as_date = pd.DatetimeIndex(dates)
    else:
        bins_as_date=pd.date_range(start=start_date, end = end_date, freq=frequency)

    # bins_as_date = bins_as_date.insert(0,datetime.datetime.strptime(start_date, '%Y-%m-%d'))
    # bins_as_date = bins_as_date.insert(len(bins_as_date),datetime.datetime.strptime(end_date, '%Y-%m-%d'))
    bins_as_datenumber = (bins_as_date-datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')).days  
    
    bin_min = max((datetime.datetime.strptime(start_date, '%Y-%m-%d')-datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')).days, (datetime.datetime.strptime(dates[0], '%Y-%m-%d')-datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')).days)
    bin_max = min((datetime.datetime.strptime(end_date, '%Y-%m-%d')-datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')).days, (datetime.datetime.strptime(dates[-1], '%Y-%m-%d')-datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')).days)

    kept_bins = ndimage.binary_dilation(np.logical_and(bins_as_datenumber>=bin_min,bins_as_datenumber<=bin_max),iterations=1,structure=np.array([False,True,True])) #Kept bins are those within bin_min and bin_max plus one bin after bin_max

    bins_as_date = bins_as_date[kept_bins]
    bins_as_datenumber = bins_as_datenumber[kept_bins]
    
    return bins_as_date, bins_as_datenumber

def convert_dateindex_to_datenumber(dataset, dates):
    """
    Converts array containing dates as an index to an array containing dates as the number of days since "2015-01-01" or to a no data value if masked

    Parameters
    ----------
    dataset : xarray dataset with at least arrays : 
        "state", binary array with False where returned array will take a no data value (99999999)
        "first date", array containing index of date in 'dates'
    dates : array
        Array of dates in the format "YYYY-MM-DD"

    Returns
    -------
    results_date_number : xarray DataArray
        DataArray with dates as the number of days since "2015-01-01", or no data value of 99999999

    """
    
    used_dates_numbers = (pd.to_datetime(dates)-datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')).days
    results_date_number = used_dates_numbers[dataset.first_date.data.ravel()]
    results_date_number = np.reshape(np.array(results_date_number),dataset.first_date.shape)
    results_date_number[~dataset.state.data] = 99999999
    
    return results_date_number


def get_periodic_results_as_shapefile(first_date_number, bins_as_date, bins_as_datenumber, relevant_area, attrs):
    """
    Aggregates pixels in array containing dates, based on the period they fall into, then vectorizes results masking dates oustide the bins.

    Parameters
    ----------
    first_date_number : array
        Array containing dates as the number of days since "2015-01-01"
    bins_as_date : array
        Array containing dates used as bins in the format "YYYY-MM-JJ"
    bins_as_datenumber : array
        Array containing dates used as bins, as the number of days since "2015-01-01" 
    relevant_area : array
        Mask where pixels with value False will be ignored.
    attrs : dict
        Dictionnary containing 'tranform' and 'crs' to create the vector.

    Returns
    -------
    period_end_results : geopandas dataframe
        Polygons containing the period during which dates fall.

    """
    
    inds_soil = np.digitize(first_date_number, bins_as_datenumber, right = True)
    # geoms_period_index = list(
    #             {'properties': {'period_index': v}, 'geometry': s}
    #             for i, (s, v) 
    #             in enumerate(
    #                 rasterio.features.shapes(inds_soil.astype("uint16"), mask =  (relevant_area & (inds_soil!=0) &  (inds_soil!=len(bins_as_date))).data , transform=Affine(*attrs["transform"]))))
    geoms_period_index = list(
                {'properties': {'period_index': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    rasterio.features.shapes(inds_soil.astype("uint16"), mask =  (relevant_area & (inds_soil!=0) &  (inds_soil!=len(bins_as_date))).compute().data , transform=Affine(*attrs["transform"]))))
    gp_results = gp.GeoDataFrame.from_features(geoms_period_index)
    gp_results.period_index=gp_results.period_index.astype(int)
    gp_results.insert(0,"period_start",(bins_as_date[gp_results.period_index-1] + pd.DateOffset(1)).strftime('%Y-%m-%d'))
    gp_results.insert(1,"period_end",(bins_as_date[gp_results.period_index]).strftime('%Y-%m-%d'))
    gp_results.insert(0,"period", (gp_results["period_start"] + " - " + gp_results["period_end"]))
    gp_results.crs = attrs["crs"].replace("+init=","")
    gp_results = gp_results.drop(columns=['period_index'])
    return gp_results

def get_state_at_date(state_code,relevant_area,attrs):
    """
    Vectorizes array 'state_code' using 'relevant_area' as mask

    Parameters
    ----------
    state_code : array
        Array to vectorize, in which value 0 is ignored, 1 is 'Anomaly', 2 is "Bare ground" and 3 is 'Bare ground after anomaly'
    relevant_area : array
        Mask where pixels with value False will be ignored.
    attrs : dict
        Dictionnary containing 'tranform' and 'crs' to create the vector.

    Returns
    -------
    period_end_results : geopandas dataframe
        Polygons from vectorization of state_code, aggregated according to value 'Anomaly', "Bare ground" and 'Bare ground after anomaly'

    """
    
    geoms = list(
                {'properties': {'state': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    rasterio.features.shapes(state_code.astype("uint8"), mask =  np.logical_and(relevant_area.data,state_code!=0).compute(), transform=Affine(*attrs["transform"]))))
    period_end_results = gp.GeoDataFrame.from_features(geoms)
    
    period_end_results = period_end_results.replace([1, 2, 3], ["Anomaly","Bare ground","Bare ground after anomaly"])
    
    period_end_results.crs = attrs["crs"].replace("+init=","")
    return period_end_results

def vectorizing_confidence_class(confidence_index, nb_dates, relevant_area, bins_classes, classes, attrs):
    """
    Classifies pixels in the relevant area into dieback classes based on the confidence index and the number of unmasked dates since the first anomaly. 
    
    Parameters
    ----------
    confidence_index : xarray DataArray (x,y) (float)
        Confidence index.
    nb_dates : xarray DataArray (x,y) (int)
        number of unmasked dates since the first anomaly.
    relevant_area : xarray DataArray (x,y) (bool)
        Array with True where pixels will be vectorized, and False where ignored.
    bins_classes : list of float
        List of bins to classify pixels based on confidence_index
    classes : list of str
        List with names of classes (length of classes must be length of bins_classes + 1)
    attrs : dict
        Dictionnary containing 'tranform' and 'crs' to create the vector.

    Returns
    -------
    gp_results : geopandas geodataframe
        Polygons from pixels in the relevant areacontaining the dieback class.

    """
    
    digitized = np.digitize(confidence_index,bins_classes)
    digitized[nb_dates==3]=0
    geoms_class = list(
                {'properties': {'class_index': v}, 'geometry': s}
                for i, (s, v) 
                in enumerate(
                    rasterio.features.shapes(digitized.astype(np.uint8), 
                                             mask = relevant_area.data, 
                                             transform=Affine(*attrs["transform"]))))
    
    gp_results = gp.GeoDataFrame.from_features(geoms_class)
    gp_results.class_index=gp_results.class_index.astype(int)
    gp_results.insert(1,"class",classes[gp_results.class_index])
    gp_results.crs = attrs["crs"].replace("+init=","")
    gp_results = gp_results.drop(columns=['class_index'])
    return gp_results

def union_confidence_class(periodic_results, path_confidence_class):
    confidence_class = gp.read_file(path_confidence_class)
    union = gp.overlay(periodic_results, confidence_class, how='union',keep_geom_type = True)
    # union = union.explode()
    # union = union[union.geom_type != 'Point']
    # union = union[union.geom_type != 'MultiLineString']
    # union = union[union.geom_type != 'LineString']
    # union = union[union.geom_type != 'MultiPoint']
    union = union.fillna("Bare ground")
    return union