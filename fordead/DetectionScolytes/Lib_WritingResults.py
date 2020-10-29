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




def sortVersion(version):
    """
    Extrait le numéro d'une version à partir du chemin d'un dossier de version, utilisé pour trier les versions existantes dans la fonction getVersion 

    Parameters
    ----------
    version: str
        Path of the directory of an existing version

    Returns
    -------
    int
        Number of version as integer
    """
    return int(version.split("V")[-1])

def getVersion():
    """
    Vérifie les versions existantes pour donner le numéro de la nouvelle version

    Returns
    -------
    int
        Numéro de la nouvelle version 
    """
    if not(os.path.exists(os.getcwd()+"/Out/Results")):
        Version=1
    elif glob(os.getcwd()+"/Out/Results/"+"*")==[]:
        Version=1
    else:
        Version=int(sorted(glob(os.getcwd()+"/Out/Results/"+"*"),key=sortVersion)[-1].split("V")[-1])+1
    return Version

def CreateDirectories(DataDirectory,Tuiles):
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
    
    if not(os.path.exists(DataDirectory+"/DataModel")):
        os.mkdir(DataDirectory+"/DataModel")
    if not(os.path.exists(DataDirectory+"/DataUpdate")):
        os.mkdir(DataDirectory+"/DataUpdate")
    if not(os.path.exists(DataDirectory+"/DataAnomalies")):
        os.mkdir(DataDirectory+"/DataAnomalies")
    if not(os.path.exists(DataDirectory+"/Out")):
        os.mkdir(DataDirectory+"/Out")
    if not(os.path.exists(DataDirectory+"/VegetationIndex")):
        os.mkdir(DataDirectory+"/VegetationIndex")
    if not(os.path.exists(DataDirectory+"/Mask")):
        os.mkdir(DataDirectory+"/Mask")
    
    for tuile in Tuiles:
        if not(os.path.exists(DataDirectory+"/DataModel/"+tuile)):
            os.mkdir(DataDirectory+"/DataModel/"+tuile)
        # os.mkdir(DataDirectory+"/DataUpdate/"+tuile)
        if not(os.path.exists(DataDirectory+"/DataAnomalies/"+tuile)):
            os.mkdir(DataDirectory+"/DataAnomalies/"+tuile)
        if not(os.path.exists(DataDirectory+"/DataUpdate/"+tuile)):
            os.mkdir(DataDirectory+"/DataUpdate/"+tuile)
        if not(os.path.exists(DataDirectory+"/Out/"+tuile)):
            os.mkdir(DataDirectory+"/Out/"+tuile)
        if not(os.path.exists(DataDirectory+"/VegetationIndex/"+tuile)):
            os.mkdir(DataDirectory+"/VegetationIndex/"+tuile)
        if not(os.path.exists(DataDirectory+"/Mask/"+tuile)):
            os.mkdir(DataDirectory+"/Mask/"+tuile)
        # os.mkdir(DataDirectory+"/Save/"+tuile+"/DateFirstScolyte")
        # os.mkdir(DataDirectory+"/Save/"+tuile+"/DateFirstSol")
    
        # if ExportMasks:
        #     os.mkdir(DataDirectory+"/Masques/"+tuile)
    return True


def writeShapefiles(date, Atteint, MaskForet, DataDirectory, tuile, MetaProfile, CRS_Tuile):
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
    
        with fiona.open(DataDirectory+"/Out/"+tuile+"/Atteint_"+date+".shp", "w",crs=fiona.crs.from_epsg(CRS_Tuile),driver='ESRI Shapefile', schema=SchemaAtteint) as output:
            for poly in geomsAtteint:
                output.write(poly)
    return True


def writeRasters(Atteint, DataDirectory,tuile,date,MetaProfile):
    
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
    with rasterio.open(DataDirectory+"/Out/"+tuile+"/Atteint_"+date+".tif", "w", nbits=3, **ProfileSave) as dst:
        dst.write(Atteint, indexes=1)
    return True

         
