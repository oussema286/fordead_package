# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 11:55:14 2020

@author: raphael.dutrieux
"""

from glob import glob
import os
import rasterio
import numpy as np
import fiona ; import fiona.crs
import pandas as pd
import geopandas as gp
import json



def CreateDirectories(OutputDirectory,Tuiles):
    """
    Créer les dossiers nécessaires pour l'écriture des résultats 

    Parameters
    ----------
    Version: str
        Nom de la version
    ExportMasks: bool
        Si True, créer un dossier pour l'export des masques ombres et nuages
    Tuiles: list
        Liste des tuiles calculées

    Returns
    -------
    bool
        True if good
    """
    
    if not(os.path.exists(OutputDirectory+"/DataModel")):
        os.mkdir(OutputDirectory+"/DataModel")
    if not(os.path.exists(OutputDirectory+"/DataUpdate")):
        os.mkdir(OutputDirectory+"/DataUpdate")
    if not(os.path.exists(OutputDirectory+"/DataAnomalies")):
        os.mkdir(OutputDirectory+"/DataAnomalies")
    if not(os.path.exists(OutputDirectory+"/Out")):
        os.mkdir(OutputDirectory+"/Out")
    if not(os.path.exists(OutputDirectory+"/VegetationIndex")):
        os.mkdir(OutputDirectory+"/VegetationIndex")
    if not(os.path.exists(OutputDirectory+"/Mask")):
        os.mkdir(OutputDirectory+"/Mask")
    if not(os.path.exists(OutputDirectory+"/MaskForet")):
        os.mkdir(OutputDirectory+"/MaskForet")
    
    for tuile in Tuiles:
        if not(os.path.exists(OutputDirectory+"/DataModel/"+tuile)):
            os.mkdir(OutputDirectory+"/DataModel/"+tuile)
        # os.mkdir(OutputDirectory+"/DataUpdate/"+tuile)
        if not(os.path.exists(OutputDirectory+"/DataAnomalies/"+tuile)):
            os.mkdir(OutputDirectory+"/DataAnomalies/"+tuile)
        if not(os.path.exists(OutputDirectory+"/DataUpdate/"+tuile)):
            os.mkdir(OutputDirectory+"/DataUpdate/"+tuile)
        if not(os.path.exists(OutputDirectory+"/Out/"+tuile)):
            os.mkdir(OutputDirectory+"/Out/"+tuile)
        if not(os.path.exists(OutputDirectory+"/VegetationIndex/"+tuile)):
            os.mkdir(OutputDirectory+"/VegetationIndex/"+tuile)
        if not(os.path.exists(OutputDirectory+"/Mask/"+tuile)):
            os.mkdir(OutputDirectory+"/Mask/"+tuile)
        # os.mkdir(OutputDirectory+"/Save/"+tuile+"/DateFirstScolyte")
        # os.mkdir(OutputDirectory+"/Save/"+tuile+"/DateFirstSol")
    
        # if ExportMasks:
        #     os.mkdir(OutputDirectory+"/Masques/"+tuile)
    return True


def writeShapefiles(date, Atteint, MaskForet, OutputDirectory, tuile, MetaProfile, CRS_Tuile):
    """
    Ecrit les shapefiles de résultats 

    Parameters
    ----------
    date: list
        Liste des dates
    Atteint: numpy.ndarray
        Numpy (date,x,y) avec les résultats de la détection (0 = sain, 1 = atteint, 2 = coupe, 3 = coupe sanitaire)
    MaskForet: numpy.ndarray
        Masque foret (True si résineux)
    Version: str
        Nom de la version
    tuile: str
        Nom de la tuile
    MetaProfile: rasterio.profiles.Profile
        Metadata du raster pour écriture
    CRS_Tuile: int
        Système de projection de la tuile, numéro d'EPSG
    Overwrite: bool
        Si True, remplace le fichier même si il existe déjà. Utilise lors de la mise à jour.
        
    Returns
    -------
    bool
        True if good
    """
    SchemaAtteint= {'properties': {'Etat': 'int:18'},'geometry': 'Polygon'}
    SchemaMasque={'properties': {'Value': 'int:18'},'geometry': 'Polygon'}
    # TransformBloc=rasterio.Affine(10,0,MetaProfile["transform"][2]+Bornes[y]*10,0,-10,MetaProfile["transform"][5]-Bornes[x]*10)
    
    # for dateIndex in range(np.argmax(Dates>='2018-01-01'),stackAtteint.shape[0]):
    if np.any(Atteint!=0):
        resultsAtteint = (
                    {'properties': {'Etat': v}, 'geometry': s}
                    for i, (s, v) 
                    in enumerate(
                        rasterio.features.shapes(Atteint.astype("uint8"), mask=MaskForet,transform=MetaProfile["transform"])))
        geomsAtteint = list(resultsAtteint)
    
        with fiona.open(OutputDirectory+"/Out/"+tuile+"/Atteint_"+date+".shp", "w",crs=fiona.crs.from_epsg(CRS_Tuile),driver='ESRI Shapefile', schema=SchemaAtteint) as output:
            for poly in geomsAtteint:
                output.write(poly)
    return True


def writeRasters(Atteint, OutputDirectory,tuile,date,MetaProfile):
    
    """
    Ecrit les résultats sous forme de rasters

    Parameters
    ----------
    stackAtteint: numpy.ndarray
        Numpy (date,x,y) avec les résultats de la détection (0 = sain, 1 = atteint, 2 = coupe, 3 = coupe sanitaire)
    FirstDateDiff: int
        Indice de la première date à partir de laquelle les shapefiles seront exportés
    Bornes: list
        Liste des bornes des blocs
    x: int
        Coordonnée en x du bloc
    y: int
        Coordonnée en y du bloc
    Version: str
        Nom de la version
    tuile: str
        Nom de la tuile
    Dates: list
        Liste des dates
    MetaProfile: rasterio.profiles.Profile
        Metadata du raster pour écriture
        
    Returns
    -------
    bool
        True if good
    """
    
    ProfileSave=MetaProfile.copy()
    ProfileSave["dtype"]=Atteint.dtype
    ProfileSave["tiled"]=True
    ProfileSave["nodata"]=5
    with rasterio.open(OutputDirectory+"/Out/"+tuile+"/Atteint_"+date+".tif", "w", nbits=3, **ProfileSave) as dst:
        dst.write(Atteint, indexes=1)
    return True

def writeBinaryRaster(DataArray,Path, MetaProfile):
    
    ProfileSave=MetaProfile.copy()
    ProfileSave["dtype"]=np.uint8
    ProfileSave["tiled"]=True

    with rasterio.open(Path, "w", nbits=1, **ProfileSave) as dst:
        dst.write(DataArray.astype(np.uint8), indexes=1)
        
def writeInputDataDateByDate(VegetationIndex,Mask,MetaProfile,date,OutputDirectory,tuile):
    ProfileSave=MetaProfile.copy()
    ProfileSave["dtype"]=np.float32
    ProfileSave["tiled"]=True
    with rasterio.open(OutputDirectory+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif", "w", nbits=8, **ProfileSave) as dst:
        dst.write(VegetationIndex.astype(np.float32), indexes=1)
    
    writeBinaryRaster(Mask,OutputDirectory+"/Mask/"+tuile+"/Mask_"+date+".tif", MetaProfile)

def writeModel(StackEtat, rasterP, rasterSigma,MetaProfile,Dates,Version,tuile):
    ProfileSave=MetaProfile.copy()
    ProfileSave["dtype"]=np.float32
    ProfileSave["tiled"]=True
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif", "w", nbits=8, **ProfileSave) as dst:
        dst.write(stackCRSWIR.astype(np.float32), indexes=1)
        
    ProfileSave["dtype"]=np.uint8
    ProfileSave["tiled"]=True
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Mask/"+tuile+"/Mask_"+date+".tif", "w", nbits=1, **ProfileSave) as dst:
        dst.write(Invalid2.astype(np.uint8), indexes=1)

  
# def writeInputDataStack(stackCRSWIR,Invalid2,MetaProfile,DateIndex,Version,tuile,Dates):
#     ProfileSave=MetaProfile.copy()
#     ProfileSave["dtype"]=np.float32
#     ProfileSave["tiled"]=True
#     if DateIndex==0:
#         ProfileSave["count"]=Dates.shape[0]
#         with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/VegetationIndex/"+tuile+"/VegetationIndex.tif", "w", **ProfileSave) as dst:
#             EmptyStack=np.empty((Dates.shape[0],stackCRSWIR.shape[0],stackCRSWIR.shape[1]),dtype=np.float32)
#             EmptyStack[0,:,:]=stackCRSWIR
#             dst.write(EmptyStack)
#     else:
#         with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/VegetationIndex/"+tuile+"/VegetationIndex.tif", "r+", **ProfileSave) as dst:
#             dst.write(stackCRSWIR.astype(np.float32),indexes=DateIndex+1)
            
    # ProfileSave["dtype"]=np.uint8
    # ProfileSave["tiled"]=True
    # if DateIndex==0:
    #     ProfileSave["count"]=Dates.shape[0]
    #     with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Mask/"+tuile+"/Mask.tif", "w", **ProfileSave) as dst:
    #         EmptyStack=np.empty((Dates.shape[0],stackCRSWIR.shape[0],stackCRSWIR.shape[1]),dtype=np.uint8)
    #         EmptyStack[0,:,:]=Invalid2
    #         dst.write(EmptyStack)
    # else:
    #     with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Mask/"+tuile+"/Mask.tif", "r+", **ProfileSave) as dst:
    #         dst.write(Invalid2.astype(np.uint8),indexes=DateIndex+1)

