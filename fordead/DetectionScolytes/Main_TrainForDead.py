# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 10:30:53 2020

@author: admin


"""

#%% =============================================================================
#   LIBRAIRIES
# =============================================================================

import os, time, datetime, sys
import numpy as np
import argparse

#%% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================

from Lib_ImportValidSentinelData import readInputDataDateByDate, getDates
from Lib_ComputeMasks import getMaskForet
from Lib_DetectionDeperissement import ModelCRSWIR
from Lib_WritingResults import CreateDirectories
from Lib_SaveForUpdate import SaveDataModel

#%% =============================================================================
#   FONCTIONS
# =============================================================================

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--Tuiles', nargs='+',default=["ZoneTest"],help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("-s", "--SeuilMin", dest = "SeuilMin",type = float,default = 0.04, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-a", "--CoeffAnomalie", dest = "CoeffAnomalie",type = float,default = 4, help = "Coefficient multiplicateur du seuil de détection d'anomalies")
    parser.add_argument("-k", "--RemoveOutliers", dest = "RemoveOutliers", action="store_false",default = True, help = "Si activé, garde les outliers dans les deux premières années")
    parser.add_argument("-g", "--DateFinApprentissage", dest = "DateFinApprentissage",type = str,default = "2018-06-01", help = "Uniquement les dates antérieures à la date indiquée seront utilisées")
    parser.add_argument("-o", "--DataDirectory", dest = "DataDirectory",type = str,default = "G:/Deperissement/Code/Python/fordead_package/fordead/tests/OutputFordead", help = "Dossier avec les indices de végétations et les masques")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
        
    return dictArgs
    
def TrainForDead(    
    Tuiles= ["ZoneTest"],
    SeuilMin=0.04,
    CoeffAnomalie=4,
    RemoveOutliers=True,
    DateFinApprentissage="2018-06-01",
    DataDirectory = "G:/Deperissement/Out/PackageVersion"
    ):

    CreateDirectories(DataDirectory,Tuiles)
    # writeParameters(Version, Tuiles, SeuilMin, CoeffAnomalie, PercNuageLim, ApplyMaskTheia, RemoveOutliers, InterpolationOrder, ExportMasks,CorrectCRSWIR,DataSource,ExportAsShapefile,DateFinApprentissage)
    
    for tuile in Tuiles:
        start_time_debut = time.time()
        
        Dates=getDates(tuile,DataDirectory)
        MaskForet,MetaProfile,CRS_Tuile = getMaskForet(os.path.join(DataDirectory,"MaskForet",tuile+"_MaskForet.tif"))
    
        # TimeInitialisation=time.time() - start_time_debut ; start_time = time.time()
        StackVegetationIndex, StackMask = readInputDataDateByDate(DataDirectory, Dates[Dates<DateFinApprentissage],tuile)
        # TimeReadInput=time.time() - start_time; start_time = time.time()
        print("Import des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))
        StackVegetationIndex = np.ma.masked_array(StackVegetationIndex, mask=StackMask) #Application du masque
        rasterP, rasterSigma = ModelCRSWIR(np.where(MaskForet),Dates[Dates<DateFinApprentissage],StackVegetationIndex,RemoveOutliers, SeuilMin, CoeffAnomalie)
        # TimeModelCRSWIR=time.time() - start_time ; start_time = time.time()
        
        print("Modélisation du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))
        
        SaveDataModel(rasterP,rasterSigma, MetaProfile, tuile,DataDirectory)
        
        # TimeWriteDataUpdate=time.time() - start_time
        print("Ecriture du modele : %s secondes ---" % (time.time() - start_time_debut))
        # TimeTotal=time.time() - start_time_debut
        # writeExecutionTime(Version, tuile, TimeTotal, TimeInitialisation,TimeComputeDate,TimeWriteInputData,TimeReadInput,TimeModelCRSWIR,TimeWriteDataUpdate)

if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    TrainForDead(**dictArgs)