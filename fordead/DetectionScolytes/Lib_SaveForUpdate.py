# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 18:11:40 2020

@author: admin
"""

import rasterio
import os
import numpy as np
import pickle
from glob import glob

def ImportForUpdate(tuile,DataDirectory):
    # with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/DataUpdate/"+tuile+"/BoolSolNu.tif") as rasterBoolSolNu:
    #     BoolSolNu=rasterBoolSolNu.read(1).astype(bool)
    # with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/DataUpdate/"+tuile+"/DateFirstSolNu.tif") as rasterDateFirstSolNu:
    #     DateFirstSolNu=rasterDateFirstSolNu.read(1)
    # with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/DataUpdate/"+tuile+"/CompteurSolNu.tif") as rasterCompteurSolNu:
    #     CompteurSolNu=rasterCompteurSolNu.read(1)
        
    with rasterio.open(DataDirectory+"/DataModel/"+tuile+"/StackP.tif") as src: 
        StackP = src.read()
    with rasterio.open(DataDirectory+"/DataModel/"+tuile+"/rasterSigma.tif") as src: 
        rasterSigma = src.read(1)
        
    #Load them
    if os.path.exists(DataDirectory+"/DataUpdate/"+tuile+"/EtatChange.tif"):
        with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/EtatChange.tif") as rasterEtatChange:
            EtatChange=rasterEtatChange.read(1).astype(bool)
        with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/DateFirstScolyte.tif") as rasterDateFirstScolyte:
            DateFirstScolyte=rasterDateFirstScolyte.read(1)
        with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/CompteurScolyte.tif") as rasterCompteurScolyte:
            CompteurScolyte=rasterCompteurScolyte.read(1)
    else:
        CompteurScolyte= np.zeros_like(rasterSigma,dtype=np.uint8) #np.int8 possible ?
        DateFirstScolyte=np.zeros_like(rasterSigma,dtype=np.uint16) #np.int8 possible ?
        EtatChange=np.zeros_like(rasterSigma,dtype=bool)
    
    return StackP,rasterSigma,EtatChange,DateFirstScolyte,CompteurScolyte

    
def SaveDataUpdateSolNu(BoolSolNu,DateFirstSolNu, CompteurSolNu, MetaProfile, Version, tuile):
    
    ProfileSave=MetaProfile.copy()    
    ProfileSave["dtype"]=np.uint8

    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/DataUpdate/"+tuile+"/BoolSolNu.tif", 'w', nbits=1, **ProfileSave) as dst:
        dst.write(BoolSolNu.astype(np.uint8),indexes=1)
    
    ProfileSave["dtype"]=DateFirstSolNu.dtype
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/DataUpdate/"+tuile+"/DateFirstSolNu.tif", 'w', **ProfileSave) as dst:
        dst.write(DateFirstSolNu,indexes=1)
    
    ProfileSave["dtype"]=CompteurSolNu.dtype
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/DataUpdate/"+tuile+"/CompteurSolNu.tif", 'w', **ProfileSave) as dst:
        dst.write(CompteurSolNu,indexes=1)
        
    return True

def SaveDataUpdateScolytes(EtatChange,DateFirstScolyte, CompteurScolyte, MetaProfile, DataDirectory, tuile):
    
    ProfileSave=MetaProfile.copy()    
    ProfileSave["dtype"]=np.uint8

    with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/EtatChange.tif", 'w', nbits=1, **ProfileSave) as dst:
        dst.write(EtatChange.astype(np.uint8),indexes=1)
    
    ProfileSave["dtype"]=DateFirstScolyte.dtype
    with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/DateFirstScolyte.tif", 'w', **ProfileSave) as dst:
        dst.write(DateFirstScolyte,indexes=1)
    
    ProfileSave["dtype"]=CompteurScolyte.dtype
    with rasterio.open(DataDirectory+"/DataUpdate/"+tuile+"/CompteurScolyte.tif", 'w', **ProfileSave) as dst:
        dst.write(CompteurScolyte,indexes=1)
        
    return True
def SaveDataModel(rasterP,rasterSigma, MetaProfile, tuile, DataDirectory):
    
    ProfileSave=MetaProfile.copy()    
    ProfileSave["dtype"]=rasterSigma.dtype
    ProfileSave["count"]=1
    with rasterio.open(DataDirectory+"/DataModel/"+tuile+"/rasterSigma.tif", 'w', **ProfileSave) as dst:
        dst.write(rasterSigma,indexes=1)
        
    ProfileSave["dtype"]=rasterP.dtype
    ProfileSave["count"]=5
    with rasterio.open(DataDirectory+"/DataModel/"+tuile+"/StackP.tif", 'w', **ProfileSave) as dst:
        dst.write(rasterP)
        
    return True

def SaveDataAnomalies(Anomalies,date,MetaProfile, DataDirectory, tuile):
    ProfileSave=MetaProfile.copy()    
    ProfileSave["dtype"]=np.uint8

    with rasterio.open(DataDirectory+"/DataAnomalies/"+tuile+"/Anomalies_"+date+".tif", 'w', nbits=1, **ProfileSave) as dst:
        dst.write(Anomalies.astype(np.uint8),indexes=1)
        
def SaveData(BoolSolNu,DateFirstSolNu, CompteurSolNu,rasterP,rasterSigma, Dates,MetaProfile, Version, tuile):
    
    SaveDataUpdateSolNu(BoolSolNu,DateFirstSolNu, CompteurSolNu, MetaProfile, Version, tuile)
    SaveDataModel(rasterP,rasterSigma, MetaProfile, Version, tuile)

    with open(os.getcwd()+"/Out/Results/"+"V"+Version+"/DataUpdate/"+tuile+"/Dates", 'wb') as f:
        pickle.dump(Dates, f)
        
def OverwriteUpdate(tuile,DataDirectory):
    Files = glob(DataDirectory+"/DataAnomalies/"+tuile+"/*") + glob(DataDirectory+"/DataUpdate/"+tuile+"/*") + glob(DataDirectory+"/Out/"+tuile+"/*")
    for file in Files:
        os.remove(file)

def SaveForUpdate2(stackDetected, stackSolNu ,rasterP,rasterSigma, DateFirstScolyte, DateFirstSol, CompteurScolyte, CompteurSolNu, Dates, MetaProfile, Bornes, x ,y, Version, tuile,Overwrite):
    
    """
    Ecrit l'ensemble des éléments à sauvegarder pour rendre possible la mise à jour à partir de nouvelles dates
    
    Parameters
    ----------
    stackDetected: (Dates,X,Y) ndarray de type bool
        Si True, pixel détecté comme atteint à cette date
    stackSolNu : (Dates,x,y) ndarray de type bool
        Si True, pixel détecté comme sol nu à cette date
    rasterP : (5,x,y) ndarray
        ndarray avec la valeur des coefficients pour la modélisation du CRSWIR pour chaque pixel
    rasterSigma: (x,y) ndarray
        ndarray avec la valeur du seuil pour la détection d'anomalies pour chaque pixel
    DateFirstScolyte: (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série d'anomalies de la dernière mise à jour.
    DateFirstSol : (x,y) ndarray
        ndarray avec comme valeur la première date de la dernière série où le pré-masque SolNu valait True lors de la dernière mise à jour.
    CompteurScolyte: (x,y) ndarray
        Compteur du nombre de dates succesives d'anomalies au moment de la dernière date SENTINEL-2 de la dernière mise à jour.
    CompteurSolNu : (x,y) ndarray
        Compteur du nombre de dates succesives où le pré-masque SolNu vaut True au moment de la dernière date SENTINEL-2 de la dernière mise à jour.
    Dates: ndarray
        Array des dates valides au format "AAAA-MM-JJ"
    MetaProfile:  rasterio.profiles.Profile
        Métadonnées de raster pour écriture
    Bornes: list
        Liste des bornes des blocs
    x: int
        Coordonnée en x du bloc
    y: int
        Coordonnée en y du bloc
    Version: str
        Nom de la version
    tuile: str
        Nom de la tuile concernée
    Overwrite: bool
        True lors de la mise à jour pour réecriture
    Returns
    -------
    bool
        True if good
    """
    write_window=rasterio.windows.Window.from_slices((Bornes[x], Bornes[x+1]), (Bornes[y], Bornes[y+1]))

    ProfileSave=MetaProfile.copy()
    ProfileSave["dtype"]=np.uint8
    ProfileSave["count"]=stackDetected.shape[0]
    ProfileSave["tiled"]=True

    
    if not(os.path.isfile(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/StackAtteint/StackDetected.tif")) or Overwrite:
        writingMode="w"
    else:
        writingMode="r+"
    
#    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Atteint/"+tuile+"/Atteint_"+Dates[dateIndex]+".tif", writingMode, nbits=2, **ProfileSave) as dst:
#        dst.write(stackAtteint[dateIndex,:,:], indexes=1, window=write_window)
                
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/StackAtteint/StackDetected.tif", writingMode, nbits=1, **ProfileSave) as dst:
        dst.write(stackDetected.astype(np.uint8), window=write_window)
    
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/StackAtteint/StackSolNu.tif", writingMode, nbits=1, **ProfileSave) as dst:
        dst.write(stackSolNu.astype(np.uint8), window=write_window)
    
    if type(rasterP)!=bool: #Si update
    
        ProfileSave["dtype"]=rasterSigma.dtype
        ProfileSave["count"]=1
        with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/rasterSigma/rasterSigma.tif", writingMode, **ProfileSave) as dst:
            dst.write(rasterSigma,indexes=1, window=write_window)
            
        ProfileSave["dtype"]=rasterP.dtype
        ProfileSave["count"]=5
        with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/StackP/StackP.tif", writingMode, **ProfileSave) as dst:
            dst.write(rasterP, window=write_window)
    
    ProfileSave["dtype"]=DateFirstScolyte.dtype
    ProfileSave["count"]=1
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/DateFirstScolyte/DateFirstScolyte.tif", writingMode, **ProfileSave) as dst:
        dst.write(DateFirstScolyte,indexes=1, window=write_window)
    
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/DateFirstSol/DateFirstSol.tif", writingMode, **ProfileSave) as dst:
        dst.write(DateFirstSol,indexes=1, window=write_window)
        
    ProfileSave["dtype"]=CompteurScolyte.dtype
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/DateFirstSol/CompteurSolNu.tif", writingMode, **ProfileSave) as dst:
        dst.write(CompteurSolNu,indexes=1, window=write_window)
    
    with rasterio.open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/DateFirstScolyte/CompteurScolyte.tif", writingMode, **ProfileSave) as dst:
        dst.write(CompteurScolyte,indexes=1, window=write_window)
    
    with open(os.getcwd()+"/Out/Results/"+"V"+Version+"/Save/"+tuile+"/Dates", 'wb') as f:
        pickle.dump(Dates, f)
    return True