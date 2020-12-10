# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 16:06:51 2020

@author: Raphaël Dutrieux

L'arborescence nécessaire dans le dossier indiqué par le paramètre InputDirectory est la suivante :
    -tile1
        -Date1
        -Date2
        ...

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

from fordead.ImportData import TileInfo, get_band_paths, get_cloudiness, import_resampled_sen_stack, import_soil_data, initialize_soil_data, get_raster_metadata
from fordead.masking_vi import compute_masks, compute_vegetation_index
from fordead.writing_data import write_tif

#%% =============================================================================
#   FONCTIONS
# =============================================================================

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_directory", dest = "input_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/input_sentinel/ZoneTest", help = "Path of the directory with Sentinel dates")
    parser.add_argument("-o", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection/ZoneTest", help = "Path of the output directory")
    # parser.add_argument("-t", "--tile", dest = "tile",type = str,default = "ZoneTest", help = "Chemin du dossier où sauvegarder les résultats")
    parser.add_argument("-n", "--lim_perc_cloud", dest = "lim_perc_cloud",type = float,default = 0.3, help = "Maximum cloudiness at the tile or zone scale, used to filter used SENTINEL dates")
    # parser.add_argument("-s", "--InterpolationOrder", dest = "InterpolationOrder",type = int,default = 0, help ="interpolation order : 0 = nearest neighbour, 1 = linear, 2 = bilinéaire, 3 = cubique")
    # parser.add_argument("-c", "--CorrectCRSWIR", dest = "CorrectCRSWIR", action="store_true",default = False, help = "Si activé, execute la correction du CRSWIR à partir")
    parser.add_argument("-d", "--sentinel_source", dest = "sentinel_source",type = str,default = "THEIA", help = "Source des données parmi 'THEIA' et 'Scihub' et 'PEPS'")
    parser.add_argument("-m", "--apply_source_mask", dest = "apply_source_mask", action="store_true",default = False, help = "If activated, applies the mask from SENTINEL-data supplier")
    parser.add_argument("-v", "--vi", dest = "vi",type = str,default = "CRSWIR", help = "Chosen vegetation index")

    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def compute_masked_vegetationindex(
    # Tuiles= ["ZoneTestLarge"],
    # InterpolationOrder=0,
    # CorrectCRSWIR=False,
    input_directory,
    data_directory,
    lim_perc_cloud=0.3,
    # forest_mask_source = "LastComputed",
    sentinel_source = "THEIA",
    apply_source_mask = False,
    vi = "CRSWIR",
    ):
    #############################
    
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"lim_perc_cloud" : lim_perc_cloud, "sentinel_source" : sentinel_source, "apply_source_mask" : apply_source_mask, "vi" : vi})
    if tile.parameters["Overwrite"] : tile.delete_dirs("VegetationIndexDir", "MaskDir","coeff_model", "AnomaliesDir","state_decline", "state_soil", "valid_area_mask")

    tile.getdict_datepaths("Sentinel",Path(input_directory)) #adds a dictionnary to tile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands
    tile.paths["Sentinel"] = get_band_paths(tile.paths["Sentinel"]) #Replaces the paths to the directories for each date with a dictionnary where keys are the bands, and values are their paths
    
    #Adding directories for ouput
    tile.add_dirpath("VegetationIndexDir", tile.data_directory / "VegetationIndex")
    tile.add_dirpath("MaskDir", tile.data_directory / "Mask")
    
    raster_meta = get_raster_metadata(list(tile.paths["Sentinel"].values())[0]["B2"])

    tile.add_path("state_soil", tile.data_directory / "DataSoil" / "state_soil.tif")
    tile.add_path("first_date_soil", tile.data_directory / "DataSoil" / "first_date_soil.tif")
    tile.add_path("count_soil", tile.data_directory / "DataSoil" / "count_soil.tif")
        
    #Computing cloudiness percentage for each date
    cloudiness = get_cloudiness(Path(input_directory) / "cloudiness", tile.paths["Sentinel"], sentinel_source)

    #Import or initialize data for the soil mask
    if tile.paths["state_soil"].exists():
        soil_data = import_soil_data(tile.paths)
    else:
        soil_data = initialize_soil_data(raster_meta["shape"],raster_meta["coords"])

    #get already computed dates
    tile.getdict_datepaths("VegetationIndex",tile.paths["VegetationIndexDir"])
    date_index=0
    for date in tile.paths["Sentinel"]:
        if cloudiness.perc_cloud[date] <= lim_perc_cloud and not(date in tile.paths["VegetationIndex"]): #If date not too cloudy and not already computed
            # print(date)
            # Resample and import SENTINEL data
            stack_bands = import_resampled_sen_stack(tile.paths["Sentinel"][date], ["B2","B3","B4","B8A","B11","B12"])
            # Compute masks
            mask = compute_masks(stack_bands, soil_data, date_index)
            # Compute vegetation index
            vegetation_index = compute_vegetation_index(stack_bands, vi)
            write_tif(vegetation_index, raster_meta["attrs"],tile.paths["VegetationIndexDir"] / ("VegetationIndex_"+date+".tif"),nodata=0)
            write_tif(mask, raster_meta["attrs"], tile.paths["MaskDir"] / ("Mask_"+date+".tif"),nodata=0)
            date_index=date_index+1
    
    print(str(date_index) + " new SENTINEL dates")
  
    if date_index!=0: #If there is at least one new date
        write_tif(soil_data["state"], raster_meta["attrs"],tile.paths["state_soil"],nodata=0)
        write_tif(soil_data["first_date"], raster_meta["attrs"],tile.paths["first_date_soil"],nodata=0)
        write_tif(soil_data["count"], raster_meta["attrs"],tile.paths["count_soil"],nodata=0)
    
    tile.save_info()
    
if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    start_time_debut = time.time()
    compute_masked_vegetationindex(**dictArgs)
    print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))


