# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 17:36:42 2020

@author: raphael.dutrieux
"""

import numpy as np
import math, os, datetime
from scipy.linalg import lstsq
from scipy import ndimage
import rasterio
import pickle

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

def getDateLim(DateFirstTested,CRSWIRMask):
    
    if np.sum(~CRSWIRMask[:DateFirstTested])<10:
        DateLim=np.where(np.cumsum(~CRSWIRMask)==10)[0][0]
        
        return DateLim
    else:
        return DateFirstTested
        
        
    
    

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


def DetectAnomalies(stackCRSWIR,DateLim, p, sigma,CoeffAnomalie, X, Y, Days, ValidLater):
    
    """
    Détecte les anomalies en comparant le CRSWIR prédit sur les dates testées et le CRSWIR réel 

    Parameters
    ----------
    stackCRSWIR: (Dates,X,Y) masked ndarray
        CRSWIR pour chaque date et chaque pixel avec données invalides masques
    DateLim: int
        Indice de la première date qui sera testée. Permet d'identifier les dates utilisées pour la modélisation du CRSWIR normal.
    p: (5,) ndarray
        Liste des coefficients pour la prédiction de CRSWIR
    sigma: float
        Seuil utilisé pour la détection d'anomalies
    CoeffAnomalie: float
        Coefficient multiplicateur du seuil de détection d'anomalies
    X: int
        Coordonnées du pixel en X
    Y: int
        Coordonnées du pixel en Y
    Days: 1D ndarray
        Liste de numéros de jours (Nombre de jours entre le lancement du premier satellite et la date voulue)
    ValidLater: 1D ndarray de type bool
        ndarray, True si donnée valide à cette date
    
    Returns
    -------
    1D ndarray de type bool
        True si anomalie détectée (CRSWIR réel > CRSWIR prédit + sigma*CoeffAnomalie)
    """
    
    stackCRSWIRValidLater=stackCRSWIR[DateLim:,X,Y].compressed()
    predictLater=functionToFit(Days[DateLim:][ValidLater],p)
    diffLater=stackCRSWIRValidLater-predictLater
    Etat=diffLater>CoeffAnomalie*sigma #Indice avec augmentation de l'indice quand atteint
    # Etat=diffLater<-CoeffAnomalie*sigma #Indice avec baisse de l'indice quand atteint
    return Etat


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


# def DetectScolytes(stackAtteint, Etat, DateLim,ValidLater, X, Y):
#     """
#     Deprecated, use DetectScolytes2
#     """
#     stackStress=np.zeros((stackAtteint.shape[0],stackAtteint.shape[1],stackAtteint.shape[2]), dtype='bool')
    
#     IndexRef=np.array(range(0,ValidLater.shape[0]))[ValidLater]
#     EtatFinal=False
#     SearchingBoolList=np.array([True,True,True])

#     for i in range(1,len(Etat)-1):
#         if stackAtteint[DateLim:,X,Y][ValidLater][i+1]==2: #Si sol nu à partir de cette date, arret de la recherche
#             stackStress[DateLim:,X,Y][IndexRef[i-2:i+1]]=EtatFinal #Extraire Infos Stress
#             break
#         if np.array_equal(Etat[i-1:i+2],SearchingBoolList):
#             SearchingBoolList=SearchingBoolList==False #On change la série cherchée
#             EtatFinal=not(EtatFinal)
#             saveIndex=IndexRef[i-1]
#         stackStress[DateLim:,X,Y][IndexRef[i-1]]=EtatFinal
#     stackStress[DateLim:,X,Y][IndexRef[len(Etat)-2:len(Etat)+1]]=EtatFinal
  
#     if EtatFinal:
#         stackAtteint[DateLim:,X,Y][saveIndex:][stackAtteint[DateLim:,X,Y][saveIndex:]!=2]=1
#         if 2 in stackAtteint[DateLim:,X,Y][saveIndex:]:
#             stackAtteint[DateLim:,X,Y][saveIndex:][stackAtteint[DateLim:,X,Y][saveIndex:]==2]=3
#     return stackAtteint, stackStress


