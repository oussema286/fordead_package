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

#%% =============================================================================
#   DEFINITION DES PARAMETRES
# =============================================================================
# Processeur="VM"
# Processeur="Bureau"
Processeur="Maison"

if Processeur=="VM":
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--Tuiles', nargs='+',default=["T31UFQ","T31UGQ", "T31UGP", "T31TGL", "T31TGM", "T31UFR", "T31TDL", "T31UFP", "T31TFL", "T31TDK", "T32ULU", "T31UEP"],help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("-s", "--SeuilMin", dest = "SeuilMin",type = float,default = 0.04, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-a", "--CoeffAnomalie", dest = "CoeffAnomalie",type = float,default = 4, help = "Coefficient multiplicateur du seuil de détection d'anomalies")
    parser.add_argument("-k", "--RemoveOutliers", dest = "RemoveOutliers", action="store_false",default = True, help = "Si activé, garde les outliers dans les deux premières années")
    parser.add_argument("-g", "--DateFinApprentissage", dest = "DateFinApprentissage",type = str,default = "2018-06-01", help = "Uniquement les dates antérieures à la date indiquée seront utilisées")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    Tuiles=dictArgs["Tuiles"]
    SeuilMin=dictArgs["SeuilMin"]
    CoeffAnomalie=dictArgs["CoeffAnomalie"]
    RemoveOutliers=dictArgs["RemoveOutliers"]
    DateFinApprentissage=dictArgs["DateFinApprentissage"]
    
    os.chdir('/mnt/fordead')
    sys.path.append(os.path.abspath("~/Scripts/DetectionScolytes"))
    
else:
    #["T31UFQ","T31UGP","T31UGQ"]
    Tuiles= ["ZoneTest1"]
    SeuilMin=0.04
    CoeffAnomalie=4
    RemoveOutliers=True
    DateFinApprentissage="2018-06-01"
    
    DataDirectory = "G:/Deperissement/Out/PackageVersion"
    
    os.chdir("G:/Deperissement/")
    sys.path.append(os.path.abspath(os.getcwd()+"/Code/Python/fordead/DetectionScolytes"))

#%% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================

from Lib_ImportValidSentinelData import readInputDataDateByDate, getDates
from Lib_ComputeMasks import getRasterizedBDForet
from Lib_DetectionDeperissement import ModelForAnomalies
from Lib_WritingResults import CreateDirectories
from Lib_SaveForUpdate import SaveDataModel
    
#%% =============================================================================
#   MAIN CODE
# ===============================================================================

# Version = str(getVersion())
CreateDirectories(DataDirectory,Tuiles)
# writeParameters(Version, Tuiles, SeuilMin, CoeffAnomalie, PercNuageLim, ApplyMaskTheia, RemoveOutliers, InterpolationOrder, ExportMasks,CorrectCRSWIR,DataSource,ExportAsShapefile,DateFinApprentissage)

for tuile in Tuiles:
    start_time_debut = time.time()
    #DETERMINE DATES VALIDES    
    
    Dates=getDates(tuile,DataDirectory)
    #RASTERIZE MASQUE FORET
    MaskForet,MetaProfile,CRS_Tuile = getRasterizedBDForet(DataDirectory,tuile)

    # TimeInitialisation=time.time() - start_time_debut
    # sys.exit()
    # start_time = time.time()
    StackVegetationIndex, StackMask = readInputDataDateByDate(DataDirectory, Dates[Dates<DateFinApprentissage],tuile)
    # TimeReadInput=time.time() - start_time; start_time = time.time()
    print("Import des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))
    StackVegetationIndex = np.ma.masked_array(StackVegetationIndex, mask=StackMask) #Application du masque
    rasterP, rasterSigma = ModelForAnomalies(np.where(MaskForet),Dates[Dates<DateFinApprentissage],StackVegetationIndex,RemoveOutliers, SeuilMin, CoeffAnomalie)
    # TimeModelCRSWIR=time.time() - start_time ; start_time = time.time()
    
    print("Modélisation du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))
    
    SaveDataModel(rasterP,rasterSigma, MetaProfile, tuile,DataDirectory)
    
    # TimeWriteDataUpdate=time.time() - start_time
    print("Ecriture du modele : %s secondes ---" % (time.time() - start_time_debut))
    # TimeTotal=time.time() - start_time_debut
    # writeExecutionTime(Version, tuile, TimeTotal, TimeInitialisation,TimeComputeDate,TimeWriteInputData,TimeReadInput,TimeModelCRSWIR,TimeWriteDataUpdate)
