# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 12:02:24 2020

@author: admin
"""


from examples.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from examples.step2_TrainFordead import train_model
from examples.step3_DetectionFordead import decline_detection
from examples.step4_compute_forest_mask import compute_forest_mask
from fordead.ImportData import TileInfo

from pathlib import Path
import argparse
import time
import datetime

# main_directory=  "/mnt/fordead/Out"

# main_directory=  "D:/Documents/Deperissement/Output_detection"
# main_directory=  "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection"


def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--main_directory", dest = "main_directory",type = str, help = "Dossier contenant les dossiers des tuiles")
    parser.add_argument('-t', '--tuiles', nargs='+',default = ["ZoneTest"], help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")

    parser.add_argument("-i", "--sentinel_directory", dest = "sentinel_directory",type = str, help = "Path of the directory with a directory containing Sentinel data for each tile ")
    parser.add_argument("-f", "--forest_mask_source", dest = "forest_mask_source",type = str,default = "BDFORET", help = "Source of the forest mask, accepts 'BDFORET', 'OSO', or None in which case all pixels will be considered valid")
    parser.add_argument("-c", "--lim_perc_cloud", dest = "lim_perc_cloud",type = float,default = 0.3, help = "Maximum cloudiness at the tile or zone scale, used to filter used SENTINEL dates")
    parser.add_argument("--vi", dest = "vi",type = str,default = "CRSWIR", help = "Chosen vegetation index")
    parser.add_argument("-k", "--remove_outliers", dest = "remove_outliers", action="store_false",default = True, help = "Si activé, garde les outliers dans les deux premières années")
    parser.add_argument("-s", "--threshold_anomaly", dest = "threshold_anomaly",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    
    parser.add_argument("--path_example_raster", dest = "path_example_raster",type = str, help = "Path to raster from which to copy the extent, resolution, CRS...")
    parser.add_argument("--dep_path", dest = "dep_path",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/Departements/departements-20140306-100m.shp", help = "Path to shapefile containg departements with code insee. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("--bdforet_dirpath", dest = "bdforet_dirpath",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/BDFORET", help = "Path to directory containing BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("--list_forest_type", dest = "list_forest_type",type = str,default = ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], help = "List of forest types to be kept in the forest mask, corresponds to the CODE_TFV of the BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("--path_oso", dest = "path_oso",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/OCS_2017_CESBIO.tif", help = "Path to soil occupation raster, only used if forest_mask_source = 'OSO' ")
    parser.add_argument("--list_code_oso", dest = "list_code_oso",type = str,default = [32], help = "List of values used to filter the soil occupation raster. Only used if forest_mask_source = 'OSO'")

    parser.add_argument("--sentinel_source", dest = "sentinel_source",type = str,default = "THEIA", help = "Source des données parmi 'THEIA' et 'Scihub' et 'PEPS'")
    parser.add_argument("--apply_source_mask", dest = "apply_source_mask", action="store_true",default = False, help = "If activated, applies the mask from SENTINEL-data supplier")
    parser.add_argument("--threshold_outliers", dest = "threshold_outliers",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("--min_last_date_training", dest = "min_last_date_training",type = str,default = "2018-01-01", help = "Première date de la détection")
    parser.add_argument("--date_lim_training", dest = "date_lim_training",type = str,default = "2018-06-01", help = "Dernière date pouvant servir pour l'apprentissage")
    

    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

def process_tiles(main_directory, sentinel_directory, tuiles, forest_mask_source,
                  path_example_raster, dep_path, bdforet_dirpath, list_forest_type, path_oso, list_code_oso, #compute_forest_mask arguments
                  lim_perc_cloud, vi, sentinel_source, apply_source_mask, #compute_masked_vegetationindex arguments
                  remove_outliers, threshold_outliers, min_last_date_training, date_lim_training, #Train_model arguments
                  threshold_anomaly): #Decline_detection argument

    # main_directory = "/mnt/fordead/Out"
    # sentinel_directory = "/mnt/fordead/Data/SENTINEL/"
    
    main_directory = "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection"
    sentinel_directory = "C:/Users/admin/Documents/Deperissement/fordead_data/input_sentinel"
    # sentinel_directory = "G:/Deperissement/Data/SENTINEL"
    
    # main_directory = "D:/Documents/Deperissement/Output_detection"    
    # sentinel_directory = "G:/Deperissement/Data/SENTINEL/"

    sentinel_directory = Path(sentinel_directory)
    main_directory = Path(main_directory)
    logpath = main_directory / (datetime.datetime.now().strftime("%Y-%m-%d-%HH%Mm%Ss") + ".txt")
    file = open(logpath, "w") 
    file.close()
    
    for tuile in tuiles:
        file = open(logpath, "a") 
        file.write("Tuile : " + tuile + "\n") ; start_time = time.time()
        file.close()
        
        start_time = time.time()

        # path_example_raster = "/mnt/fordead/Data/Rasters/"+tuile+"/BDForet_"+tuile+".tif"
        # dep_path = "/mnt/fordead/Data/Vecteurs/Departements/departements-20140306-100m.shp"
        # bdforet_dirpath = "/mnt/fordead/Data/Vecteurs/BDFORET"
        
        # path_example_raster = "C:/Users/admin/Documents/Deperissement/fordead_data/input_sentinel/ZoneTest/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1_FRE_B2.tif"
        # path_example_raster = "G:/Deperissement/Data/SENTINEL/T31UFQ/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1_FRE_B2.tif"
        # dep_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/Departements/departements-20140306-100m.shp"
        # bdforet_dirpath = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/BDFORET"


# =====================================================================================================================
     
        print("Computing masks and vegetation index")
        compute_masked_vegetationindex(input_directory = sentinel_directory / tuile,
                                        data_directory = main_directory / tuile,
                                        lim_perc_cloud = lim_perc_cloud, vi = vi,
                                        sentinel_source = sentinel_source, apply_source_mask = apply_source_mask)
        file = open(logpath, "a") 
        file.write("compute_masked_vegetationindex : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================

        train_model(data_directory=main_directory / tuile,  
                    threshold_outliers = 0.16, remove_outliers = remove_outliers)
        # print(str(time.time() - start_time))
        file = open(logpath, "a") 
        file.write("train_model : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================    
    
        print("Decline detetion")
        decline_detection(data_directory=main_directory / tuile, 
                          threshold_anomaly = threshold_anomaly)
        file = open(logpath, "a") 
        file.write("decline_detection : " + str(time.time() - start_time) + "\n\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================

        # print("Computing forest mask")
        compute_forest_mask(data_directory = main_directory / tuile,
                            forest_mask_source = forest_mask_source,
                            dep_path = dep_path,
                            bdforet_dirpath = bdforet_dirpath)
        file = open(logpath, "a") 
        file.write("compute_forest_mask : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
        
    tile = TileInfo(main_directory / tuile)
    tile = tile.import_info()
    file = open(logpath, "a") 
    for parameter in tile.parameters:
        file.write(parameter + " : " +  str(tile.parameters[parameter]) + "\n")
    file.close()

if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    process_tiles(**dictArgs)

