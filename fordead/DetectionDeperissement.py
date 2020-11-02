# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:34:34 2020

@author: admin
"""

import datetime
import numpy as np
import math

def PredictVegetationIndex(StackP,date):
    """
    A partir des données du modèle et de la date, prédit l'indice de végétation
    """
    
    NewDay=(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
    PredictedVegetationIndex = StackP[0,:,:] + StackP[1,:,:]*np.sin(2*math.pi*NewDay/365.25) + StackP[2,:,:]*np.cos(2*math.pi*NewDay/365.25) + StackP[3,:,:]*np.sin(2*2*math.pi*NewDay/365.25)+StackP[4,:,:]*np.cos(2*2*math.pi*NewDay/365.25)
    return PredictedVegetationIndex


def DetectAnomalies(VegetationIndex, PredictedVegetationIndex, rasterSigma, CoeffAnomalie):
    """
    Détecte les anomalies par comparaison entre l'indice de végétation réel et l'indice prédit.

    """
    
    DiffVegetationIndex = VegetationIndex-PredictedVegetationIndex
    Anomalies = DiffVegetationIndex > CoeffAnomalie*rasterSigma
    
    Anomalies[rasterSigma==0]=False #Retire les zones invalides (sans modèle)

    return Anomalies