# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:34:34 2020

@author: Raphael Dutrieux
"""

import datetime
from fordead.ModelVegetationIndex import compute_HarmonicTerms
from fordead.masking_vi import get_dict_vi
import xarray as xr

import numpy as np

def prediction_vegetation_index(coeff_model,date_list):
    """
    Predicts the vegetation index from the model coefficients and the date
    
    Parameters
    ----------
    coeff_model : array (5,x,y)
        Array containing the five coefficients of the vegetation index model for each pixel
    date : str
        Date in the format "YYYY-MM-DD"

    Returns
    -------
    predicted_vi : array (x,y)
        Array containing predicted vegetation index from the model

    """
        
    date_as_number_list=[(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in date_list]
    harmonic_terms = np.array([compute_HarmonicTerms(DateAsNumber) for DateAsNumber in date_as_number_list])
    harmonic_terms = xr.DataArray(harmonic_terms, coords={"Time" : date_list, "coeff" : range(1, 6)},dims=["Time", "coeff"])
    
    predicted_vi = sum(coeff_model * harmonic_terms)
    return predicted_vi



def detection_anomalies(vegetation_index, predicted_vi, threshold_anomaly, vi, path_dict_vi = None):
    """
    Detects anomalies by comparison between predicted and calculated vegetation index. The array returns contains True where the difference between the vegetation index and its prediction is above the threshold in the direction of the specified decline change direction of the vegetation index. 

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
        Path to a text file containing vegetation indices information, where is indicated whether the index rises of falls in case of forest decline. See get_dict_vi documentation. The default is None.


    Returns
    -------
    anomalies : array (x,y) (bool)
        Array, pixel value is True if an anomaly is detected.

    """

    dict_vi = get_dict_vi(path_dict_vi)
    
    diff_vi = vegetation_index-predicted_vi
    
    if dict_vi[vi]["decline_change_direction"] == "+":
        anomalies = diff_vi > threshold_anomaly
    elif dict_vi[vi]["decline_change_direction"] == "-":
        anomalies = diff_vi < (-1*threshold_anomaly)
    else:
        raise Exception("Unrecognized decline_change_direction in " + path_dict_vi + " for vegetation index " + vi)
            
    return anomalies

def detection_decline(decline_data, anomalies, mask, date_index):
    """
    Updates decline data using anomalies. Successive anomalies are counted for pixels considered healthy, and successive dates without anomalies are counted for pixels considered declining. The state of the pixel changes when the count reaches 3.
    
    Parameters
    ----------
    decline_data : Dataset with four arrays : 
        "count" which is the number of successive anomalies, 
        "state" which is True where pixels are detected as declining, False where they are considered healthy.
        "first date" which contains the index of the date of the first anomaly, when confirmed by 3 successive anomalies.
        "first date_unconfirmed" which contains the index of the date of the first anomaly, even if not yet confirmed by 3 successive anomalies.
    anomalies : array (x,y) (bool)
        Array, pixel value is True if an anomaly is detected.
    mask : array (x,y) (bool)
        Array, True where pixels are masked
    date_index : int
        Index of the date

    Returns
    -------
    decline_data : Dataset
        Dataset with the four arrays updated with the results from the date being analysed

    """
   
    decline_data["count"] = xr.where(~mask & (anomalies!=decline_data["state"]),decline_data["count"]+1,decline_data["count"])
    decline_data["count"] = xr.where(~mask & (anomalies==decline_data["state"]),0,decline_data["count"])
    
    changing_pixels = ~mask & (decline_data["count"]==3)
    decline_data["state"] = xr.where(changing_pixels, ~decline_data["state"], decline_data["state"]) #Changement d'état si CompteurScolyte = 3 et date valide
    decline_data["first_date"] = xr.where(changing_pixels, decline_data["first_date_unconfirmed"], decline_data["first_date"]) #First_date saved if confirmed

    decline_data["count"] = xr.where(changing_pixels, 0,decline_data["count"])
    decline_data["first_date_unconfirmed"]=xr.where(~mask & (decline_data["count"]==1) & ~decline_data["state"], date_index, decline_data["first_date_unconfirmed"]) #Garde la première date de détection de scolyte sauf si déjà détécté comme scolyte

    
    return decline_data

