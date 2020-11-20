# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 16:06:51 2020

@author: Raphaël Dutrieux

L'arborescence nécessaire dans le dossier indiqué par le paramètre InputDirectory est la suivante :
    -Tuile1
        -Date1
        -Date2
        ...
    # -Rasters
    #     - Tuile1
    #         -MaskForet_Tuile1.tif (raster binaire (1 pour la foret, en dehors) dont l'extent, la résolution et le CRS correspondent aux bandes SENTINEL à 10m)

Pour créer le masque forêt à partir de la BD FORET, assigner "BDFORET" au paramètre ForestMaskSource. De plus, l'arborescence suivante devient nécessaire :
    - Data
        -Vecteurs
            -Departements
                # departements-20140306-100m.shp
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
# import numpy as np
import argparse
from pathlib import Path
# from path import Path
#%% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================

from fordead.ImportData import TileInfo, get_band_paths

#%% =============================================================================
#   FONCTIONS
# =============================================================================

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_directory", dest = "input_directory",type = str,default = "G:/Deperissement/Data/SENTINEL/ZoneTest", help = "Path of the directory with Sentinel dates")
    parser.add_argument("-o", "--data_directory", dest = "data_directory",type = str,default = "G:/Deperissement/Out/PackageVersion", help = "Path of the output directory")
    # parser.add_argument("-t", "--tuile", dest = "tuile",type = str,default = "ZoneTest", help = "Chemin du dossier où sauvegarder les résultats")
    parser.add_argument("-n", "--lim_perc_cloud", dest = "lim_perc_cloud",type = float,default = 0.3, help = "Maximum cloudiness at the tile or zone scale, used to filter used SENTINEL dates")
    # parser.add_argument("-s", "--InterpolationOrder", dest = "InterpolationOrder",type = int,default = 0, help ="interpolation order : 0 = nearest neighbour, 1 = linear, 2 = bilinéaire, 3 = cubique")
    # parser.add_argument("-c", "--CorrectCRSWIR", dest = "CorrectCRSWIR", action="store_true",default = False, help = "Si activé, execute la correction du CRSWIR à partir")
    parser.add_argument("-f", "--forestmask_source", dest = "forestmask_source",type = str,default = "BDFORET", help = "Source of the forest mask")
    parser.add_argument("-d", "--sentinel_source", dest = "sentinel_source",type = str,default = "THEIA", help = "Source des données parmi THEIA et Scihub et PEPS")
    parser.add_argument("-m", "--apply_source_mask", dest = "apply_source_mask", action="store_true",default = False, help = "If activated, applies the mask from SENTINEL-data supplier")
    
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
        
    return dictArgs




def ComputeMaskedVI(
    # Tuiles= ["ZoneTestLarge"],
    # InterpolationOrder=0,
    # CorrectCRSWIR=False,
    input_directory = "G:/Deperissement/Data/",
    data_directory = "G:/Deperissement/Out/PackageVersion",
    lim_perc_cloud=0.3,
    forestmask_source = "LastComputed",
    sentinel_source = "THEIA",
    apply_source_mask = False
    ):
    #############################
    
    input_directory="G:/Deperissement/Data/SENTINEL/ZoneTest"
    input_directory=Path(input_directory)
    
    tuile = TileInfo(input_directory)

    tuile.getdict_datepaths("Sentinel",Path(input_directory)) #adds a dictionnary to tuile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands
    tuile.paths["Sentinel"] = get_band_paths(tuile.paths["Sentinel"]) #Replaces the paths to the directories for each date with a dictionnary where keys are the bands, and values are thair paths
    
    #Filter dates with source cloud mask
    #Check what dates are already computed in the output directory
    #Compute forest mask
    #Compute masks and vegetation index
    
    # Dates = getValidDates(DictSentinelPaths,tuile, PercNuageLim,DataSource)
    
    # #RASTERIZE MASQUE FORET
    # MaskForet,MetaProfile,CRS_Tuile = ComputeMaskForet(DictSentinelPaths[Dates[0]]["B2"],InputDirectory,ForestMaskSource,tuile)
    # writeBinaryRaster(MaskForet,os.path.join(OutputDirectory,"MaskForet",tuile+"_MaskForet.tif"),MetaProfile)
    
    # #COMPUTE CRSWIR MEDIAN
    # listDiffCRSWIRmedian = getCRSWIRCorrection(DictSentinelPaths,getValidDates(getSentinelPaths(InputDirectory,tuile,DataSource),tuile, PercNuageLim,DataSource),tuile,MaskForet)[:Dates.shape[0]] if CorrectCRSWIR else []

    # CompteurSolNu= np.zeros((MaskForet.shape[0],MaskForet.shape[1]),dtype=np.uint8) #np.int8 possible ?
    # DateFirstSolNu=np.zeros((MaskForet.shape[0],MaskForet.shape[1]),dtype=np.uint16) #np.int8 possible ?
    # BoolSolNu=np.zeros((MaskForet.shape[0],MaskForet.shape[1]), dtype='bool')
    
    # for DateIndex,date in enumerate(Dates):
    #     print(date)
    #     VegetationIndex ,Mask, BoolSolNu, CompteurSolNu,DateFirstSolNu = ComputeDate(date,DateIndex,DictSentinelPaths,InterpolationOrder,ApplyMaskTheia,BoolSolNu,CompteurSolNu,DateFirstSolNu,listDiffCRSWIRmedian,CorrectCRSWIR)
    #     writeInputDataDateByDate(VegetationIndex,Mask,MetaProfile,date,OutputDirectory,tuile)
        # writeInputDataStack(VegetationIndex,Mask,MetaProfile,DateIndex,Version,tuile,Dates)
            
        
        
if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    start_time_debut = time.time()
    ComputeMaskedVI(**dictArgs)
    print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))
