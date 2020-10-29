# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 17:30:16 2020

@author: raphael.dutrieux
"""

import os, sys ; from glob import glob 
import rasterio ; import rasterio.features
import numpy as np
import pandas as pd
from scipy import ndimage
import time
import xarray as xr

from Lib_ComputeMasks import getPreMasks, getNuages2, getSolNu2


def getDates(tuile,DataDirectory):
    AllPaths=glob(DataDirectory+"/VegetationIndex/"+tuile+"/*.tif")
    Dates=[Path[-14:-4] for Path in AllPaths]
    return np.array(Dates)

def getOldDates(tuile,DataDirectory):
    AllPaths=glob(DataDirectory+"/DataAnomalies/"+tuile+"/*.tif")
    Dates=[Path[-14:-4] for Path in AllPaths]
    return np.array(Dates)

def getPercNuage(DatePath,DataSource):
    """
    Calcule le pourcentage d'ennuagement d'une date SENTINEL-2 à partir du masque THEIA

    Parameters
    ----------
    dirDateSEN: str
        Chemin du dossier des données d'une date SENTINEL-2 

    Returns
    -------
    float
        Pourcentage d'ennuagement de la date
    """
    with rasterio.open(DatePath["Mask"]) as clm:
        if DataSource=="THEIA":
            with rasterio.open(DatePath["B11"]) as Couverture:
                if np.all(Couverture.read(1)==-10000):
                    return 2.0
                else:
                    return np.sum(clm.read(1)>0)/np.sum(Couverture.read(1)!=-10000)#Nombre de pixels ennuagés sur le nombre de pixels dans la fauchée du satellite
        elif DataSource=="Scihub" or DataSource=="PEPS":
            CLM=clm.read(1)
            Valid=np.logical_or(CLM==4,CLM==5)
            return np.sum(~Valid)/np.sum(CLM!=0)
   

def formattedDate(date):
    return date[:4]+"-"+date[4:6]+"-"+date[6:8]

def getDirDates(tuile,DataSource):
    """
    A partir de la tuile et de la source des données, renvoie un dictionnaire où les clés sont les dates au format "YYYY-MM-JJ" et les valeurs sont les chemins des dossiers de données SENTINEL-2 correspondants

    Parameters
    ----------
    tuile: str
        Nom de la tuile concernée 
    DataSource: str
        Source des données parmi THEIA, Scihub et PEPS
        
    Returns
    -------
    dict
        Dictionnaire où les clés sont les dates au format "YYYY-MM-JJ" et les valeurs sont les chemins des dossiers de données SENTINEL-2 correspondants
    """
    if DataSource=="THEIA":
        DirDates = glob(os.getcwd()+"/Data/SENTINEL/"+tuile+"/SEN*")
        def getDateFromPath(dirdate):
            return dirdate.split('_')[-5].split('-')[0]
    elif DataSource=="Scihub":
        DirDates = glob(os.getcwd()+"/Data/SENTINEL/"+tuile+"/S2*")
        def getDateFromPath(dirdate):
            return dirdate.split('_')[-5][:8]
    elif DataSource=="PEPS":
        DirDates = glob(os.getcwd()+"/Data/SENTINEL/"+tuile+"/L2*")
        def getDateFromPath(dirdate):
            return dirdate.split('_')[-1][:8]
    else:
        print("Source de données inconnu")
        sys.exit()
    
    DirDates.sort(key=getDateFromPath)
    Dates=[formattedDate(getDateFromPath(dirdate)) for dirdate in DirDates]

    return dict(zip(Dates, DirDates))
    
def getSentinelPaths(tuile,DataSource):
    DictDirDates=getDirDates(tuile,DataSource)
    DictSentinelPaths={}
    for date in DictDirDates:
        AllPaths=glob(DictDirDates[date]+"/**",recursive=True)
        DictSentinelPaths[date]={}
        if np.any(["B2" in path or "B02" in path for path in AllPaths]):
            DictSentinelPaths[date]["B2"]=[path for path in AllPaths if "_B2" in path or "_B02" in path][0]
        if np.any(["B3" in path or "B03" in path for path in AllPaths]):
            DictSentinelPaths[date]["B3"]=[path for path in AllPaths if "_B3" in path or "_B03" in path][0]
        if np.any(["B4" in path or "B04" in path for path in AllPaths]):
            DictSentinelPaths[date]["B4"]=[path for path in AllPaths if "_B4" in path or "_B04" in path][0]
        if np.any(["B5" in path or "B05" in path for path in AllPaths]):
            DictSentinelPaths[date]["B5"]=[path for path in AllPaths if "_B5" in path or "_B05" in path][0]
        if np.any(["B6" in path or "B06" in path for path in AllPaths]):
            DictSentinelPaths[date]["B6"]=[path for path in AllPaths if "_B6" in path or "_B06" in path][0]
        if np.any(["B7" in path or "B07" in path for path in AllPaths]):
            DictSentinelPaths[date]["B7"]=[path for path in AllPaths if "_B7" in path or "_B07" in path][0]
        if np.any([("_B8" in path or "_B08" in path) and not("_B8A" in path) for path in AllPaths]):
            DictSentinelPaths[date]["B8"]=[path for path in AllPaths if ("_B8" in path or "_B08" in path) and not("_B8A" in path)][0]
        if np.any(["B8A" in path for path in AllPaths]):
            DictSentinelPaths[date]["B8A"]=[path for path in AllPaths if "_B8A" in path][0]
        if np.any(["B11" in path for path in AllPaths]):
            DictSentinelPaths[date]["B11"]=[path for path in AllPaths if "_B11" in path][0]
        if np.any(["B12" in path for path in AllPaths]):
            DictSentinelPaths[date]["B12"]=[path for path in AllPaths if "_B12" in path][0]
            
        if np.any(["_CLM_" in path or "SCL" in path for path in AllPaths]):
            DictSentinelPaths[date]["Mask"]=[path for path in AllPaths if "_CLM_" in path or "SCL" in path][0]
                

    # print(DictSentinelPaths)
   
    return DictSentinelPaths
    

def getValidDates(DictSentinelPaths,tuile, PercNuageLim,DataSource):
    """
    Importe le pourcentage d'ennuagement des dates SENTINEL-2 depuis un .csv, ou le calcul et le rajoute au .csv si de nouvelles dates sont détectées.
    Puis les dates de la tuile sont filtrées selon le paramètre de seuil d'ennuagement maximal.

    Parameters
    ----------
    tuile: str
        Nom de la tuile concernée 
    PercNuageLim: float
        Pourcentage d'ennuagement maximal autorisé

    Returns
    -------
    DirDates: list
        Liste des chemins des dossiers des dates SENTINEL-2 téléchargées
    ValidDirDates : list
        Liste des chemins des dossiers des dates SENTINEL-2 valides
    Dates: ndarray
        Array des dates valides au format "AAAA-MM-JJ"
    """
   
    
    RecalculateEnnuagement=True
    PercNuageDates = {}
    if os.path.exists(os.getcwd()+"/Data/SENTINEL/"+tuile+"/Ennuagement.csv"):
        RecalculateEnnuagement=False
        
        #Formation du dictionnaire à partir du csv
        PercNuageDatesPanda=pd.read_csv(os.getcwd()+"/Data/SENTINEL/"+tuile+"/Ennuagement.csv")
        for row in range(PercNuageDatesPanda.shape[0]):
            PercNuageDates[PercNuageDatesPanda.iloc[row][0]]=PercNuageDatesPanda.iloc[row][1]
            
        #Vérif si il existe des dates pas dans le dictionnaire
        for date in DictSentinelPaths:
            if not(date in PercNuageDates.keys()):
                RecalculateEnnuagement=True
                print("Nouvelle date")
                
    #Si il y a de nouvelles dates
    if RecalculateEnnuagement:
        print("Recalcul de l'ennuagement")

        for date in DictSentinelPaths:
            if not(date in PercNuageDates.keys()):
                print(date)
                PercNuageDates[date] = getPercNuage(DictSentinelPaths[date],DataSource)
                
        PercNuageDatesPanda=pd.DataFrame.from_dict(PercNuageDates, orient='index')
        PercNuageDatesPanda.to_csv(os.getcwd()+"/Data/SENTINEL/"+tuile+"/Ennuagement.csv")
    else:
        print("Ennuagement déjà calculé")
    
    Dates=[]
    for date in DictSentinelPaths:
        if float(PercNuageDates[date]) < PercNuageLim:
            Dates+=[date]
    return np.array(Dates)
            
def getResampledTheiaMask(DictSentinelPath):
    
    with rasterio.open(DictSentinelPath["Mask"]) as mask:
        stackMask=mask.read(1)
    stackMaskInterpolated=ndimage.zoom(stackMask,zoom=[2.0,2.0],order=0)

    return stackMaskInterpolated
        

#Probleme des -10000 pour le resampling bicubique



def getResampledStack2(DictSentinelPath,Bands,InterpolationOrder):
    # DictSentinelPath=DictSentinelPaths[date]
    # if "Mask" in DictSentinelPath: 
    #     DictSentinelPath2=dict(DictSentinelPath)
    #     del DictSentinelPath2["Mask"]
    DictBandPosition={}
    for BandIndex,Band in enumerate(Bands):
        DictBandPosition[Band]=BandIndex
        with rasterio.open(DictSentinelPath[Band]) as RasterBand:
            InterpolationFactor=RasterBand.profile["transform"][0]/10
            if BandIndex==0: stackBands=np.empty((int(RasterBand.profile["width"]*InterpolationFactor),int(RasterBand.profile["height"]*InterpolationFactor),len(Bands)),dtype='int16')
            stackBands[:,:,BandIndex] = ndimage.zoom(RasterBand.read(1),zoom=[InterpolationFactor,InterpolationFactor],order=InterpolationOrder)
            
    return stackBands, DictBandPosition

def readInputDataStack(Version,tuile):
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/VegetationIndex/"+tuile+"/VegetationIndex.tif") as VegetationIndex:
        with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Mask/"+tuile+"/Mask.tif") as Mask:
            return VegetationIndex.read(), Mask.read().astype(bool)
        
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

def ComputeDate(date,DateIndex,DictSentinelPaths,InterpolationOrder,ApplyMaskTheia,BoolSolNu,CompteurSolNu,DateFirstSol,listDiffCRSWIRmedian,CorrectCRSWIR):
    
    MaskTheia=getResampledTheiaMask(DictSentinelPaths[date]) if ApplyMaskTheia else [] #Stack le masque theia si option activée
    stackBands, DictBandPosition = getResampledStack2(DictSentinelPaths[date],["B2","B3","B4","B8A","B11","B12"],InterpolationOrder)
    # print("Stack importé")
    
    SolNu,Ombres,HorsFauche,Invalid = getPreMasks(stackBands, DictBandPosition, MaskTheia, ApplyMaskTheia)

    #COMPUTE SOL NU
    BoolSolNu, CompteurSolNu, DateFirstSol = getSolNu2(BoolSolNu,CompteurSolNu,DateFirstSol,SolNu,Invalid,DateIndex)

    
    #COMPUTE NUAGES
    stackBands=np.ma.array(stackBands, mask = Ombres[:,:,np.newaxis]**[1 for i in range(stackBands.shape[-1])]) #Pas forcément indispensable mais retire erreur
    Nuages2=getNuages2(stackBands,DictBandPosition,HorsFauche,BoolSolNu,SolNu)
    
    # print("Masques calculés")
    
    #COMPUTE SOLYTES
    VegetationIndex=stackBands[:,:,DictBandPosition["B11"]]/(stackBands[:,:,DictBandPosition["B8A"]]+((stackBands[:,:,DictBandPosition["B12"]]-stackBands[:,:,DictBandPosition["B8A"]])/(2185.7-864))*(1610.4-864)) #Calcul du CRSWIR
    
    #CORRECTION DU CRSWIR                
    if CorrectCRSWIR: VegetationIndex=VegetationIndex-listDiffCRSWIRmedian[DateIndex,np.newaxis,np.newaxis]
    
    #APPLICATION DES MASQUES   
    if ApplyMaskTheia : Mask=np.logical_or(np.logical_or(np.logical_or(Ombres, Nuages2),np.logical_or(HorsFauche,MaskTheia)),np.logical_or(BoolSolNu,SolNu)) #Création du masque de pixels invalides avec THEIA
    else : Mask=np.logical_or(np.logical_or(np.logical_or(Ombres, Nuages2),np.logical_or(HorsFauche,BoolSolNu)),SolNu) #Création du masque de pixels invalides sans THEIA
    
    return VegetationIndex ,Mask, BoolSolNu, CompteurSolNu,DateFirstSol