def DetectScolytes2(StackEtat, CRSWIRMask):
    """
    Détecte les déperissements, lorsqu'il y a trois dates valides successives avec des anomalies 

    Parameters
    ----------
    StackEtat: (Dates,X,Y) ndarray de type bool
        Si True, anomalie détectée à cette date
    CRSWIRMask: (Dates,X,Y) ndarray de type bool
        Si True, pixel invalide à cette date
    
    Returns
    -------
    stackDetected: (Dates,X,Y) ndarray de type bool
        Si True, pixel détecté comme atteint à cette date
    DateFirstScolyte: (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série d'anomalies. Utile pour la mise à jour à partir de nouvelles dates
    CompteurScolyte: (x,y) ndarray
        Compteur du nombre de dates succesives d'anomalies au moment de la dernière date SENTINEL-2. Utile pour la mise à jour à partir de nouvelles dates 
    """
    # CRSWIRMask=stackCRSWIR.mask
    DateFirstTested=CRSWIRMask.shape[0]-StackEtat.shape[0]
    
    structScolyte=np.zeros((3,3,3),dtype='bool')
    structScolyte[1:3,1,1]=True
    
    stackDetected=np.zeros((CRSWIRMask.shape[0],CRSWIRMask.shape[1],CRSWIRMask.shape[2]), dtype='bool')
    
    CompteurScolyte= np.zeros((CRSWIRMask.shape[1],CRSWIRMask.shape[2]),dtype=np.uint8) #np.int8 possible ?
    DateFirstScolyte=np.zeros((CRSWIRMask.shape[1],CRSWIRMask.shape[2]),dtype=np.uint16) #np.int8 possible ?
    EtatChange=np.zeros((CRSWIRMask.shape[1],CRSWIRMask.shape[2]),dtype=bool)
      
    for date in range(StackEtat.shape[0]):

        CompteurScolyte[np.logical_and(StackEtat[date,:,:]!=EtatChange,~CRSWIRMask[DateFirstTested+date,:,:])]+=1
        CompteurScolyte[np.logical_and(StackEtat[date,:,:]==EtatChange,~CRSWIRMask[DateFirstTested+date,:,:])]=0
        
        EtatChange[np.logical_and(CompteurScolyte==3,~CRSWIRMask[DateFirstTested+date,:,:])]=~EtatChange[np.logical_and(CompteurScolyte==3,~CRSWIRMask[DateFirstTested+date,:,:])] #Changement d'état si CompteurScolyte = 3 et date valide
        CompteurScolyte[CompteurScolyte==3]=0
        DateFirstScolyte[np.logical_and(np.logical_and(CompteurScolyte==1,~EtatChange),~CRSWIRMask[DateFirstTested+date,:,:])]=DateFirstTested+date #Garde la première date de détection de scolyte sauf si déjà détécté comme scolyte

    stackDetected[DateFirstScolyte,np.arange(stackDetected.shape[1])[:,None],np.arange(stackDetected.shape[1])[None,:]]=True #Met True à la date de détection comme scolyte
    stackDetected[:,~EtatChange]=False #Remet à 0 tous les pixels dont le compteur n'est pas arrivé à 3
    stackDetected=ndimage.binary_dilation(stackDetected,iterations=-1,structure=structScolyte) #Itération pour mettre des TRUE à partir du premier TRUE
    
    return stackDetected, DateFirstScolyte, CompteurScolyte



