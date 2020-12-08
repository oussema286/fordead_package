# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 12:02:24 2020

@author: admin
"""

from examples.step1_compute_forest_mask import compute_forest_mask
from examples.step2_compute_masked_vegetationindex import compute_masked_vegetationindex
from examples.step3_TrainFordead import train_model
from examples.step4_DetectionFordead import decline_detection
from fordead.ImportData import TileInfo

from pathlib import Path
import argparse
import time
import datetime

# main_directory=  "/mnt/fordead/Out"

# main_directory=  "D:/Documents/Deperissement/Output_detection"



def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--main_directory", dest = "main_directory",type = str,default =  "/mnt/fordead/Out", help = "Dossier contenant les dossiers des tuiles")
    parser.add_argument('-t', '--tuiles', nargs='+',default=["T31UFQ"],help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("-f", "--forest_mask_source", dest = "forest_mask_source",type = str,default = None, help = "Source of the forest mask, accepts 'BDFORET', 'OSO', or None in which case all pixels will be considered valid")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

def process_tiles(main_directory, 
                  tuiles,
                  forest_mask_source):
    
    main_directory = Path(main_directory)
    logpath = main_directory / (datetime.datetime.now().strftime("%Y-%m-%d-%HH%Mm%Ss") + ".txt")
    file = open(logpath, "w") 
    file.close()
    
    for tuile in tuiles:
        file = open(logpath, "a") 
        file.write("Tuile : " + tuile + "\n") ; start_time = time.time()
        file.close()
        
        start_time = time.time()
        
        path_example_raster = "/mnt/fordead/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif"
        dep_path = "/mnt/fordead/Data/Vecteurs/Departements/departements-20140306-100m.shp"
        bdforet_dirpath = "/mnt/fordead/Data/Vecteurs/BDFORET"
        input_directory = "/mnt/fordead/Data/SENTINEL/" + tuile
        
        # path_example_raster = "G:/Deperissement/Data/SENTINEL/T31UFQ/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1_FRE_B2.tif"
        # dep_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/Departements/departements-20140306-100m.shp"
        # bdforet_dirpath = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/BDFORET"
        # input_directory = "G:/Deperissement/Data/SENTINEL/T31UFQ/"
# =====================================================================================================================
  
        print("Computing forest mask")
        compute_forest_mask(data_directory = main_directory / tuile,
                            path_example_raster = path_example_raster,
                            forest_mask_source = forest_mask_source,
                            dep_path = dep_path,
                            bdforet_dirpath = bdforet_dirpath)
        file = open(logpath, "a") 
        file.write("compute_forest_mask : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================
     
        print("Computing masks and vegetation index")
        compute_masked_vegetationindex(input_directory = input_directory,
                                        data_directory = main_directory / tuile)
        file = open(logpath, "a") 
        file.write("compute_masked_vegetationindex : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================
        
        print("Training")
        train_model(data_directory=main_directory / tuile,  threshold_outliers = 0.16)
        print(str(time.time() - start_time))
        file = open(logpath, "a") 
        file.write("train_model : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================
    
        print("Decline detetion")
        decline_detection(data_directory=main_directory / tuile)
        file = open(logpath, "a") 
        file.write("decline_detection : " + str(time.time() - start_time) + "\n\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================
 
    tile = TileInfo(main_directory / tuile)
    tile = tile.import_info()
    file = open(logpath, "a") 
    for parameter in tile.parameters:
        file.write(parameter + " : " +  str(tile.parameters[parameter]) + "\n")
    file.close()

if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    process_tiles(**dictArgs)