def writeResultObs(RasterizedScolytesTerrain,stackAtteint,stackCRSWIR,stackPredictedCRSWIR,stackDiff,stackStress, NbStressPeriod, NbAnomalies, Bornes, x, y, Version, Dates):
    
    """
    Ecrit les résultats au niveau des données d'observation terrain sous forme d'un .csv

    Parameters
    ----------
    RasterizedScolytesTerrain: numpy.ndarray
        Numpy avec pour chaque pixel l'identifiant de l'observation terrain, 0 sinon
    stackAtteint: numpy.ndarray
        Numpy (date,x,y) avec les résultats de la détection (0 = sain, 1 = atteint, 2 = coupe, 3 = coupe sanitaire)
    stackCRSWIR: numpy.ma.core.MaskedArray
        Masked numpy (date,x,y) avec la valeur du CRSWIR pour chaque pixel
    stackPredictedCRSWIR: numpy.ndarray
        Numpy (date,x,y) avec la valeur du CRSWIR prédit pour chaque pixel
    stackDiff: numpy.ndarray
        Numpy (date,x,y) avec l'écart type de la différence entre le CRSWIR et le CRSWIR prédit pour chaque pixel
    stackStress: numpy.ndarray
        Numpy (date,x,y) de type bool avec True si le pixel est déterminé comme en état de stress à cette date (Ne marche qu'à partir de la troisième date valide)
    NbStressPeriod: numpy.ndarray
        Numpy (x,y) avec le nombre de périodes de stress de chaque pixel
    NbAnomalies: numpy.ndarray
        Numpy (x,y) avec le nombre de dates avec anomalies pour chaque pixel
    Bornes: list
        Liste des bornes des blocs
    x: int
        Coordonnée en x du bloc
    y: int
        Coordonnée en y du bloc
    Version: str
        Nom de la version
    Dates: list
        Liste des dates
        
    Returns
    -------
    bool
        True if good
    """
    
    RasterizedScolytesTerrainZone = RasterizedScolytesTerrain[Bornes[x]:Bornes[x+1],Bornes[y]:Bornes[y+1]]!=0
    if np.any(RasterizedScolytesTerrainZone):
            for dateIndex in range(stackAtteint.shape[0]):
                
                AtteintList=stackAtteint[dateIndex,:,:][RasterizedScolytesTerrainZone]
                d1 = {'IdZone': RasterizedScolytesTerrain[Bornes[x]:Bornes[x+1],Bornes[y]:Bornes[y+1]][RasterizedScolytesTerrainZone],
                      "IdZoneXY" : [str(x)+str(y)]*AtteintList.shape[0],
                      "IdPixel" : range(AtteintList.shape[0]),
                      "Date" : [Dates[dateIndex]]*AtteintList.shape[0],
                      'Etat': AtteintList,
                      "CRSWIR" : stackCRSWIR[dateIndex,:,:][RasterizedScolytesTerrainZone].data,
                      "Mask" : stackCRSWIR[dateIndex,:,:][RasterizedScolytesTerrainZone].mask,
                      "PredictedCRSWIR" : stackPredictedCRSWIR[dateIndex,:,:][RasterizedScolytesTerrainZone],
                      "DiffSeuil" : stackDiff[dateIndex,:,:][RasterizedScolytesTerrainZone],
                      "EtatStress" : stackStress[dateIndex,:,:][RasterizedScolytesTerrainZone]}
                
                Results = pd.DataFrame(data=d1)
                Results.to_csv(os.getcwd()+"/Out/Results/"+'V'+Version+'/ResultsTable.csv', mode='a', index=False,header=not(os.path.exists(os.getcwd()+"/Out/Results/"+'V'+Version+'/ResultsTable.csv')))
           
            d2 = {'IdZone': RasterizedScolytesTerrain[Bornes[x]:Bornes[x+1],Bornes[y]:Bornes[y+1]][RasterizedScolytesTerrainZone],
                  "IdZoneXY" : [str(x)+str(y)]*AtteintList.shape[0],
                  "IdPixel" : range(AtteintList.shape[0]),
                  "NbStressperiod" : NbStressPeriod[RasterizedScolytesTerrainZone],
                  "NbAnomalies" : NbAnomalies[RasterizedScolytesTerrainZone]}
            
            Results2 = pd.DataFrame(data=d2)
            Results2.to_csv(os.getcwd()+"/Out/Results/"+'V'+Version+'/ResultsStress.csv', mode='a', index=False,header=not(os.path.exists(os.getcwd()+"/Out/Results/"+'V'+Version+'/ResultsStress.csv')))
    return True
            
