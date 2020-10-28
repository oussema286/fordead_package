# -*- coding: utf-8 -*-
"""
Created on Wed OCt 28 16:30:16 2020

@author: raphael.dutrieux
"""

import os, sys
import numpy as np
import rasterio
import datetime

def readInputDataDateByDate(DataDirectory, Dates,tuile):
    for DateIndex,date in enumerate(Dates):
        with rasterio.open(DataDirectory+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif") as VegetationIndex:
            if DateIndex==0:
                StackVegetationIndex=np.empty((Dates.shape[0],VegetationIndex.profile["width"],VegetationIndex.profile["height"]),dtype=np.float32)
            StackVegetationIndex[DateIndex,:,:]=VegetationIndex.read(1)
        with rasterio.open(DataDirectory+"/Mask/"+tuile+"/Mask_"+date+".tif") as Mask:
            if DateIndex==0:
                StackMask=np.empty((Dates.shape[0],Mask.profile["width"],Mask.profile["height"]),dtype=np.bool)
            StackMask[DateIndex,:,:]=Mask.read(1)
    return StackVegetationIndex, StackMask


def ModelForAnomalies(PixelsToTest,Dates,VegetationIndex,RemoveOutliers, SeuilMin, CoeffAnomalie):
    
    #Initialisation stack résultats
    rasterP=np.zeros((5,VegetationIndex.shape[-2],VegetationIndex.shape[-1]), dtype='float')
    rasterSigma=np.zeros((VegetationIndex.shape[-2],VegetationIndex.shape[-1]), dtype='float')
    
    Days=np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in Dates]) #Numéro des jours
    DateFirstTested=np.where(Dates==Dates[Dates>="2018-01-01"][0])[0][0]
    
    for pixel in range(PixelsToTest[0].shape[0]):
        X=PixelsToTest[0][pixel]
        Y=PixelsToTest[1][pixel]
        
        #DETERMINATION DE LA PREMIERE DATE AVEC 10 DATES VALIDES PRECEDENTES
        if np.sum(~VegetationIndex[:,X,Y].mask)<12:
            continue
        DateLim = getDateLim(DateFirstTested,VegetationIndex.mask[:,X,Y])
        ValidEarlier=~VegetationIndex[:DateLim,X,Y].mask # ; ValidLater=~VegetationIndex[DateLim:,X,Y].mask
  
        #MODELISATION DU CRSWIR SUR LES PREMIERES DATES
        p, sigma = ModelCRSWIR(VegetationIndex,DateLim, X, Y, Days, ValidEarlier, RemoveOutliers, SeuilMin, CoeffAnomalie)
        rasterP[:,X,Y]=p
        rasterSigma[X,Y]=sigma
        
        # DETECTION DES ANOMALIES
        # Etat=DetectAnomalies(VegetationIndex,DateLim, p, sigma,CoeffAnomalie, X, Y, Days, ValidLater)
        # StackEtat[~VegetationIndex[DateFirstTested:,X,Y].mask,X,Y]= np.concatenate((np.array(AddedDates* [False]).astype(bool),Etat))
        
    return rasterP,rasterSigma




def ModelCRSWIR(stackCRSWIR,DateLim, X, Y, Days, ValidEarlier, RemoveOutliers, SeuilMin, CoeffAnomalie):
    
    """
    Calcule les coefficients pour la prédiction de CRSWIR à partir de premières dates ainsi que le seuil utilisé pour la détection d'anomalies et la différence entre entre le CRSWIR prédit et réel des premières dates 

    Parameters
    ----------
    stackCRSWIR: (Dates,X,Y) masked ndarray
        CRSWIR pour chaque date et chaque pixel avec données invalides masques
    DateLim: int
        Indice de la première date qui sera testée. Permet d'identifier les dates utilisées pour la modélisation du CRSWIR normal.
    X: int
        Coordonnées du pixel en X
    Y: int
        Coordonnées du pixel en Y
    Days: 1D ndarray
        Liste de numéros de jours (Nombre de jours entre le lancement du premier satellite et la date voulue)
    ValidEarlier: 1D ndarray de type bool
        ndarray, True si donnée valide à cette date
    RemoveOutliers: bool
        Si True, la prédiction se fait en deux étape, les outliers sont retirés après la première étape
    SeuilMin: float
        Seuil minimum pour la détection d'anomalies
    CoeffAnomalie: float
        Coefficient multiplicateur du seuil de détection d'anomalies
    
    Returns
    -------
    p: (5,) ndarray
        Liste des coefficients pour la prédiction de CRSWIR
    sigma: float
        Seuil utilisé pour la détection d'anomalies, maximum entre l'écart type des différences du CRSWIR avec la prédiction et le seuil minimum défini comme paramètre
    diffEarlier: 1D ndarray
        Liste des différences entre entre le CRSWIR prédit et réel des premières dates. Utilisé pour export au niveau des données d'observations 
    
    """
    
    stackCRSWIRValidEarlier=stackCRSWIR[:DateLim,X,Y].compressed()
    
    M=Days[:DateLim,np.newaxis]**[0,1.0,1.0,1.0,1.0]
    M=M[ValidEarlier]
    M[:,1]=np.sin(2*math.pi*M[:,1]/365.25)
    M[:,2]=np.cos(2*math.pi*M[:,2]/365.25)
    M[:,3]=np.sin(2*2*math.pi*M[:,3]/365.25)
    M[:,4]=np.cos(2*2*math.pi*M[:,4]/365.25)
    p, _, _, _ = lstsq(M, stackCRSWIRValidEarlier)

    predictEarlier=functionToFit(Days[:DateLim][ValidEarlier],p) #Prédiction
    diffEarlier=np.abs(stackCRSWIRValidEarlier-predictEarlier)
    # sigma=max(SeuilMin,np.std(diffEarlier))
    sigma=np.std(diffEarlier)
    
    #POUR RETIRER OUTLIERS
    if RemoveOutliers:
        Outliers=diffEarlier<CoeffAnomalie*max(SeuilMin,sigma)
        M=M[Outliers,:]
        p, _, _, _ = lstsq(M, stackCRSWIRValidEarlier[Outliers])
        predictEarlier=functionToFit(np.array(Days[:DateLim])[ValidEarlier][Outliers],p)
        diffEarlier=np.abs(stackCRSWIRValidEarlier[Outliers]-predictEarlier)
        sigma=np.std(diffEarlier)
    
    return p, sigma



def functionToFit(x,p):
    """
    Calcule le CRSWIR prédit à partir du numéro du jour 

    Parameters
    ----------
    x: ndarray
        Liste de numéros de jours (Nombre de jours entre le lancement du premier satellite et la date voulue)
    p: ndarray
        ndarray avec les 5 coefficients permettant de modéliser le CRSWIR

    Returns
    -------
    ndarray
        Liste du CRSWIR prédit pour chaque jour dans la liste en entrée
    """
    y = p[0] + p[1]*np.sin(2*math.pi*x/365.25)+p[2]*np.cos(2*math.pi*x/365.25)+ p[3]*np.sin(2*2*math.pi*x/365.25)+p[4]*np.cos(2*2*math.pi*x/365.25)
    return y

