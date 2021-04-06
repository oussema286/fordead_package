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

dep_path = "/mnt/fordead/Data/Vecteurs/Departements/departements-20140306-100m.shp"
tuiles = ["T31UFQ", "T31UFR", "T31UGP", "T31UGQ", "T31TGL"]
sentinel_directory = "/mnt/fordead/Data/SENTINEL/"
bdforet_dirpath = "/mnt/fordead/Data/Vecteurs/BDFORET"


correct_vi = True
for vi in ["NDWI"]:
    for threshold_anomaly in [0.12,0.13,0.14]:
        main_directory = "/mnt/fordead/Out/"+vi
        if correct_vi:
            name_dir = vi+"_"+str(threshold_anomaly)
        else:
            name_dir = vi+"_"+str(threshold_anomaly)+"_corrected"
        Path(main_directory).mkdir(parents=True, exist_ok=True)   
        process_tiles(main_directory = main_directory, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                        dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                        lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                        min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
                        threshold_anomaly = threshold_anomaly,
                        start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                        correct_vi = correct_vi, validation = True)
        copy_validation_data(main_directory, tuiles)
        shutil.copytree(main_directory+"/All_Results", "/mnt/fordead/Out/"+name_dir) 
        for tile in tuiles:
            shutil.copytree(main_directory+"/"+tile+"/Results", "/mnt/fordead/Out/"+name_dir+"/"+tile)
        
correct_vi = True
for vi in ["CRSWIR"]:
    for threshold_anomaly in [0.14,0.16]:
        main_directory = "/mnt/fordead/Out/"+vi
        if correct_vi:
            name_dir = vi+"_"+str(threshold_anomaly)
        else:
            name_dir = vi+"_"+str(threshold_anomaly)+"_corrected"
        Path(main_directory).mkdir(parents=True, exist_ok=True)   
        process_tiles(main_directory = main_directory, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                        dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                        lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                        min_last_date_training = "2018-01-01", max_last_date_training = "2018-08-01", nb_min_date = 11,#Train_model arguments
                        threshold_anomaly = threshold_anomaly,
                        start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                        correct_vi = correct_vi, validation = True)
        copy_validation_data(main_directory, tuiles)
        shutil.copytree(main_directory+"/All_Results", "/mnt/fordead/Out/"+name_dir) 
        for tile in tuiles:
            shutil.copytree(main_directory+"/"+tile+"/Results", "/mnt/fordead/Out/"+name_dir+"/"+tile)
            
correct_vi = False
vi = "CRSWIR"
threshold_anomaly = 0.16
for max_last_date_training in ["2018-06-01", "2018-08-01", "2018-10-01"]:
    main_directory = "/mnt/fordead/Out/"+vi
    name_dir = vi+"_"+max_last_date_training
    Path(main_directory).mkdir(parents=True, exist_ok=True)   
    process_tiles(main_directory = main_directory, sentinel_directory = sentinel_directory, tuiles = tuiles, forest_mask_source = "BDFORET", extent_shape_path = None,
                    dep_path = dep_path, bdforet_dirpath = bdforet_dirpath, list_forest_type =  ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], path_oso = None, list_code_oso = None, #compute_forest_mask arguments
                    lim_perc_cloud = 0.4, vi = vi, sentinel_source = "THEIA", apply_source_mask = False, #compute_masked_vegetationindex arguments
                    min_last_date_training = "2018-01-01", max_last_date_training = max_last_date_training, nb_min_date = 11,#Train_model arguments
                    threshold_anomaly = threshold_anomaly,
                    start_date_results = '2015-06-23', end_date_results = '2022-06-23', results_frequency = "M", multiple_files = False,
                    correct_vi = correct_vi, validation = True)
    copy_validation_data(main_directory, tuiles)
    shutil.copytree(main_directory+"/All_Results", "/mnt/fordead/Out/"+name_dir) 
    for tile in tuiles:
        shutil.copytree(main_directory+"/"+tile+"/Results", "/mnt/fordead/Out/"+name_dir+"/"+tile)
            