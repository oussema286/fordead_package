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
# from pathlib import Path
from path import Path
#%% ===========================================================================
#   IMPORT LIBRAIRIES PERSO
# =============================================================================

from fordead.ImportData import TileInfo, get_band_paths, get_cloudiness, import_resampled_sen_stack
from fordead.masking_vi import get_forest_mask, import_soil_data, initialize_soil_data, get_pre_masks, detect_soil
#%% =============================================================================
#   FONCTIONS
# =============================================================================

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_directory", dest = "input_directory",type = str,default = "G:/Deperissement/Data/SENTINEL/ZoneTest", help = "Path of the directory with Sentinel dates")
    parser.add_argument("-o", "--data_directory", dest = "data_directory",type = str,default = "G:/Deperissement/Out/PackageVersion/ZoneTest", help = "Path of the output directory")
    # parser.add_argument("-t", "--tuile", dest = "tuile",type = str,default = "ZoneTest", help = "Chemin du dossier où sauvegarder les résultats")
    parser.add_argument("-n", "--lim_perc_cloud", dest = "lim_perc_cloud",type = float,default = 0.3, help = "Maximum cloudiness at the tile or zone scale, used to filter used SENTINEL dates")
    # parser.add_argument("-s", "--InterpolationOrder", dest = "InterpolationOrder",type = int,default = 0, help ="interpolation order : 0 = nearest neighbour, 1 = linear, 2 = bilinéaire, 3 = cubique")
    # parser.add_argument("-c", "--CorrectCRSWIR", dest = "CorrectCRSWIR", action="store_true",default = False, help = "Si activé, execute la correction du CRSWIR à partir")
    # parser.add_argument("-f", "--forest_mask_source", dest = "forestmask_source",type = str,default = "BDFORET", help = "Source of the forest mask")
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
    input_directory = "G:/Deperissement/Data/SENTINEL/ZoneTest",
    data_directory = "G:/Deperissement/Out/PackageVersion/ZoneTest",
    lim_perc_cloud=0.3,
    # forest_mask_source = "LastComputed",
    sentinel_source = "THEIA",
    apply_source_mask = False
    ):
    #############################
    
    input_directory = "G:/Deperissement/Data/SENTINEL/ZoneTestLarge"
    data_directory = "G:/Deperissement/Out/PackageVersion/ZoneTestLarge"

    # input_directory=Path(input_directory)
    input_directory=Path(input_directory)
    
    tuile = TileInfo(data_directory)

    tuile.getdict_datepaths("Sentinel",input_directory) #adds a dictionnary to tuile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands
    tuile.paths["Sentinel"] = get_band_paths(tuile.paths["Sentinel"]) #Replaces the paths to the directories for each date with a dictionnary where keys are the bands, and values are their paths
    
    #Adding directories for ouput
    tuile.add_dirpath("VegetationIndexDir", tuile.data_directory / "VegetationIndex")
    tuile.add_dirpath("MaskDir", tuile.data_directory / "Mask")
    tuile.add_path("ForestMask", tuile.data_directory / "ForestMask" / "Forest_Mask.tif")
    
    #Compute forest mask
    forest_mask = get_forest_mask(tuile.paths["ForestMask"],
                                  example_path = tuile.paths["Sentinel"][list(tuile.paths["Sentinel"].keys())[0]]["B2"],
                                  dep_path = "G:/Deperissement/Data/Vecteurs/Departements/departements-20140306-100m.shp",
                                  bdforet_dirpath = "G:/Deperissement/Data/Vecteurs/BDFORET")
    
    #Computing cloudiness percentage for each date
    cloudiness = get_cloudiness(input_directory / "cloudiness", tuile.paths["Sentinel"], sentinel_source)

    #Import or initialize data for the soil mask
    if "state_soil" in tuile.paths:
        soil_data = import_soil_data(tuile.paths)
    else:
        soil_data = initialize_soil_data(forest_mask.shape,forest_mask.coords)
        
        tuile.add_path("state_soil", tuile.data_directory / "DataSoil" / "state_soil.tif")
        tuile.add_path("first_date_soil", tuile.data_directory / "DataSoil" / "first_date_soil.tif")
        tuile.add_path("count_soil", tuile.data_directory / "DataSoil" / "count_soil.tif")

    #get already computed dates
    tuile.getdict_datepaths("VegetationIndex",tuile.paths["VegetationIndexDir"])
    
    for date_index, date in enumerate(tuile.paths["Sentinel"]):
        if cloudiness.perc_cloud[date] <= lim_perc_cloud and not(date in tuile.paths["VegetationIndex"]): #If date not too cloudy and not already computed
            print(date)
            # Resample and import SENTINEL data
            stack_bands = import_resampled_sen_stack(tuile.paths["Sentinel"][date], ["B2","B3","B4","B8A","B11","B12"])
            
            # Compute pre-masks
            premask_soil, shadows, outside_swath, invalid = get_pre_masks(stack_bands)
            
            # Compute soil
            soil_data = detect_soil(soil_data, premask_soil, invalid, date_index)
                        
            # Compute clouds
            # stackBands=np.ma.array(stackBands, mask = Ombres[:,:,np.newaxis]**[1 for i in range(stackBands.shape[-1])]) #Pas forcément indispensable mais retire erreur
            # Nuages2=getNuages2(stackBands,DictBandPosition,HorsFauche,BoolSolNu,SolNu)
            
            # #Compute vegetation index
            # VegetationIndex=stackBands[:,:,DictBandPosition["B11"]]/(stackBands[:,:,DictBandPosition["B8A"]]+((stackBands[:,:,DictBandPosition["B12"]]-stackBands[:,:,DictBandPosition["B8A"]])/(2185.7-864))*(1610.4-864)) #Calcul du CRSWIR
            
            
            # stack_bands.sel(band="B2").plot()
            print("test")
        
        
if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    start_time_debut = time.time()
    ComputeMaskedVI(**dictArgs)
    print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))
