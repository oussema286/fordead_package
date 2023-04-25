# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 18:55:28 2023

@author: Raphael Dutrieux
"""

import time
import click
from pathlib import Path

from fordead.validation import get_params

@click.command(name='testing_parameters')
# @click.option("--testing_directory", type = str,default = None, help = "Path of the directory containing Sentinel-2 data.", show_default=True)
# @click.option("--export_path", type = str,default = None, help = "Path to write csv file with extracted reflectance", show_default=True)
# @click.option("-t","--tile_selection", multiple=True, type = str, default = None, help = "List of tiles from which to extract reflectance (ex : -t T31UFQ -t T31UGQ). If None, all tiles are extracted.", show_default=True)
# @click.option("--sentinel_source", type = str,default = "THEIA", help = "", show_default=True)
def cli_testing_parameters():
    """
    
    \f

    """
    
    testing_parameters()


def testing_parameters(testing_directory, tiles, reflectance_path, 
                       params_to_test, 
                       overwrite = True, name_column = "id"):
    
    
    testing_directory = Path(testing_directory)
    

    param_dict = get_params(params_to_test)
     
    for area_name in np.unique(obs_shape.area_name):
        obs_area = obs_shape[obs_shape.area_name == area_name] 
        # obs=obs_shape.iloc[obs_index:(obs_index+1)]
        obs_area.to_file(temp_obs_path)
        
        comb_param = get_params(params_to_test)
        for combs in product(*comb_param.values()):
            print(combs)
            
            if overwrite:
                dir_path = testing_directory / "last_test_directory"
            else:
                dir_path = testing_directory / '__'.join([list(comb_param.keys())[i] + "_" + str(combs[i]) for i in range(len(combs))])
     
            dir_path.mkdir(parents=True, exist_ok=True) 
    
    
    
            mask_vi_from_dataframe(reflectance_path = reflectance_path,
                                       export_path = masked_vi_path,
                                       name_column = name_column,
                                       vi = vi,
                                       cloudiness_path = extracted_cloudiness_path,
                                       lim_perc_cloud = 0.45,
                                       soil_detection = True,
                                       formula_mask = "(B2 >= 700)",
                                       path_dict_vi = None,
                                       list_bands =  ["B2","B3","B4", "B8A", "B11","B12"],
                                       apply_source_mask = False,
                                       sentinel_source = "THEIA")
            
            print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut)) ; start_time_debut = time.time()
            
            
            train_model_from_dataframe(masked_vi_path = masked_vi_path,
                                       export_path = pixel_info_path,
                                       name_column = name_column,
                                       soil_detection = True,
                                       min_last_date_training = "2018-01-01",
                                       max_last_date_training = "2018-06-01",
                                       nb_min_date = 10
                                       )
            print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut)) ; start_time_debut = time.time()
            
            dieback_detection_from_dataframe(masked_vi_path = masked_vi_path, 
                                             pixel_info_path = pixel_info_path, 
                                             export_path = periods_path, 
                                             name_column = name_column,
                                             threshold_anomaly = 0.16, 
                                             max_nb_stress_periods = 5, 
                                             vi = vi)
            print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut)) ; start_time_debut = time.time()
            
            # export_csv(data_directory = dir_path / str(area_name),
            #             obs_shape = obs_area, name_column = name_column)
            
            # combine_validation_results(data_directory = dir_path / str(area_name), target_directory = testing_directory / str("Compared_validation"))


              
    #DELETE OBS_TEMP
    
if __name__ == '__main__':
    start_time_debut = time.time()
    params_to_test = {"stress_index_mode" : ["mean","weighted_mean"], "threshold_anomaly" : [0.15,0.16]}
    # params_to_test = "D:/fordead/Data/Validation/results_from_raster/Feuillu/param_dict.txt"
    
    
    testing_parameters(testing_directory = "D:/fordead/fordead_data/output",
                       input_directory = "D:/fordead/fordead_data/sentinel_data/validation_tutorial/sentinel_data",
                       reflectance_path = "D:/fordead/fordead_data/output/reflectance_tuto.csv",
                       tiles = ["T31UGP"],
                       params_to_test = params_to_test,
                       overwrite = True)
    
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))