def JoinBlocs(Dates, Version, tuile, ExportMasks):
    
    
    """
    Dissous les shapefiles des différents blocs pour supprimer le quadrillage en blocs (à améliorer)

    Parameters
    ----------
    Dates: list
        Liste des dates
    Version: str
        Nom de la version
    tuile: str
        Nom de la tuile
    ExportMasks: bool
        Si True, dissous également les shapefiles des masques ombres et nuages
        
    Returns
    -------
    bool
        True if good
    """
    
    for date in Dates:
        if os.path.exists(os.getcwd()+"/Out/Results/"+"V"+Version+"/Atteint/"+tuile+"/Atteint_"+date+".shp"):     
            AtteintTot=gp.read_file(os.getcwd()+"/Out/Results/"+"V"+Version+"/Atteint/"+tuile+"/Atteint_"+date+".shp")
            AtteintTot=AtteintTot.dissolve(by='Etat')
            AtteintTot.index.name = 'Etat'
            AtteintTot.reset_index(inplace=True)
            AtteintTot.to_file(os.getcwd()+"/Out/Results/"+"V"+Version+"/Atteint/"+tuile+"/Atteint_"+date+".shp")
        if ExportMasks:
            if os.path.exists(os.getcwd()+"/Out/Results/"+"V"+Version+"/Masques/"+tuile+"/Nuages_"+date+".shp"):      
                NuagesTot=gp.read_file(os.getcwd()+"/Out/Results/"+"V"+Version+"/Masques/"+tuile+"/Nuages_"+date+".shp")
                NuagesTot=NuagesTot.dissolve(by='Value')
                NuagesTot.index.name = 'Value'
                NuagesTot.reset_index(inplace=True)
                NuagesTot.to_file(os.getcwd()+"/Out/Results/"+"V"+Version+"/Masques/"+tuile+"/Nuages_"+date+".shp")
                
            if os.path.exists(os.getcwd()+"/Out/Results/"+"V"+Version+"/Masques/"+tuile+"/Ombres_"+date+".shp"):      
                OmbresTot=gp.read_file(os.getcwd()+"/Out/Results/"+"V"+Version+"/Masques/"+tuile+"/Ombres_"+date+".shp")
                OmbresTot=OmbresTot.dissolve(by='Value')
                OmbresTot.index.name = 'Value'
                OmbresTot.reset_index(inplace=True)
                OmbresTot.to_file(os.getcwd()+"/Out/Results/"+"V"+Version+"/Masques/"+tuile+"/Ombres_"+date+".shp")
    return True

