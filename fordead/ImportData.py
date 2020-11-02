# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:42:31 2020

@author: admin
"""

import rasterio
from glob import glob
import os
import numpy as np

def getDates(DirectoryPath):
    """
    Prend en entrée un dossier avec des fichiers nommés sur le modèle ???????_YYYY-MM-JJ.???
    Renvoie un array contenant l'ensemble des dates
    """

    AllPaths=glob(os.path.join(DirectoryPath,"*"))
    Dates=[Path[-14:-4] for Path in AllPaths]
    return np.array(Dates)

def ImportMaskedVI(DataDirectory,tuile,date):
    with rasterio.open(DataDirectory+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif") as rasterVegetationIndex:
        VegetationIndex=rasterVegetationIndex.read(1)
    with rasterio.open(DataDirectory+"/Mask/"+tuile+"/Mask_"+date+".tif") as rasterMask:
        Mask=rasterMask.read(1).astype(bool)
    
    return VegetationIndex, Mask

def ImportModel(tuile,DataDirectory):
        
    with rasterio.open(DataDirectory+"/DataModel/"+tuile+"/StackP.tif") as src: 
        StackP = src.read()
    with rasterio.open(DataDirectory+"/DataModel/"+tuile+"/rasterSigma.tif") as src: 
        rasterSigma = src.read(1)
    
    return StackP,rasterSigma

def ImportDataScolytes(tuile,DataDirectory):
    
    with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/EtatChange.tif") as rasterEtatChange:
        EtatChange=rasterEtatChange.read(1).astype(bool)
    with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/DateFirstScolyte.tif") as rasterDateFirstScolyte:
        DateFirstScolyte=rasterDateFirstScolyte.read(1)
    with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/CompteurScolyte.tif") as rasterCompteurScolyte:
        CompteurScolyte=rasterCompteurScolyte.read(1)
        
def InitializeDataScolytes(tuile,DataDirectory,Shape):
    CompteurScolyte= np.zeros(Shape,dtype=np.uint8) #np.int8 possible ?
    DateFirstScolyte=np.zeros(Shape,dtype=np.uint16) #np.int8 possible ?
    EtatChange=np.zeros(Shape,dtype=bool)
    
    return EtatChange,DateFirstScolyte,CompteurScolyte

def ImportMaskForet(PathMaskForet):
    with rasterio.open(PathMaskForet) as BDFORET: 
        RasterizedBDFORET = BDFORET.read(1).astype("bool")
        profile = BDFORET.profile
        CRS_Tuile = int(str(profile["crs"])[5:])
    return RasterizedBDFORET,profile,CRS_Tuile