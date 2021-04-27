# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 12:09:05 2021

@author: admin
"""


from examples.process_tile import process_tiles
from examples.copy_validation_data import copy_validation_data
import shutil
import os
from pathlib import Path
from fordead.visualisation.create_timelapse import create_timelapse
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

dep_path = "/mnt/fordead/Data/Vecteurs/Departements/departements-20140306-100m.shp"
sentinel_directory = "/mnt/fordead/Data/SENTINEL/"
bdforet_dirpath = "/mnt/fordead/Data/Vecteurs/BDFORET"


# correct_vi = True
# for vi in ["NDWI"]:
#     for threshold_anomaly in [0.1]:
#         main_directory = "/mnt/fordead/Out/"+vi
#         if correct_vi:
#             name_dir = vi+"_"+str(threshold_anomaly)+"_corrected"
#         else:
#             name_dir = vi+"_"+str(threshold_anomaly)
#         Path(main_directory).mkdir(parents=True, exist_ok=True)   
#         process_tiles(main_directory = main_directory, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
#                         dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
#                         lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
#                         min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
#                         threshold_anomaly = threshold_anomaly,
#                         start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
#                         correct_vi = correct_vi, validation = True)
#         copy_validation_data(main_directory, tuiles)
#         shutil.copytree(main_directory+"/All_Results", "/mnt/fordead/Out/"+name_dir) 
#         for tile in tuiles:
#             shutil.copytree(main_directory+"/"+tile+"/Results", "/mnt/fordead/Out/"+name_dir+"/"+tile)
# correct_vi = False
# for vi in ["NDWI"]:
#     for threshold_anomaly in [0.15]:
#         main_directory = "/mnt/fordead/Out/"+vi
#         if correct_vi:
#             name_dir = vi+"_"+str(threshold_anomaly)+"_corrected"
#         else:
#             name_dir = vi+"_"+str(threshold_anomaly)
#         Path(main_directory).mkdir(parents=True, exist_ok=True)   
#         process_tiles(main_directory = main_directory, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
#                         dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
#                         lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
#                         min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
#                         threshold_anomaly = threshold_anomaly,
#                         start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
#                         correct_vi = correct_vi, validation = True)
#         copy_validation_data(main_directory, tuiles)
#         shutil.copytree(main_directory+"/All_Results", "/mnt/fordead/Out/"+name_dir) 
#         for tile in tuiles:
#             shutil.copytree(main_directory+"/"+tile+"/Results", "/mnt/fordead/Out/"+name_dir+"/"+tile)
# correct_vi = True
# for vi in ["CRSWIR"]:
#     for threshold_anomaly in [0.14,0.16]:
#         main_directory = "/mnt/fordead/Out/"+vi
#         if correct_vi:
#             name_dir = vi+"_"+str(threshold_anomaly)+"_corrected"
#         else:
#             name_dir = vi+"_"+str(threshold_anomaly)
#         Path(main_directory).mkdir(parents=True, exist_ok=True)   
#         process_tiles(main_directory = main_directory, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
#                         dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
#                         lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
#                         min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
#                         threshold_anomaly = threshold_anomaly,
#                         start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
#                         correct_vi = correct_vi, validation = True)
#         copy_validation_data(main_directory, tuiles)
#         shutil.copytree(main_directory+"/All_Results", "/mnt/fordead/Out/"+name_dir) 
#         for tile in tuiles:
#             shutil.copytree(main_directory+"/"+tile+"/Results", "/mnt/fordead/Out/"+name_dir+"/"+tile)
            

            

vi = "CRSWIR" ; threshold_anomaly = 0.16 ; correct_vi = False
tuiles = ["T31UGP"]
if correct_vi:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)+"_corrected"
else:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)
Path(name_dir).mkdir(parents=True, exist_ok=True)   
process_tiles(main_directory = name_dir, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
                threshold_anomaly = threshold_anomaly,
                start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                correct_vi = correct_vi, validation = True)
create_timelapse(data_directory = Path(name_dir) / tuiles[0] , x = 803986, y= 5346917, buffer = 1000)
vi_series_visualisation(data_directory = Path(name_dir) / tuiles[0], ymin = 0, ymax = 2,chunks = 1280, shape_path = "/mnt/fordead/Data/Vecteurs/points_visualisation.shp")


vi = "CRSWIR" ; threshold_anomaly = 0.14 ; correct_vi = True
if correct_vi:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)+"_corrected"
else:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)
Path(name_dir).mkdir(parents=True, exist_ok=True)   
process_tiles(main_directory = name_dir, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
                threshold_anomaly = threshold_anomaly,
                start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                correct_vi = correct_vi, validation = True)
create_timelapse(data_directory = Path(name_dir) / tuiles[0] , x = 803986, y= 5346917, buffer = 1000)
vi_series_visualisation(data_directory = Path(name_dir) / tuiles[0], ymin = 0, ymax = 2,chunks = 1280, shape_path = "/mnt/fordead/Data/Vecteurs/points_visualisation.shp")


vi = "NDWI" ; threshold_anomaly = 0.14 ; correct_vi = False
if correct_vi:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)+"_corrected"
else:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)
Path(name_dir).mkdir(parents=True, exist_ok=True)   
process_tiles(main_directory = name_dir, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
                threshold_anomaly = threshold_anomaly,
                start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                correct_vi = correct_vi, validation = True)
create_timelapse(data_directory = Path(name_dir) / tuiles[0] , x = 803986, y= 5346917, buffer = 1000)
vi_series_visualisation(data_directory = Path(name_dir) / tuiles[0], ymin = 0, ymax = 2,chunks = 1280, shape_path = "/mnt/fordead/Data/Vecteurs/points_visualisation.shp")

vi = "NDWI" ; threshold_anomaly = 0.12 ; correct_vi = True
if correct_vi:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)+"_corrected"
else:
    name_dir = "/mnt/fordead/Out/"+vi+"_"+str(threshold_anomaly)
Path(name_dir).mkdir(parents=True, exist_ok=True)   
process_tiles(main_directory = name_dir, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
                threshold_anomaly = threshold_anomaly,
                start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                correct_vi = correct_vi, validation = True)
create_timelapse(data_directory = Path(name_dir) / tuiles[0] , x = 803986, y= 5346917, buffer = 1000)
vi_series_visualisation(data_directory = Path(name_dir) / tuiles[0], ymin = 0, ymax = 2,chunks = 1280, shape_path = "/mnt/fordead/Data/Vecteurs/points_visualisation.shp")




correct_vi = False
vi = "CRSWIR"
threshold_anomaly = 0.16
tuiles = ["T31UFQ", "T31UFR", "T31UGP", "T31UGQ", "T31TGL"]
for nb_min_date in [12,13]:
    for max_last_date_training in ["2018-08-01"]:
        main_directory = "/mnt/fordead/Out/"+vi
        name_dir = vi+"_"+max_last_date_training+"_"+str(nb_min_date)
        Path(main_directory).mkdir(parents=True, exist_ok=True)   
        process_tiles(main_directory = main_directory, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                        dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                        lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                        min_last_date_training = "2018-01-01", max_last_date_training = max_last_date_training, nb_min_date = nb_min_date,#Train_model arguments
                        threshold_anomaly = threshold_anomaly,
                        start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                        correct_vi = correct_vi, validation = True)
        copy_validation_data(main_directory, tuiles)
        shutil.copytree(main_directory+"/All_Results", "/mnt/fordead/Out/"+name_dir) 
        for tile in tuiles:
            shutil.copytree(main_directory+"/"+tile+"/Results", "/mnt/fordead/Out/"+name_dir+"/"+tile)
            