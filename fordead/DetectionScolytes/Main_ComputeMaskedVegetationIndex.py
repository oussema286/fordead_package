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
        -Rasters
            - Tuile1
                -MaskForet_Tuile1.tif (raster binaire (1 pour la foret, en dehors) dont l'extent, la résolution et le CRS correspondent aux bandes SENTINEL à 10m)

Pour créer le masque forêt à partir de la BD FORET, assigner "BDFORET" au paramètre ForestMaskSource. De plus, l'arborescence suivante devient nécessaire :
    - Data
        -Vecteurs
            -Departements
                departements-20140306-100m.shp
            -BDFORET
                -BD_Foret_V2_Dep001
                -BD_Foret_V2_Dep002
                ...
            TilesSentinel.shp




"""

#%% =============================================================================
#   LIBRAIRIES
# =============================================================================

import time
import numpy as np
import argparse

#%% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================

from Lib_ImportValidSentinelData import getSentinelPaths, getValidDates, ComputeDate
from Lib_ComputeMasks import getRasterizedBDForet
from Lib_DetectionDeperissement import getCRSWIRCorrection
from Lib_WritingResults import CreateDirectories, writeInputDataDateByDate,writeMaskForet
    
#%% =============================================================================
#   FONCTIONS
# =============================================================================

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--Tuiles', nargs='+',default=["ZoneTest"],help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("-n", "--PercNuageLim", dest = "PercNuageLim",type = float,default = 0.3, help = "Pourcentage d'ennuagement maximum à l'échelle de la tuile pour utilisation de la date SENTINEL")
    parser.add_argument("-m", "--ApplyMaskTheia", dest = "ApplyMaskTheia", action="store_true",default = False, help = "Si activé, applique le masque theia")
    parser.add_argument("-s", "--InterpolationOrder", dest = "InterpolationOrder",type = int,default = 0, help ="Ordre d'interpolation : 0 = proche voisin, 1 = linéaire, 2 = bilinéaire, 3 = cubique")
    parser.add_argument("-c", "--CorrectCRSWIR", dest = "CorrectCRSWIR", action="store_true",default = False, help = "Si activé, execute la correction du CRSWIR à partir")
    parser.add_argument("-d", "--DataSource", dest = "DataSource",type = str,default = "THEIA", help = "Source des données parmi THEIA et Scihub et PEPS")
    parser.add_argument("-i", "--InputDirectory", dest = "InputDirectory",type = str,default = "G:/Deperissement/Data/", help = "Chemin des données en entrée")
    parser.add_argument("-o", "--OutputDirectory", dest = "OutputDirectory",type = str,default = "G:/Deperissement/Out/PackageVersion", help = "Chemin du dossier où sauvegarder les résultats")
    parser.add_argument("-f", "--ForestMaskSource", dest = "ForestMaskSource",type = str,default = "LastComputed", help = "Source du masque forêt, accepte pour le moment 'LastComputed' et 'BDFORET'")
    
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
        
    return dictArgs

def ComputeMaskedVI(
    Tuiles= ["ZoneTest"],
    PercNuageLim=0.5,
    ApplyMaskTheia=False,
    InterpolationOrder=0,
    CorrectCRSWIR=False,
    DataSource="THEIA",
    OutputDirectory = "G:/Deperissement/Out/PackageVersion",
    InputDirectory= "G:/Deperissement/Data/",
    ForestMaskSource="LastComputed"):
    
    #############################
    
    CreateDirectories(OutputDirectory,Tuiles)
    
    for tuile in Tuiles:
        start_time_debut = time.time()
    
        #DETERMINE DATES VALIDES
        DictSentinelPaths = getSentinelPaths(InputDirectory,tuile,DataSource) #Récupération de l'ensemble des dates avant la date de fin d'apprentissage, associées aux chemins de chaque bande SENTINEL-2
    
        Dates = getValidDates(DictSentinelPaths,tuile, PercNuageLim,DataSource)
        
        #RASTERIZE MASQUE FORET
        MaskForet,MetaProfile,CRS_Tuile = getRasterizedBDForet(DictSentinelPaths[Dates[0]]["B2"],InputDirectory,ForestMaskSource,tuile)
        writeMaskForet(MaskForet,MetaProfile,OutputDirectory,tuile)
        
        #COMPUTE CRSWIR MEDIAN
        listDiffCRSWIRmedian = getCRSWIRCorrection(DictSentinelPaths,getValidDates(getSentinelPaths(InputDirectory,tuile,DataSource),tuile, PercNuageLim,DataSource),tuile,MaskForet)[:Dates.shape[0]] if CorrectCRSWIR else []
    
        CompteurSolNu= np.zeros((MaskForet.shape[0],MaskForet.shape[1]),dtype=np.uint8) #np.int8 possible ?
        DateFirstSolNu=np.zeros((MaskForet.shape[0],MaskForet.shape[1]),dtype=np.uint16) #np.int8 possible ?
        BoolSolNu=np.zeros((MaskForet.shape[0],MaskForet.shape[1]), dtype='bool')
        
        for DateIndex,date in enumerate(Dates):
            print(date)
            VegetationIndex ,Mask, BoolSolNu, CompteurSolNu,DateFirstSolNu = ComputeDate(date,DateIndex,DictSentinelPaths,InterpolationOrder,ApplyMaskTheia,BoolSolNu,CompteurSolNu,DateFirstSolNu,listDiffCRSWIRmedian,CorrectCRSWIR)
            writeInputDataDateByDate(VegetationIndex,Mask,MetaProfile,date,OutputDirectory,tuile)
            # writeInputDataStack(VegetationIndex,Mask,MetaProfile,DateIndex,Version,tuile,Dates)
            
        print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))
        
        
if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    ComputeMaskedVI(**dictArgs)