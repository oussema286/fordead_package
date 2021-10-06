# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 12:02:24 2020

@author: Raphael Dutrieux
"""

from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.steps.step2_train_model import train_model
from fordead.steps.step3_decline_detection import decline_detection
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
from fordead.steps.step6_export_results import export_results
from fordead.steps.step5_compute_confidence_index import compute_confidence_index

from fordead.visualisation.create_timelapse import create_timelapse
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

from fordead.import_data import TileInfo

from pathlib import Path
import argparse
import time
import datetime


def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--main_directory", dest = "main_directory",type = str, help = "Dossier contenant les dossiers des tuiles")
    parser.add_argument('-t', '--tuiles', nargs='+',default = ["ZoneEtude"], help="Liste des tuiles à analyser ex : -t T31UGP T31UGQ")
    parser.add_argument("--extent_shape_path", dest = "extent_shape_path",type = str,default = None, help = "Path of shapefile used as extent of detection")
    
    parser.add_argument("-i", "--sentinel_directory", dest = "sentinel_directory",type = str, help = "Path of the directory with a directory containing Sentinel data for each tile ")
    parser.add_argument("-f", "--forest_mask_source", dest = "forest_mask_source",type = str,default = "BDFORET", help = "Source of the forest mask, accepts 'BDFORET', 'OSO', the path to a binary raster with the extent and resolution of the computed area, or None in which case all pixels will be considered valid")
    parser.add_argument("-c", "--lim_perc_cloud", dest = "lim_perc_cloud",type = float,default = 0.3, help = "Maximum cloudiness at the tile or zone scale, used to filter used SENTINEL dates")
    parser.add_argument("--vi", dest = "vi",type = str,default = "CRSWIR", help = "Chosen vegetation index")
    parser.add_argument("-s", "--threshold_anomaly", dest = "threshold_anomaly",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("--nb_min_date", dest = "nb_min_date",type = int,default = 10, help = "Nombre minimum de dates valides pour modéliser l'indice de végétation")
    parser.add_argument('--ignored_period', nargs='+',default = None, help="Period whose date to ignore (format 'MM-DD', ex : --ignored_period 11-01 05-01")

    parser.add_argument("--dep_path", dest = "dep_path",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/Departements/departements-20140306-100m.shp", help = "Path to shapefile containg departements with code insee. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("--bdforet_dirpath", dest = "bdforet_dirpath",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/BDFORET", help = "Path to directory containing BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("--list_forest_type", dest = "list_forest_type", nargs='+',default = ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], help = "List of forest types to be kept in the forest mask, corresponds to the CODE_TFV of the BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("--path_oso", dest = "path_oso",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/OCS_2017_CESBIO.tif", help = "Path to soil occupation raster, only used if forest_mask_source = 'OSO' ")
    parser.add_argument("--list_code_oso", dest = "list_code_oso",type = str,default = [17], help = "List of values used to filter the soil occupation raster. Only used if forest_mask_source = 'OSO'")

    parser.add_argument("--sentinel_source", dest = "sentinel_source",type = str,default = "THEIA", help = "Source des données parmi 'THEIA' et 'Scihub' et 'PEPS'")
    parser.add_argument("--apply_source_mask", dest = "apply_source_mask", action="store_true",default = False, help = "If activated, applies the mask from SENTINEL-data supplier")
    parser.add_argument("--soil_detection", dest = "soil_detection", action="store_true",default = False, help = "If activated, detects bare ground")
    parser.add_argument("--min_last_date_training", dest = "min_last_date_training",type = str,default = "2018-01-01", help = "Première date de la détection")
    parser.add_argument("--max_last_date_training", dest = "max_last_date_training",type = str,default = "2018-06-01", help = "Dernière date pouvant servir pour l'apprentissage")
    
    parser.add_argument("--start_date_results", dest = "start_date_results",type = str,default = '2015-06-23', help = "Date de début pour l'export des résultats")
    parser.add_argument("--end_date_results", dest = "end_date_results",type = str,default = "2022-01-01", help = "Date de fin pour l'export des résultats")
    parser.add_argument("--results_frequency", dest = "results_frequency",type = str,default = 'M', help = "Frequency used to aggregate results, if value is 'sentinel', then periods correspond to the period between sentinel dates used in the detection, or it can be the frequency as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)")
    parser.add_argument("--multiple_files", dest = "multiple_files", action="store_true",default = False, help = "If activated, one shapefile is exported for each period containing the areas in decline at the end of the period. Else, a single shapefile is exported containing declined areas associated with the period of decline")

    parser.add_argument("--correct_vi", dest = "correct_vi", action="store_true",default = False, help = "If True, corrects vi using large scale median vi")
    # parser.add_argument('--threshold_list', nargs='+',default = [0.2, 0.265], help="Liste des seuils utilisés pour classer les stades de dépérissement par discrétisation de l'indice de confiance")
    # parser.add_argument('--classes_list', nargs='+',default = ["Faible anomalie","Forte anomalie"], help="Liste des noms des classes pour la discrétisation de l'indice de confiance. Si threshold_list a une longueur n, classes_list doit avoir une longueur n+1")

    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

def process_tiles(main_directory, sentinel_directory, tuiles, forest_mask_source, extent_shape_path,ignored_period,
                  dep_path, bdforet_dirpath, list_forest_type, path_oso, list_code_oso, #compute_forest_mask arguments
                  lim_perc_cloud, vi, sentinel_source, apply_source_mask, soil_detection, #compute_masked_vegetationindex arguments
                  min_last_date_training, max_last_date_training, nb_min_date,#Train_model arguments
                  threshold_anomaly,
                  start_date_results, end_date_results, results_frequency, multiple_files,
                  correct_vi):

    # sentinel_directory = "D:/Documents/Deperissement/FORMATION_SANTE_FORETS/A_DATA/RASTER/SERIES_SENTINEL"
    # main_directory = "D:/Documents/Deperissement/Output"    
    # soil_detection = False
    
    sentinel_directory = Path(sentinel_directory)
    main_directory = Path(main_directory)
    logpath = main_directory / (datetime.datetime.now().strftime("%Y-%m-%d-%HH%Mm%Ss") + ".txt")
    file = open(logpath, "w") 
    file.close()
    
    for tuile in tuiles:
        print(tuile)
        file = open(logpath, "a") 
        file.write("Tuile : " + tuile + "\n") ; start_time = time.time()
        file.close()
        
        start_time = time.time()
        
        compute_masked_vegetationindex(input_directory = sentinel_directory / tuile,
                                       data_directory = main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile,
                                       lim_perc_cloud = lim_perc_cloud, vi = vi,
                                       sentinel_source = sentinel_source, apply_source_mask = apply_source_mask,
                                       extent_shape_path = extent_shape_path,
                                       soil_detection = soil_detection,
                                       ignored_period = ignored_period)
        file = open(logpath, "a") 
        file.write("compute_masked_vegetationindex : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
        
# =====================================================================================================================

        compute_forest_mask(data_directory = main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile,
                            forest_mask_source = forest_mask_source,
                            dep_path = dep_path,
                            bdforet_dirpath = bdforet_dirpath,
                            list_forest_type = list_forest_type,
                            path_oso = path_oso,
                            list_code_oso = list_code_oso)
        file = open(logpath, "a") 
        file.write("compute_forest_mask : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================
            
        train_model(data_directory=main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile,
                    max_last_date_training = max_last_date_training,
                    nb_min_date = nb_min_date, correct_vi = correct_vi)
        file = open(logpath, "a")
        file.write("train_model : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
# =====================================================================================================================    

        decline_detection(data_directory=main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile, 
                                          threshold_anomaly = threshold_anomaly)
        file = open(logpath, "a")
        file.write("decline_detection : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()

# # =====================================================================================================================
        
        file = open(logpath, "a")
        compute_confidence_index(main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile, 
                                threshold_list = [0.2,0.265],
                                classes_list = ["1-Faible anomalie","2-Moyenne anomalie","3-Forte anomalie"],
                                chunks = 1280)
        file.write("Classify declining area : " + str(time.time() - start_time) + "\n\n") ; start_time = time.time()
        file.close()
        
# # =====================================================================================================================

        export_results(
            data_directory = main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile,
            start_date = start_date_results,
            end_date = end_date_results,
            frequency= results_frequency,
            multiple_files = multiple_files,
            intersection_confidence_class = True
            )



        # create_timelapse(data_directory = main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile,
        #                   shape_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/" + tuile + ".shp", 
        #                   obs_terrain_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/ObservationsTerrain/ValidatedScolytes.shp",
        #                   name_column = "id", max_date = None, zip_results = True)
        # vi_series_visualisation(data_directory = main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile, ymin = 0, ymax = 2)
        # vi_series_visualisation(data_directory = main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile, ymin = 0, ymax = 2, shape_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/points_visualisation.shp")

        
    tile = TileInfo(main_directory / Path(extent_shape_path).stem if extent_shape_path is not None else main_directory / tuile)
    tile = tile.import_info()
    file = open(logpath, "a")
    for parameter in tile.parameters:
        file.write(parameter + " : " +  str(tile.parameters[parameter]) + "\n")
    file.close()

if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    process_tiles(**dictArgs)

