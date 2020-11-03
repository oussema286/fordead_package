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

# Image tile class
class TileImg:
    def __init__(self, DataDirectory, tuile):
        self.tuile = tuile
        self.DataDirectory = DataDirectory

    def getDates(self, dataType):
        """
        Prend en entrée un dossier avec des fichiers nommés sur le modèle ???????_YYYY-MM-JJ.???
        Renvoie un array contenant l'ensemble des dates

        @param datatype <string> date type to check ['VegetationIndex', 'DataAnomalies']
        """
        Dates = getDates(os.path.join(DataDirectory, "VegetationIndex", tuile))
        OldDates = getDates(os.path.join(DataDirectory, "DataAnomalies", tuile))

        AllPaths = glob(os.path.join(self.DataDirectory, dataType, self.tuile, "*"))
        Dates = [Path[-14:-4] for Path in AllPaths]
        return np.array(Dates)

    def ImportMaskedVI(self, date):
        self.VegetationIndex = xr.open_rasterio(self.DataDirectory+"/VegetationIndex/"+self.tuile+"/VegetationIndex_"+date+".tif")
        self.Mask = xr.open_rasterio(self.DataDirectory+"/Mask/"+self.tuile+"/Mask_"+date+".tif").astype(bool)
    
    def ImportModel(self):
        self.StackP = xr.open_rasterio(self.DataDirectory+"/DataModel/"+self.tuile+"/StackP.tif")
        self.rasterSigma = xr.open_rasterio(self.DataDirectory+"/DataModel/"+self.tuile+"/rasterSigma.tif")

    def ImportDataScolytes(self):
        self.BoolEtat = xr.open_rasterio(self.DataDirectory+"/DataUpdate/"+self.tuile+"/EtatChange.tif")
        self.DateFirstScolyte = xr.open_rasterio(self.DataDirectory+"/DataUpdate/"+self.tuile+"/DateFirstScolyte.tif")
        self.CompteurScolyte = xr.open_rasterio(self.DataDirectory+"/DataUpdate/"+self.tuile+"/CompteurScolyte.tif")
        
    def InitializeDataScolytes(self, Shape):
        self.CompteurScolyte = np.zeros(Shape,dtype=np.uint8) #np.int8 possible ?
        self.DateFirstScolyte = np.zeros(Shape,dtype=np.uint16) #np.int8 possible ?
        self.EtatChange=np.zeros(Shape,dtype=bool)

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