def CorrectCRSWIR(DictSentinelPaths,date,MaskForet):
    """
    Importe les bandes d'une date, calcule des masques, puis le CRSWIR médian des pixels valides.

    Parameters
    ----------
    dirDateSEN: str
        Chemin du dossier avec les données d'une date SENTINEL-2
    MaskForet: (X,Y) ndarray de type bool
        ndarray avec True si pixel dans les peuplements concernés
    
    Returns
    -------
    CRSWIRForetBD: float
        CRSWIR médian des pixels valides dans la BDFORET à l'échelle de la tuile'
    """    
    
    
    #Lecture de RGB et sauvegarde dans stackBands
    with rasterio.open(DictSentinelPaths[date]["B2"]) as B2:
        stackBands=np.empty((int(B2.profile["width"]/2),int(B2.profile["height"]/2),6),dtype='int16')
        stackBands[:,:,0]=B2.read(1)[::2,::2]
    with rasterio.open(DictSentinelPaths[date]["B3"]) as B3:
        stackBands[:,:,1]=B3.read(1)[::2,::2]
    with rasterio.open(DictSentinelPaths[date]["B4"]) as B4:
        stackBands[:,:,2]=B4.read(1)[::2,::2]
    
    with rasterio.open(DictSentinelPaths[date]["B8A"]) as B8A:
        stackBands[:,:,3] = B8A.read(1)
    with rasterio.open(DictSentinelPaths[date]["B11"]) as B11:
        stackBands[:,:,4] = B11.read(1)
    with rasterio.open(DictSentinelPaths[date]["B12"]) as B12:
        stackBands[:,:,5] = B12.read(1)
    # print("Import bandes : %s secondes ---" % (time.time() - start_time1))
        
    
    stackNG=stackBands[:,:,1]/(stackBands[:,:,3]+stackBands[:,:,2]+stackBands[:,:,1])
    CRSWIR=stackBands[:,:,4]/(stackBands[:,:,3]+((stackBands[:,:,5]-stackBands[:,:,3])/(2185.7-864))*(1610.4-864)) #Calcul du CRSWIR

    Ombres=np.any(stackBands==0,axis=2) #Reflectance d'une des bandes à 0
    HorsFauche=stackBands[:,:,5]<0 #<0 -> -10000 Peut retirer aussi des soucis dûs à l'interpolation
    
    cond1=stackNG>0.15
    cond2=stackBands[:,:,0]>400
    cond3=stackBands[:,:,0]>700
    Nuages=np.logical_or(np.logical_and(np.logical_and(HorsFauche,cond1),cond2),cond3)

    Invalid = np.logical_or(
        np.logical_or(
        np.logical_or(stackBands[:,:,5] > 1250,stackBands[:,:,0] > 600),
        np.logical_or(stackBands[:,:,1]+stackBands[:,:,2] > 800,Nuages)
        ),
        np.logical_or(
            np.logical_or(Ombres,HorsFauche),
            CRSWIR > 1
            ))
    
    InvalidForetBD=np.logical_or(Invalid,~MaskForet[::2,::2])
    
    CRSWIRForetBD=np.median(CRSWIR[~InvalidForetBD])

    return CRSWIRForetBD


def getListCRSWIRmedian(DictSentinelPaths,Dates,tuile,MaskForet):
    
    """
    Importe le dictionnaire avec le CRSWIR médian calculé pour chaque date, calcule le CRSWIR médian pour les dates non calculées, sauvegarde les résultats
    Renvoi la liste des CRSWIR médians pour l'ensemble des dates

    Parameters
    ----------
    tuile: str
        Nom de la tuile concernée
    MaskForet: (X,Y) ndarray de type bool
        ndarray avec True si pixel dans les peuplements concernés
    ValidDirDates: 1D ndarray
        Liste des dossiers des dates valides
    
    Returns
    -------
    1D ndarray
        Liste des CRSWIR médians à l'échelle de la tuile'
    """
    DirSentinelData = os.path.dirname(os.path.dirname(os.path.dirname(list(list(DictSentinelPaths.values())[0].values())[0])))
    
    if os.path.exists(os.path.join(DirSentinelData,tuile,"CRSWIRmedian")):
        with open(os.path.join(DirSentinelData,tuile,"CRSWIRmedian"), 'rb') as f:
            CRSWIRmedian = pickle.load(f)
    else:
        CRSWIRmedian={}
        
    for date in Dates:
        if not(date in CRSWIRmedian.keys()):
            print("Calcul CRSWIR median " + date)
            CRSWIRmedian[date] = CorrectCRSWIR(DictSentinelPaths,date,MaskForet)
    CRSWIRmedian=dict(sorted(CRSWIRmedian.items()))
    
    with open(os.path.join(DirSentinelData,tuile,"CRSWIRmedian"), 'wb') as f:
        pickle.dump(CRSWIRmedian, f)
    # print(list(CRSWIRmedian.values()))
    return np.array(list(CRSWIRmedian.values()))