def getRasterizedScolytesTerrain(tuile, CRS_Tuile, ValidationObs, MetaProfile):
    
    """
    Errode les vecteurs d'observations terrain de la tuile puis les transforme en raster avec comme valeur l'identifiant du polygone. 
    
    
    Parameters
    ----------
    
    tuile: str
        Nom de la tuile
    CRS_Tuile: int
        Système de projection de la tuile, numéro d'EPSG
    ValidationObs: bool
        Si True, garde les observations non validées et effectue une dilation plutôt qu'une érosion. Permet d'effectuer les calculs sur les observations non validées afin de créer les timelapses et les valider manuellement.
    MetaProfile: rasterio.profiles.Profile
        Metadata du raster pour écriture
        
    Returns
    -------
    numpy.ndarray
        Observations rasterisées
    """
    
        #Rasterize données terrain
    if os.path.exists(os.getcwd()+"/Data/Vecteurs/ObservationsTerrain/"+"scolyte"+tuile[1:]+".shp"):
        ScolytesTerrain=gp.read_file(os.getcwd()+"/Data/Vecteurs/ObservationsTerrain/"+"scolyte"+tuile[1:]+".shp")
        ScolytesTerrain=ScolytesTerrain.to_crs(epsg=CRS_Tuile)
        
        if ValidationObs:
            ScolytesTerrain['geometry']=ScolytesTerrain.geometry.buffer(10) #Buffer pour avoir au moins un pixel et que l'observation ne soit pas sautée
        else:
            ScolytesTerrain['geometry']=ScolytesTerrain.geometry.buffer(-10)
            ScolytesTerrain=ScolytesTerrain[~(ScolytesTerrain.is_empty)]
            ScolytesTerrain=ScolytesTerrain[ScolytesTerrain["IndSur"]==1]
            
        ScolytesTerrain_json_str = ScolytesTerrain.to_json()
        ScolytesTerrain_json_dict = json.loads(ScolytesTerrain_json_str)
        ScolytesTerrain_jsonMask = [(feature["geometry"],feature["properties"]["Id"]) for feature in ScolytesTerrain_json_dict["features"]]
        return rasterio.features.rasterize(ScolytesTerrain_jsonMask,out_shape = (MetaProfile["width"],MetaProfile["height"]) ,dtype="int16",transform=MetaProfile['transform'])
    else:
        return np.zeros((MetaProfile["width"],MetaProfile["height"]),dtype="uint8")
    
def writeInputDataDateByDate(stackCRSWIR,Invalid2,MetaProfile,date,DataDirectory,tuile):
    ProfileSave=MetaProfile.copy()
    ProfileSave["dtype"]=np.float32
    ProfileSave["tiled"]=True
    with rasterio.open(DataDirectory+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif", "w", nbits=8, **ProfileSave) as dst:
        dst.write(stackCRSWIR.astype(np.float32), indexes=1)
        
    ProfileSave["dtype"]=np.uint8
    ProfileSave["tiled"]=True
    with rasterio.open(DataDirectory+"/Mask/"+tuile+"/Mask_"+date+".tif", "w", nbits=1, **ProfileSave) as dst:
        dst.write(Invalid2.astype(np.uint8), indexes=1)
        
def writeInputDataStack(stackCRSWIR,Invalid2,MetaProfile,DateIndex,Version,tuile,Dates):
    ProfileSave=MetaProfile.copy()
    ProfileSave["dtype"]=np.float32
    ProfileSave["tiled"]=True
    if DateIndex==0:
        ProfileSave["count"]=Dates.shape[0]
        with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/VegetationIndex/"+tuile+"/VegetationIndex.tif", "w", **ProfileSave) as dst:
            EmptyStack=np.empty((Dates.shape[0],stackCRSWIR.shape[0],stackCRSWIR.shape[1]),dtype=np.float32)
            EmptyStack[0,:,:]=stackCRSWIR
            dst.write(EmptyStack)
    else:
        with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/VegetationIndex/"+tuile+"/VegetationIndex.tif", "r+", **ProfileSave) as dst:
            dst.write(stackCRSWIR.astype(np.float32),indexes=DateIndex+1)
            
    ProfileSave["dtype"]=np.uint8
    ProfileSave["tiled"]=True
    if DateIndex==0:
        ProfileSave["count"]=Dates.shape[0]
        with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Mask/"+tuile+"/Mask.tif", "w", **ProfileSave) as dst:
            EmptyStack=np.empty((Dates.shape[0],stackCRSWIR.shape[0],stackCRSWIR.shape[1]),dtype=np.uint8)
            EmptyStack[0,:,:]=Invalid2
            dst.write(EmptyStack)
    else:
        with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Mask/"+tuile+"/Mask.tif", "r+", **ProfileSave) as dst:
            dst.write(Invalid2.astype(np.uint8),indexes=DateIndex+1)

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
