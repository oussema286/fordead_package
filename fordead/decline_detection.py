# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:34:34 2020

@author: admin
"""

import datetime
from fordead.ModelVegetationIndex import compute_HarmonicTerms
import xarray as xr

def prediction_vegetation_index(coeff_model,date):
    """
    A partir des données du modèle et de la date, prédit l'indice de végétation
    """
    
    date_as_number=(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
    
    harmonic_terms = compute_HarmonicTerms(date_as_number)
    harmonic_terms = xr.DataArray(harmonic_terms, coords={"band" : [1,2,3,4,5]},dims=["band"])
    
    predicted_vi = sum(coeff_model * harmonic_terms)
    return predicted_vi


def detection_anomalies(masked_vi, predicted_vi, threshold_anomaly):
    """
    Détecte les anomalies par comparaison entre l'indice de végétation réel et l'indice prédit.

    """
    
    diff_vi = masked_vi["vegetation_index"].where(~masked_vi["mask"])-predicted_vi.where(~masked_vi["mask"])
    anomalies = diff_vi.where(~masked_vi["mask"]) > threshold_anomaly
        
    return anomalies

def detection_decline(decline_data, anomalies, mask, date_index):
   
    decline_data["count"] = xr.where(~mask & (anomalies!=decline_data["state"]),decline_data["count"]+1,decline_data["count"])
    decline_data["count"] = xr.where(~mask & (anomalies==decline_data["state"]),0,decline_data["count"])
    
    # print(decline_data["count"].where(~mask & (decline_data["count"]==3),drop=True).shape)
    # print(decline_data["count"].where(decline_data["count"]==3,drop=True).shape)
    
    decline_data["state"] = xr.where(~mask & (decline_data["count"]==3), ~decline_data["state"], decline_data["state"]) #Changement d'état si CompteurScolyte = 3 et date valide
    
    # print(decline_data["state"].where(decline_data["state"],drop=True).shape)
    
    decline_data["count"] = xr.where(decline_data["count"]==3, 0,decline_data["count"])
    decline_data["first_date"]=xr.where(~mask & decline_data["count"]==1 & ~decline_data["state"], date_index,decline_data["first_date"]) #Garde la première date de détection de scolyte sauf si déjà détécté comme scolyte
   

    return decline_data

# def detection_anomalies(masked_vi, predicted_vi, threshold_anomaly):
#     """
#     Détecte les anomalies par comparaison entre l'indice de végétation réel et l'indice prédit.

#     """
        
#     diff_vi = masked_vi["vegetation_index"]-predicted_vi
#     Anomalies = diff_vi > threshold_anomaly
    
#     # Anomalies.where(~(rasterSigma==0),False)#Retire les zones invalides (sans modèle)
    
#     return anomalies