# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:34:34 2020

@author: Raphael Dutrieux
"""

from fordead.masking_vi import get_dict_vi
import xarray as xr

def detection_anomalies(vegetation_index, predicted_vi, threshold_anomaly, vi, path_dict_vi = None):
    """
    Detects anomalies by comparison between predicted and calculated vegetation index. The array returns contains True where the difference between the vegetation index and its prediction is above the threshold in the direction of the specified dieback change direction of the vegetation index. 

    Parameters
    ----------
    vegetation_index : xarray DataArray
        Array containing the vegetation index values computed from satellite data
    predicted_vi : array (x,y)
        Array containing the vegetation index predicted by the model
    threshold_anomaly : float
        Threshold used to compare predicted and calculated vegetation index.
    vi : str
        Name of the used vegetation index
    path_dict_vi : str, optional
        Path to a text file containing vegetation indices information, where is indicated whether the index rises of falls in case of forest dieback. See get_dict_vi documentation. The default is None.


    Returns
    -------
    anomalies : array (x,y) (bool)
        Array, pixel value is True if an anomaly is detected.

    """

    dict_vi = get_dict_vi(path_dict_vi)
    
    diff_vi = vegetation_index-predicted_vi
    
    if dict_vi[vi]["dieback_change_direction"] == "+":
        anomalies = diff_vi > threshold_anomaly
    elif dict_vi[vi]["dieback_change_direction"] == "-":
        anomalies = diff_vi < (-1*threshold_anomaly)
    else:
        raise Exception("Unrecognized dieback_change_direction in " + path_dict_vi + " for vegetation index " + vi)
            
    return anomalies



def detection_dieback_validation(dieback_data, anomalies, mask, date_index, raster_binary_validation_data):
   
    dieback_data["count"] = xr.where(~mask & (anomalies!=dieback_data["state"]),dieback_data["count"]+1,dieback_data["count"])
    dieback_data["count"] = xr.where(~mask & (anomalies==dieback_data["state"]),0,dieback_data["count"])
    
    changing_pixels = ~mask & (dieback_data["count"]==3)
    dieback_data["state"] = xr.where(changing_pixels, ~dieback_data["state"], dieback_data["state"]) #Changement d'état si CompteurScolyte = 3 et date valide
    dieback_data["first_date"] = xr.where(changing_pixels, dieback_data["first_date_unconfirmed"], dieback_data["first_date"]) #First_date saved if confirmed
    dates_changes_validation = dieback_data["first_date"].where(changing_pixels).data[raster_binary_validation_data]

    dieback_data["count"] = xr.where(changing_pixels, 0,dieback_data["count"])
    dieback_data["first_date_unconfirmed"]=xr.where(~mask & (dieback_data["count"]==1), date_index, dieback_data["first_date_unconfirmed"]) #Garde la première date de détection de scolyte sauf si déjà détécté comme scolyte
   
    return dieback_data, dates_changes_validation


def detection_dieback(dieback_data, anomalies, mask, date_index):
    """
    Updates dieback data using anomalies. Successive anomalies are counted for pixels considered healthy, and successive dates without anomalies are counted for pixels considered suffering from dieback. The state of the pixel changes when the count reaches 3.
    
    Parameters
    ----------
    dieback_data : Dataset with three arrays : 
        "count" which is the number of successive anomalies, 
        "state" which is True where pixels are detected as suffering from dieback, False where they are considered healthy.
        "first date" which contains the index of the date of the first anomaly.
    anomalies : array (x,y) (bool)
        Array, pixel value is True if an anomaly is detected.
    mask : array (x,y) (bool)
        Array, True where pixels are masked
    date_index : int
        Index of the date

    Returns
    -------
    dieback_data : Dataset
        Dataset with the three arrays updated with the results from the date being analysed

    """
   
    dieback_data["count"] = xr.where(~mask & (anomalies!=dieback_data["state"]),dieback_data["count"]+1,dieback_data["count"])
    dieback_data["count"] = xr.where(~mask & (anomalies==dieback_data["state"]),0,dieback_data["count"])
    
    dieback_data["state"] = xr.where(~mask & (dieback_data["count"]==3), ~dieback_data["state"], dieback_data["state"]) #Changement d'état si CompteurScolyte = 3 et date valide
        
    dieback_data["count"] = xr.where(dieback_data["count"]==3, 0,dieback_data["count"])
    dieback_data["first_date"]=xr.where(~mask & (dieback_data["count"]==1) & (~dieback_data["state"]), date_index, dieback_data["first_date"]) #Garde la première date de détection de scolyte sauf si déjà détécté comme scolyte

    return dieback_data


