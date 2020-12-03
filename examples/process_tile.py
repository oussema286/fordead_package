# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 12:02:24 2020

@author: admin
"""

from examples.compute_forest_mask import compute_forest_mask
from examples.compute_masked_vegetationindex import compute_masked_vegetationindex
from examples.TrainFordead import train_model
from examples.DetectionFordead import decline_detection
from fordead.ImportData import TileInfo

from pathlib import Path
import argparse
import time
import datetime

# main_directory= "/mnt/fordead/Out"
# path_example_raster = "/mnt/fordead/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif""
# forest_mask_source = None ou "BDFORET"
# dep_path = "/mnt/fordead/Data/Vecteurs/Departements/departements-20140306-100m.shp"
# bdforet_dirpath = "/mnt/fordead/Data/Vecteurs/BDFORET"
# input_directory = "/mnt/fordead/Data/SENTINEL/" + tuile

# "G:/Deperissement/Out/PackageVersion"
# "G:/Deperissement/Data/SENTINEL/T31UFQ/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1_FRE_B2.tif"
# "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/Departements/departements-20140306-100m.shp"
# "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/BDFORET"
# "G:/Deperissement/Data/SENTINEL"

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--main_directory", dest = "main_directory",type = str,default = "/mnt/fordead/Out", help = "Dossier contenant les dossiers des tuiles")
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
    
    file = open(main_directory / (datetime.datetime.now().strftime("%Y-%m-%d-%HH%Mm%Ss") + ".txt"), "w") 

    for tuile in tuiles:
        file.write("Tuile : " + tuile + "\n") ; start_time = time.time()

        start_time = time.time()
        
        compute_forest_mask(data_directory = main_directory / tuile,
                            path_example_raster = "/mnt/fordead/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif",
                            forest_mask_source = forest_mask_source,
                            dep_path = "/mnt/fordead/Data/Vecteurs/Departements/departements-20140306-100m.shp",
                            bdforet_dirpath = "/mnt/fordead/Data/Vecteurs/BDFORET")
        
        file.write("compute_forest_mask : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        
        compute_masked_vegetationindex(input_directory = "/mnt/fordead/Data/SENTINEL/" + tuile,
                                        data_directory = main_directory / tuile)
        
        file.write("compute_masked_vegetationindex : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        
        train_model(data_directory=main_directory / tuile,  threshold_outliers = 0.161)
        
        file.write("train_model : " + str(time.time() - start_time) + "\n") ; start_time = time.time()

        decline_detection(data_directory=main_directory / tuile)
        
        file.write("decline_detection : " + str(time.time() - start_time) + "\n\n") ; start_time = time.time()
    
    
    tile = TileInfo(main_directory / tuile)
    tile = tile.import_info()
    for parameter in tile.parameters:
        file.write(parameter + " : " +  str(tile.parameters[parameter]) + "\n")

    file.close()

if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    process_tiles(**dictArgs)

