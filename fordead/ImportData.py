# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:42:31 2020

@author: admin
"""

# import rasterio
from glob import glob
import os
import numpy as np
import xarray as xr

def getDates(DirectoryPath):
    """
    Prend en entrée un dossier avec des fichiers nommés sur le modèle ???????_YYYY-MM-JJ.???
    Renvoie un array contenant l'ensemble des dates
    """
    AllPaths=glob(os.path.join(DirectoryPath,"*"))
    Dates=[Path[-14:-4] for Path in AllPaths]
    return np.array(Dates)

def ImportMaskedVI(DataDirectory,tuile,date):
    VegetationIndex = xr.open_rasterio(DataDirectory+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif")
    Mask=xr.open_rasterio(DataDirectory+"/Mask/"+tuile+"/Mask_"+date+".tif").astype(bool)
    return VegetationIndex, Mask
    
def ImportModel(tuile,DataDirectory):
    StackP = xr.open_rasterio(DataDirectory+"/DataModel/"+tuile+"/StackP.tif")
    rasterSigma = xr.open_rasterio(DataDirectory+"/DataModel/"+tuile+"/rasterSigma.tif")
    return StackP,rasterSigma

def ImportDataScolytes(tuile,DataDirectory):
    BoolEtat = xr.open_rasterio(DataDirectory+"/DataUpdate/"+tuile+"/EtatChange.tif")
    DateFirstScolyte = xr.open_rasterio(DataDirectory+"/DataUpdate/"+tuile+"/DateFirstScolyte.tif")
    CompteurScolyte = xr.open_rasterio(DataDirectory+"/DataUpdate/"+tuile+"/CompteurScolyte.tif")
    
    return BoolEtat, DateFirstScolyte, CompteurScolyte
        
def InitializeDataScolytes(tuile,DataDirectory,Shape):
    CompteurScolyte= np.zeros(Shape,dtype=np.uint8) #np.int8 possible ?
    DateFirstScolyte=np.zeros(Shape,dtype=np.uint16) #np.int8 possible ?
    EtatChange=np.zeros(Shape,dtype=bool)
    
    return EtatChange,DateFirstScolyte,CompteurScolyte

def ImportMaskForet(PathMaskForet):
    MaskForet = xr.open_rasterio(PathMaskForet)
    return MaskForet.astype(bool)

# def ImportMaskForet(PathMaskForet):
#     MaskForet = xr.open_rasterio(PathMaskForet)
#     with rasterio.open(PathMaskForet) as BDFORET: 
#         RasterizedBDFORET = BDFORET.read(1).astype("bool")
#         profile = BDFORET.profile
#         CRS_Tuile = int(str(profile["crs"])[5:])
#     return RasterizedBDFORET,profile,CRS_Tuile