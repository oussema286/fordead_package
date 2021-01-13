# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 14:37:00 2020

@author: admin
"""

import time

#%% ===========================================================================
#   IMPORT LIBRAIRIES 
# =============================================================================

from fordead.ImportData import TileInfo, get_band_paths, import_resampled_sen_stack
from fordead.masking_vi import compute_vegetation_index
from fordead.writing_data import write_tif

input_directory = "G:/Deperissement/Data/SENTINEL/T31UFQ" #Directory with SENTINEL dates
output_directory = "D:/Documents/Test" #Output directory

tile = TileInfo(output_directory)
tile.getdict_datepaths("Sentinel",input_directory) #adds a dictionnary to tile.paths with key "Sentinel" and with value another dictionnary where keys are ordered and formatted dates and values are the paths to the directories containing the different bands
#Adding output directories
tile.add_dirpath("VegetationIndexDir", tile.data_directory / "VegetationIndex")
tile.add_dirpath("MaskDir", tile.data_directory / "Mask")


tile.paths["Sentinel"] = get_band_paths(tile.paths["Sentinel"]) #Replaces the paths to the directories for each date with a dictionnary where keys are the bands, and values are their path
for date in tile.paths["Sentinel"]:
    print(date)
    
    start_time = time.time()
    stack_bands = import_resampled_sen_stack(tile.paths["Sentinel"][date], ["B2","B3","B4","B8A","B11","B12"]) #Import of chosen bands, resampling, stacking
    print("import sentinel data : " + str(round(time.time() - start_time,2))) ; start_time = time.time()
    
    # mask = compute_vegetation_index(stack_bands, formula = "B2 > 600") # Compute mask
    # print("Compute mask : " + str(round(time.time() - start_time,2))) ; start_time = time.time()
    
    vegetation_index = compute_vegetation_index(stack_bands, formula = "B2 + B3 - B4") # Compute vegetation index
    print("Compute vegetation index : " + str(round(time.time() - start_time,2))) ; start_time = time.time()
    
    #WRITING RESULTS
    write_tif(vegetation_index, stack_bands.attrs,tile.paths["VegetationIndexDir"] / ("VegetationIndex_"+date+".tif"),nodata=0)
    print("Writing : " + str(round(time.time() - start_time,2))) ; start_time = time.time()
