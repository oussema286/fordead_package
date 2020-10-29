# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 23:23:05 2020
# -*- coding: utf-8 -*-


L'arborescence nécessaire pour faire tourner l'algorithme est la suivante :
    - Data
        -SENTINEL
            -Tuile1
                -Date1
                -Date2
                ...
            -Tuile2
            ...
        -Vecteurs
            -Departements
                departements-20140306-100m.shp
            -BDFORET
                -BD_Foret_V2_Dep001
                -BD_Foret_V2_Dep002
                ...
            TilesSentinel.shp

Les résultats sont écrits dans :
    -Out
        -Results


"""

#%% =============================================================================
#   LIBRAIRIES
# =============================================================================


import os, time, sys
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
    parser.add_argument("-n", "--PercNuageLim", dest = "PercNuageLim",type = float,default = 0.3, help = "Pourcentage d'ennuagement maximum à l'échelle de la tuile pour utilisation de la date SENTINEL")
    parser.add_argument("-m", "--ApplyMaskTheia", dest = "ApplyMaskTheia", action="store_true",default = False, help = "Si activé, applique le masque theia")
    parser.add_argument("-i", "--InterpolationOrder", dest = "InterpolationOrder",type = int,default = 0, help ="Ordre d'interpolation : 0 = proche voisin, 1 = linéaire, 2 = bilinéaire, 3 = cubique")
    parser.add_argument("-c", "--CorrectCRSWIR", dest = "CorrectCRSWIR", action="store_true",default = False, help = "Si activé, execute la correction du CRSWIR à partir")
    parser.add_argument("-d", "--DataSource", dest = "DataSource",type = str,default = "THEIA", help = "Source des données parmi THEIA et Scihub et PEPS")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    Tuiles=dictArgs["Tuiles"]
    PercNuageLim=dictArgs["PercNuageLim"]
    ApplyMaskTheia=dictArgs["ApplyMaskTheia"]
    InterpolationOrder=dictArgs["InterpolationOrder"]
    CorrectCRSWIR=dictArgs["CorrectCRSWIR"]
    DataSource=dictArgs["DataSource"]
    
    os.chdir('/mnt/fordead')
    sys.path.append(os.path.abspath("~/Scripts/DetectionScolytes"))
    
else:
    #["T31UFQ","T31UGP","T31UGQ"]
    Tuiles= ["ZoneTest1","ZoneTest2"]
    PercNuageLim=1.1
    ApplyMaskTheia=False
    InterpolationOrder=0
    CorrectCRSWIR=False
    DataSource="THEIA"
    DataDirectory = "G:/Deperissement/Out/PackageVersion"
    
    os.chdir('G:/Deperissement')
    sys.path.append(os.path.abspath(os.getcwd()+"/Code/Python/fordead/DetectionScolytes"))

#%% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================

from Lib_ImportValidSentinelData import getSentinelPaths, getValidDates, ComputeDate
from Lib_ComputeMasks import getRasterizedBDForet
from Lib_DetectionDeperissement import getCRSWIRCorrection
from Lib_WritingResults import CreateDirectories, writeInputDataDateByDate
    
#%% =============================================================================
#   MAIN CODE
# ===============================================================================

CreateDirectories(DataDirectory,Tuiles)

for tuile in Tuiles:
    start_time_debut = time.time()

    #DETERMINE DATES VALIDES
    DictSentinelPaths = getSentinelPaths(tuile,DataSource) #Récupération de l'ensemble des dates avant la date de fin d'apprentissage, associées aux chemins de chaque bande SENTINEL-2
    
    Dates = getValidDates(DictSentinelPaths,tuile, PercNuageLim,DataSource)
    
    #RASTERIZE MASQUE FORET
    MaskForet,MetaProfile,CRS_Tuile = getRasterizedBDForet(DataDirectory,tuile)
    
    #COMPUTE CRSWIR MEDIAN
    listDiffCRSWIRmedian = getCRSWIRCorrection(DictSentinelPaths,getValidDates(getSentinelPaths(tuile,"3000-01-01",DataSource),tuile, PercNuageLim,DataSource),tuile,MaskForet)[:Dates.shape[0]] if CorrectCRSWIR else []
  
    CompteurSolNu= np.zeros((MaskForet.shape[0],MaskForet.shape[1]),dtype=np.uint8) #np.int8 possible ?
    DateFirstSolNu=np.zeros((MaskForet.shape[0],MaskForet.shape[1]),dtype=np.uint16) #np.int8 possible ?
    BoolSolNu=np.zeros((MaskForet.shape[0],MaskForet.shape[1]), dtype='bool')
    
    for DateIndex,date in enumerate(Dates):
        print(date)
        VegetationIndex ,Mask, BoolSolNu, CompteurSolNu,DateFirstSolNu = ComputeDate(date,DateIndex,DictSentinelPaths,InterpolationOrder,ApplyMaskTheia,BoolSolNu,CompteurSolNu,DateFirstSolNu,listDiffCRSWIRmedian,CorrectCRSWIR)
        writeInputDataDateByDate(VegetationIndex,Mask,MetaProfile,date,DataDirectory,tuile)
        # writeInputDataStack(VegetationIndex,Mask,MetaProfile,DateIndex,Version,tuile,Dates)

    print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))