# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 15:48:32 2020

@author: raphael.dutrieux
"""

import numpy as np
import math, os, datetime
from scipy import ndimage
import rasterio
import copy
import time

def getSolNuUpdate(SolNu,Invalid,tuile,Version,x,y):
    
    """
    Effectue la mise à jour de détection de sol nu à partir des pré-masques sur les nouvelles dates et des données originellement sauvegardées. 
    Si le pixel est détecté comme potentiellement sol nu pour 3 dates valides successives, il est déterminé comme sol nu.

    Parameters
    ----------
    SolNu: numpy.ndarray
        Pré-masque (date,x,y) ndarray de type bool avec True si pixel est potientiellement sol nu.
    Invalid: numpy.ndarray
        (date,x,y) ndarray, masque avec True si pixel invalide à cette date
    tuile: str
        Nom de la tuile
    Version: str
        Nom de la version
    x: int
        Coordonnée en x du bloc
    y: int
        Coordonnée en y du bloc
        
    Returns
    -------
    stackSolNu : (date,x,y) ndarray
        ndarray de type bool avec True si pixel détecté comme sol nu
    DateFirstSol : (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série où le pré-masque SolNu vaut True. Utile pour la mise à jour à partir de nouvelles dates
    CompteurSolNu : (x,y) ndarray
        Compteur du nombre de dates succesives où le pré-masque SolNu vaut True au moment de la dernière date SENTINEL-2. Utile pour la mise à jour à partir de nouvelles dates
    """
    
    structSolNu=np.zeros((3,3,3),dtype='bool')
    structSolNu[1:3,1,1]=True
    
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/StackAtteint/StackSolNu_"+str(x)+"_"+str(y)+".tif") as src: 
        stackSolNu = src.read().astype("bool")
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/DateFirstSol/DateFirstSol_"+str(x)+"_"+str(y)+".tif") as src: 
        DateFirstSol = src.read(1)
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/DateFirstSol/CompteurSolNu_"+str(x)+"_"+str(y)+".tif") as src: 
        CompteurSolNu = src.read(1)

    BoolSolNu=stackSolNu[-1,:,:].copy()
    
    for date in range(SolNu.shape[0]):
        CompteurSolNu[np.logical_and(SolNu[date,:,:],~Invalid[date,:,:])]+=1
        CompteurSolNu[np.logical_and(~SolNu[date,:,:],~Invalid[date,:,:])]=0
        
        BoolSolNu[CompteurSolNu==3]=True
        DateFirstSol[np.logical_and(np.logical_and(CompteurSolNu==1,~BoolSolNu),~Invalid[date,:,:])]=stackSolNu.shape[0]+date #Garde la première date de détection de sol nu sauf si déjà détécté comme sol nu

    stackSolNu=np.concatenate((stackSolNu,np.zeros_like(SolNu,dtype="bool")))
    stackSolNu[DateFirstSol,np.arange(stackSolNu.shape[1])[:,None],np.arange(stackSolNu.shape[1])[None,:]]=True #Met True à la date de détection comme sol nu
    stackSolNu[:,~BoolSolNu]=False #Remet à 0 tous les pixels dont le compteur n'est pas arrivé à 3

    stackSolNu=ndimage.binary_dilation(stackSolNu,iterations=-1,structure=structSolNu) #Itération pour mettre des TRUE à partir du premier TRUE
    return stackSolNu, DateFirstSol, CompteurSolNu


def getSolNuUpdate2(SolNu,Invalid,stackSolNu,DateFirstSol,CompteurSolNu):
    
    """
    Effectue la mise à jour de détection de sol nu à partir des pré-masques sur les nouvelles dates et des données originellement sauvegardées. 
    Si le pixel est détecté comme potentiellement sol nu pour 3 dates valides successives, il est déterminé comme sol nu.

    Parameters
    ----------
    SolNu: numpy.ndarray
        Pré-masque (date,x,y) ndarray de type bool avec True si pixel est potientiellement sol nu.
    Invalid: numpy.ndarray
        (date,x,y) ndarray, masque avec True si pixel invalide à cette date
    stackSolNu : (date,x,y) ndarray
        ndarray de type bool avec True si pixel détecté comme sol nu
    DateFirstSol : (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série où le pré-masque SolNu vaut True. Utile pour la mise à jour à partir de nouvelles dates
    CompteurSolNu : (x,y) ndarray
        Compteur du nombre de dates succesives où le pré-masque SolNu vaut True au moment de la dernière date SENTINEL-2. Utile pour la mise à jour à partir de nouvelles dates
        
    Returns
    -------
    stackSolNu : (date,x,y) ndarray
        ndarray de type bool avec True si pixel détecté comme sol nu
    DateFirstSol : (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série où le pré-masque SolNu vaut True. Utile pour la mise à jour à partir de nouvelles dates
    CompteurSolNu : (x,y) ndarray
        Compteur du nombre de dates succesives où le pré-masque SolNu vaut True au moment de la dernière date SENTINEL-2. Utile pour la mise à jour à partir de nouvelles dates
    """
    start_time2 = time.time()
    structSolNu=np.zeros((3,3,3),dtype='bool')
    structSolNu[1:3,1,1]=True

    BoolSolNu=stackSolNu[-1,:,:].copy()
#    OldBoolSolNu=BoolSolNu.copy()
    print("Initialisation sol nu : %s secondes ---" %(time.time() - start_time2))
    start_time2 = time.time()
    for date in range(SolNu.shape[0]):
        CompteurSolNu[np.logical_and(SolNu[date,:,:],~Invalid[date,:,:])]+=1
        CompteurSolNu[np.logical_and(~SolNu[date,:,:],~Invalid[date,:,:])]=0
        
        BoolSolNu[CompteurSolNu==3]=True
        DateFirstSol[np.logical_and(np.logical_and(CompteurSolNu==1,~BoolSolNu),~Invalid[date,:,:])]=stackSolNu.shape[0]+date #Garde la première date de détection de sol nu sauf si déjà détécté comme sol nu
    print("detection sol nu : %s secondes ---" %(time.time() - start_time2))
    start_time2 = time.time()
    
#    stackSolNu=np.concatenate((stackSolNu,np.zeros_like(SolNu,dtype="bool")))
#    PixelsToTest=np.where(BoolSolNu) #On teste les pixels du masque foret non détectés en sol nu à la troisième date de 2018
#    for pixel in range(PixelsToTest[0].shape[0]):
#        ii=PixelsToTest[0][pixel]
#        kk=PixelsToTest[1][pixel]
#        stackSolNu[DateFirstSol[ii,kk]:,ii,kk]=True
        
#    stackSolNu=np.concatenate((stackSolNu,np.zeros_like(SolNu,dtype="bool")))
#    for ii in range(DateFirstSol.shape[0]):
#        for kk in range(DateFirstSol.shape[1]):
#            if BoolSolNu[ii,kk]:
#                stackSolNu[DateFirstSol[ii,kk]:,ii,kk]=True
#    print("Apply sol nu : %s secondes ---" %(time.time() - start_time2))
    
    start_time2 = time.time()
    stackSolNu=np.concatenate((stackSolNu,np.zeros_like(SolNu,dtype="bool")))
    stackSolNu[DateFirstSol,np.arange(stackSolNu.shape[1])[:,None],np.arange(stackSolNu.shape[1])[None,:]]=True #Met True à la date de détection comme sol nu
    stackSolNu[:,~BoolSolNu]=False #Remet à 0 tous les pixels dont le compteur n'est pas arrivé à 3
    print("End of detection sol nu : %s secondes ---" %(time.time() - start_time2))
    start_time2 = time.time()
    stackSolNu=ndimage.binary_dilation(stackSolNu,iterations=-1,structure=structSolNu) #Itération pour mettre des TRUE à partir du premier TRUE
    print("Dilation : %s secondes ---" %(time.time() - start_time2))
    return stackSolNu, DateFirstSol, CompteurSolNu


def DetectAnomalies(VegetationIndex, StackP, rasterSigma, CoeffAnomalie, date):
    """
    Lors de la mise à jour, importe les coefficients et le seuil pour la détection d'anomalies depuis les rasters sauvegardés puis détecte les anomalies en comparant le CRSWIR prédit sur les dates testées et le CRSWIR réel.

    Parameters
    ----------
    stackCRSWIR: (Dates,X,Y) masked ndarray
        CRSWIR pour chaque date et chaque pixel avec données invalides masques
    NewDays: 1D ndarray
        Numéro des nouvelles dates
    CoeffAnomalie: float
        Coefficient multiplicateur du seuil de détection d'anomalies
    Version: str
        Nom de la version
    tuile: str
        Nom de la tuile
    x: int
        Coordonnée en x du bloc
    y: int
        Coordonnée en y du bloc
    
    Returns
    -------
    (Dates,x,y) ndarray de type bool
        True si anomalie détectée (CRSWIR réel > CRSWIR prédit + sigma*CoeffAnomalie)
    """
    # NewDays=Days[-stackBands.shape[0]:]
    
    NewDay=(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days
    
    PredictedVegetationIndex = StackP[0,:,:] + StackP[1,:,:]*np.sin(2*math.pi*NewDay/365.25) + StackP[2,:,:]*np.cos(2*math.pi*NewDay/365.25) + StackP[3,:,:]*np.sin(2*2*math.pi*NewDay/365.25)+StackP[4,:,:]*np.cos(2*2*math.pi*NewDay/365.25)

    
    # PredictedCRSWIR = StackP[0,:,:][:,:,np.newaxis] + StackP[1,:,:][:,:,np.newaxis]*np.sin(2*math.pi*NewDays/365.25) + StackP[2,:,:][:,:,np.newaxis]*np.cos(2*math.pi*NewDays/365.25) + StackP[3,:,:][:,:,np.newaxis]*np.sin(2*2*math.pi*NewDays/365.25)+StackP[4,:,:][:,:,np.newaxis]*np.cos(2*2*math.pi*NewDays/365.25)
    # PredictedCRSWIR=np.moveaxis(PredictedCRSWIR, -1, 0)
    DiffVegetationIndex = VegetationIndex-PredictedVegetationIndex
    Anomalies = DiffVegetationIndex > CoeffAnomalie*rasterSigma
    
    Anomalies[rasterSigma==0]=False #Devrait  retirer le souci des zones presque toujours invalides

    return Anomalies

def DetectAnomaliesUpdate2(stackCRSWIR, NewDays, CoeffAnomalie, StackP, rasterSigma):
    """
    Lors de la mise à jour, importe les coefficients et le seuil pour la détection d'anomalies depuis les rasters sauvegardés puis détecte les anomalies en comparant le CRSWIR prédit sur les dates testées et le CRSWIR réel.

    Parameters
    ----------
    stackCRSWIR: (Dates,X,Y) masked ndarray
        CRSWIR pour chaque date et chaque pixel avec données invalides masques
    NewDays: 1D ndarray
        Numéro des nouvelles dates
    CoeffAnomalie: float
        Coefficient multiplicateur du seuil de détection d'anomalies
    StackP : (5,x,y) ndarray
        ndarray avec la valeur des coefficients pour la modélisation du CRSWIR pour chaque pixel
    rasterSigma: (x,y) ndarray
        ndarray avec la valeur du seuil pour la détection d'anomalies pour chaque pixel
    
    Returns
    -------
    (Dates,x,y) ndarray de type bool
        True si anomalie détectée (CRSWIR réel > CRSWIR prédit + sigma*CoeffAnomalie)
    """
    
    # NewDays=Days[-stackBands.shape[0]:]
        
    PredictedCRSWIR = StackP[0,:,:][:,:,np.newaxis] + StackP[1,:,:][:,:,np.newaxis]*np.sin(2*math.pi*NewDays/365.25) + StackP[2,:,:][:,:,np.newaxis]*np.cos(2*math.pi*NewDays/365.25) + StackP[3,:,:][:,:,np.newaxis]*np.sin(2*2*math.pi*NewDays/365.25)+StackP[4,:,:][:,:,np.newaxis]*np.cos(2*2*math.pi*NewDays/365.25)
    PredictedCRSWIR=np.moveaxis(PredictedCRSWIR, -1, 0)
    DiffCRSWIR = stackCRSWIR-PredictedCRSWIR
    StackEtat = DiffCRSWIR > CoeffAnomalie*rasterSigma
    
    StackEtat[:,rasterSigma==0]=False #Devrait  retirer le souci des zones presque toujours invalides

    return StackEtat

def DetectScolytes(CompteurScolyte,DateFirstScolyte, EtatChange, Anomalies, Mask, DateIndex):
   
    CompteurScolyte[np.logical_and(Anomalies!=EtatChange,~Mask)]+=1
    CompteurScolyte[np.logical_and(Anomalies==EtatChange,~Mask)]=0
    
    EtatChange[np.logical_and(CompteurScolyte==3,~Mask)]=~EtatChange[np.logical_and(CompteurScolyte==3,~Mask)] #Changement d'état si CompteurScolyte = 3 et date valide
    CompteurScolyte[CompteurScolyte==3]=0
    DateFirstScolyte[np.logical_and(np.logical_and(CompteurScolyte==1,~EtatChange),~Mask)]=DateIndex #Garde la première date de détection de scolyte sauf si déjà détécté comme scolyte
   

    return CompteurScolyte,DateFirstScolyte, EtatChange

def DetectScolytesUpdate2(StackEtat, CRSWIRMask,stackDetected,DateFirstScolyte,CompteurScolyte,FirstDateDiff):
    """
    Détecte les déperissements, lorsqu'il y a trois dates valides successives avec des anomalies 

    Parameters
    ----------
    StackEtat: (Dates,X,Y) ndarray de type bool
        Si True, anomalie détectée à cette date
    CRSWIRMask: (Dates,X,Y) ndarray de type bool
        Si True, pixel invalide à cette date
    stackDetected: (Dates,X,Y) ndarray de type bool
        Si True, pixel détecté comme atteint à cette date
    DateFirstScolyte: (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série d'anomalies de la dernière mise à jour.
    CompteurScolyte: (x,y) ndarray
        Compteur du nombre de dates succesives d'anomalies au moment de la dernière date SENTINEL-2 de la dernière mise à jour.
    FirstDateDiff: int
        Indice de la première date où il y a une différence avec les calculs originaux pour savoir à partir de quelle date réecrire les résultats 
    Returns
    -------
    NewStackDetected: (Dates,X,Y) ndarray de type bool
        Si True, pixel détecté comme atteint à cette date
    DateFirstScolyte: (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série d'anomalies. Utile pour la mise à jour à partir de nouvelles dates
    CompteurScolyte: (x,y) ndarray
        Compteur du nombre de dates succesives d'anomalies au moment de la dernière date SENTINEL-2. Utile pour la mise à jour à partir de nouvelles dates 
    stackStress: (Dates,x,y) ndarray
        ndarray avec l'état (stressé ou non) des pixels pour chaque date (Ne marche pas avant la troisième date valide stressée)
    FirstDateDiff: int
        Indice de la première date où il y a une différence avec les calculs originaux pour savoir à partir de quelle date réecrire les résultats 
    """

    
    structScolyte=np.zeros((3,3,3),dtype='bool')
    structScolyte[1:3,1,1]=True
    
    
    stackStress=np.zeros((stackDetected.shape[0]+CRSWIRMask.shape[0],stackDetected.shape[1],stackDetected.shape[2]), dtype='bool')
    
    EtatChange=stackDetected[-1,:,:].copy()
    
    for date in range(StackEtat.shape[0]):

        CompteurScolyte[np.logical_and(StackEtat[date,:,:]!=EtatChange,~CRSWIRMask[date,:,:])]+=1
        CompteurScolyte[np.logical_and(StackEtat[date,:,:]==EtatChange,~CRSWIRMask[date,:,:])]=0
        
        EtatChange[np.logical_and(CompteurScolyte==3,~CRSWIRMask[date,:,:])]=~EtatChange[np.logical_and(CompteurScolyte==3,~CRSWIRMask[date,:,:])]
        CompteurScolyte[CompteurScolyte==3]=0
        DateFirstScolyte[np.logical_and(np.logical_and(CompteurScolyte==1,~EtatChange),~CRSWIRMask[date,:,:])]=stackDetected.shape[0]+date #Garde la première date de détection de scolyte sauf si déjà détécté comme scolyte
        stackStress[stackDetected.shape[0]+date,:,:] = EtatChange
        
    NewStackDetected=np.concatenate((stackDetected,np.zeros_like(StackEtat,dtype="bool")))
    NewStackDetected[DateFirstScolyte,np.arange(NewStackDetected.shape[1])[:,None],np.arange(NewStackDetected.shape[1])[None,:]]=True #Met True à la date de détection comme scolyte
    NewStackDetected[:,~EtatChange]=False #Remet à 0 tous les pixels dont le compteur n'est pas arrivé à 3

    


    DateDiffDetected=np.where(NewStackDetected[:stackDetected.shape[0]]!=stackDetected)[0]
    if DateDiffDetected.size!=0:
        NewFirstDateDiff=np.min(DateDiffDetected)
    else:
        NewFirstDateDiff=stackDetected.shape[0]
        
    NewStackDetected=ndimage.binary_dilation(NewStackDetected,iterations=-1,structure=structScolyte) #Itération pour mettre des TRUE à partir du premier TRUE    
        
    FirstDateDiff=min(FirstDateDiff,NewFirstDateDiff)
    return NewStackDetected, DateFirstScolyte, CompteurScolyte, stackStress, FirstDateDiff