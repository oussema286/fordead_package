# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 12:06:31 2020

@author: raphael.dutrieux
"""


#%% =============================================================================
#   LIBRAIRIES
# =============================================================================

import os, sys
import numpy as np
import argparse
import rasterio


# %%=============================================================================
#  IMPORT LIBRAIRIES PERSO
# =============================================================================

from Lib_WritingResults import writeShapefiles, writeRasters
from Lib_ImportValidSentinelData import getDates, getOldDates
from Lib_ComputeMasks import getMaskForet
from Lib_DetectionUpdating import DetectAnomalies, DetectScolytes
from Lib_SaveForUpdate import SaveDataAnomalies, SaveDataUpdateScolytes, ImportForUpdate, OverwriteUpdate

# %%=============================================================================
#     DEFINITION PARAMETRES
# =============================================================================
    
def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--Tuiles', nargs='+',default=["ZoneTest"],help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("-s", "--SeuilMin", dest = "SeuilMin",type = float,default = 0.04, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-a", "--CoeffAnomalie", dest = "CoeffAnomalie",type = float,default = 4, help = "Coefficient multiplicateur du seuil de détection d'anomalies")
    parser.add_argument("-x", "--ExportAsShapefile", dest = "ExportAsShapefile", action="store_true",default = False, help = "Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")
    parser.add_argument("-d", "--DataDirectory", dest = "DataDirectory",type = str,default = "G:/Deperissement/Code/Python/fordead_package/fordead/tests/OutputFordead", help = "Dossier avec les données")
    parser.add_argument("-o", "--Overwrite", dest = "Overwrite", action="store_true",default = False, help = "Si vrai, recommence la détection du début. Sinon, reprends de la dernière date analysée")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs



# %%=============================================================================
# MAIN CODE
# =============================================================================

def DetectionScolytes(
    Tuiles= ["ZoneTest"],
    SeuilMin=0.04,
    CoeffAnomalie=4,
    ExportAsShapefile = False,
    DataDirectory = "G:/Deperissement/Out/PackageVersion",
    Overwrite=False
    ):

    for tuile in Tuiles:
        # start_time_debut=time.time()
        print("Tuile : " + tuile)
        # TimeDetectDeperissement=0 ; TimeComputeDate=0 ; TimeWriteInputData=0; TimeDetectAnomalies=0
        # DictSentin1elPaths = getSentinelPaths(tuile,"3000-01-01",DataSource) #Récupération de l'ensemble des dates avant la date de fin d'apprentissage, associées aux chemins de chaque bande SENTINEL-2
        # Dates = getValidDates(DictSentinelPaths,tuile, PercNuageLim,DataSource)
    
        if Overwrite: OverwriteUpdate(tuile,DataDirectory)
    
        Dates=getDates(tuile,DataDirectory)
        DateFirstTested=np.where(Dates==Dates[Dates>="2018-01-01"][0])[0][0]
        OldDates=getOldDates(tuile,DataDirectory)
        
        if OldDates.shape[0]==Dates[DateFirstTested:].shape[0]:
            print("Pas de nouvelles dates SENTINEL-2")
            continue
        else:
            print(str(Dates[DateFirstTested:].shape[0]-OldDates.shape[0])+ " nouvelles dates")
        
        #RASTERIZE MASQUE FORET
        MaskForet,MetaProfile,CRS_Tuile = getMaskForet(os.path.join(DataDirectory,"MaskForet",tuile+"_MaskForet.tif"))
      
        #INITIALISATION
        StackP,rasterSigma,EtatChange,DateFirstScolyte,CompteurScolyte = ImportForUpdate(tuile,DataDirectory)
        rasterSigma[rasterSigma<SeuilMin]=SeuilMin
        
        # TimeInitialisation=time.time() - start_time_debut
        
        print("Détection du déperissement")
        
        for DateIndex,date in enumerate(Dates):
            
            if date < "2018-01-01" or os.path.exists(DataDirectory+"/DataAnomalies/"+tuile+"/Anomalies_"+date+".tif"):
                continue
            else:
                # start_time = time.time()
                with rasterio.open(DataDirectory+"/VegetationIndex/"+tuile+"/VegetationIndex_"+date+".tif") as rasterVegetationIndex:
                    VegetationIndex=rasterVegetationIndex.read(1)
                with rasterio.open(DataDirectory+"/Mask/"+tuile+"/Mask_"+date+".tif") as rasterMask:
                    Mask=rasterMask.read(1).astype(bool)
                # TimeComputeDate+= time.time() - start_time ; start_time = time.time() ; start_time = time.time()
    
            
            Anomalies = DetectAnomalies(VegetationIndex, StackP, rasterSigma, CoeffAnomalie, date)
            SaveDataAnomalies(Anomalies,date,MetaProfile, DataDirectory, tuile)
            # TimeDetectAnomalies += time.time() - start_time
            
            # start_time = time.time()
            CompteurScolyte,DateFirstScolyte, EtatChange = DetectScolytes(CompteurScolyte,DateFirstScolyte, EtatChange, Anomalies, Mask, DateIndex)
            
            # TimeDetectDeperissement += time.time() - start_time
            
        # start_time = time.time()
        # SaveDataUpdateSolNu(BoolSolNu,DateFirstSolNu, CompteurSolNu, MetaProfile, Version, tuile)
        print("Sauvegarde des données intermediaires")
        SaveDataUpdateScolytes(EtatChange,DateFirstScolyte, CompteurScolyte, MetaProfile, DataDirectory, tuile)
    
        # TimeWriteDataUpdate=time.time() - start_time ; start_time = time.time()
        # print("Détection du déperissement : %s secondes ---" % (time.time() - start_time_debut))
        print("Ecriture des résultats")
        for DateIndex,date in enumerate(Dates):
            Detected = np.logical_and(DateFirstScolyte <= DateIndex,EtatChange)
            # SolNu = np.logical_and(DateFirstSolNu <= DateIndex,BoolSolNu)
            Atteint = np.full_like(Detected,5,dtype=np.uint8)
            Atteint[MaskForet]=Detected[MaskForet]#+2*SolNu[MaskForet]
            
            if ExportAsShapefile:
                writeShapefiles(date, Atteint, MaskForet, DataDirectory, tuile, MetaProfile, CRS_Tuile)        
            else:
                writeRasters(Atteint, DataDirectory,tuile,date,MetaProfile)
                
        # TimeWriteResults=time.time() - start_time
        # print("Ecriture des résultats : %s secondes ---" % (time.time() - start_time_debut))
        # TimeTotal=time.time() - start_time_debut
        # writeExecutionTimeUpdate(Version, tuile, TimeTotal, TimeInitialisation, TimeComputeDate,TimeWriteInputData, TimeDetectAnomalies, TimeDetectDeperissement,TimeWriteDataUpdate, TimeWriteResults, Dates.shape[0] - OldDates.shape[0])

if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    DetectionScolytes(**dictArgs)