def getCRSWIRCorrection(DictSentinelPaths,Dates,tuile,MaskForet):
    """
    Prend la liste des CRSWIR médians à partir desquels une valeur correctrice est calculée pour chaque date

    Parameters
    ----------
    tuile: str
        Nom de la tuile concernée
    MaskForet: (X,Y) ndarray de type bool
        ndarray avec True si pixel dans les peuplements concernés
    ValidDirDates: 1D ndarray
        Liste des dossiers des dates valides
    Dates:
        Liste des dates valides au format "AAAA-MM-JJ"
    
    Returns
    -------
    1D ndarray
        Liste des valeurs correctrices pour chaque date
    """
    
    ListCRSWIRmedian = getListCRSWIRmedian(DictSentinelPaths,Dates,tuile,MaskForet)
    # print(ListCRSWIRmedian)
    Days=np.array([(datetime.datetime.strptime(date, '%Y-%m-%d')-datetime.datetime.strptime('2015-06-23', '%Y-%m-%d')).days for date in Dates]) #Numéro des jours 
    
    M=Days[:,np.newaxis]**[0,1.0,1.0,1.0,1.0]
    M[:,1]=np.sin(2*math.pi*M[:,1]/365.25)
    M[:,2]=np.cos(2*math.pi*M[:,2]/365.25)
    M[:,3]=np.sin(2*2*math.pi*M[:,3]/365.25)
    M[:,4]=np.cos(2*2*math.pi*M[:,4]/365.25)
    p, _, _, _ = lstsq(M, ListCRSWIRmedian)
    
    predictedCRSWIR=functionToFit(Days,p) #Prédiction
    diffCRSWIR=ListCRSWIRmedian-predictedCRSWIR
    
    return diffCRSWIR 


def ModelCRSWIRAlongAxis(SerieCRSWIR,Days,DateFirstTested,RemoveOutliers,SeuilMin,CoeffAnomalie):
    # SerieCRSWIR=stackCRSWIR[:,50,80]
    # if np.sum(~SerieCRSWIR.mask)<12:
    #     return np.zeros((SerieCRSWIR.shape[0]), dtype='bool')
    if np.sum(~SerieCRSWIR.mask)<12:
        return np.zeros((5), dtype='float'), 0, 0
        #DETERMINATION DE LA PREMIERE DATE AVEC 10 DATES VALIDES PRECEDENTES
    # DateFirstTested=np.where(Dates==Dates[Dates>="2018-01-01"][0])[0][0]
    
    DateLim=DateFirstTested
    AddedDates=0
    if np.sum(~SerieCRSWIR.mask[:DateLim])<10:
        DateLim2=np.where(np.cumsum(~SerieCRSWIR.mask)==10)[0][0]
        AddedDates=DateLim2-DateLim-np.sum(SerieCRSWIR.mask[DateLim:DateLim2+1])
        DateLim=DateLim2
    
    ValidEarlier=~SerieCRSWIR.mask[:DateLim] ; ValidLater=~SerieCRSWIR.mask[DateLim:] ; Valid=np.append(ValidEarlier,ValidLater) #Dates valides
        
    stackCRSWIRValidEarlier=SerieCRSWIR[:DateLim].compressed()
    
    # print(stackCRSWIRValidEarlier.shape)
    
    M=Days[:DateLim,np.newaxis]**[0,1.0,1.0,1.0,1.0]
    # print(M.shape)
    M=M[ValidEarlier]
    # print(M.shape)
    M[:,1]=np.sin(2*math.pi*M[:,1]/365.25)
    M[:,2]=np.cos(2*math.pi*M[:,2]/365.25)
    M[:,3]=np.sin(2*2*math.pi*M[:,3]/365.25)
    M[:,4]=np.cos(2*2*math.pi*M[:,4]/365.25)
    p, _, _, _ = lstsq(M, stackCRSWIRValidEarlier)

    predictEarlier=functionToFit(Days[:DateLim][ValidEarlier],p) #Prédiction
    diffEarlier=np.abs(stackCRSWIRValidEarlier-predictEarlier)
    sigma=max(SeuilMin,np.std(diffEarlier))
    
    #POUR RETIRER OUTLIERS
    if RemoveOutliers:
        Outliers=diffEarlier<CoeffAnomalie*sigma
        M=M[Outliers,:]
        p, _, _, _ = lstsq(M, stackCRSWIRValidEarlier[Outliers])
        predictEarlier=functionToFit(np.array(Days[:DateLim])[ValidEarlier][Outliers],p)
        diffEarlier=np.abs(stackCRSWIRValidEarlier[Outliers]-predictEarlier)
        sigma=max(SeuilMin,np.std(diffEarlier))
    
    return p, sigma, diffEarlier