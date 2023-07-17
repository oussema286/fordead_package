# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 18:55:28 2023

@author: Raphael Dutrieux
"""

import time
import click
from pathlib import Path
from itertools import product


from fordead.validation_module import get_args, filter_args, combine_validation_results, get_test_id, get_args_dataframe
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe
from fordead.validation.dieback_detection_from_dataframe import dieback_detection_from_dataframe



@click.command(name='sensitivity_analysis')
# @click.option("--testing_directory", type = str,default = None, help = "Path of the directory containing Sentinel-2 data.", show_default=True)
# @click.option("--export_path", type = str,default = None, help = "Path to write csv file with extracted reflectance", show_default=True)
# @click.option("-t","--tile_selection", multiple=True, type = str, default = None, help = "List of tiles from which to extract reflectance (ex : -t T31UFQ -t T31UGQ). If None, all tiles are extracted.", show_default=True)
# @click.option("--sentinel_source", type = str,default = "THEIA", help = "", show_default=True)
def cli_sensitivity_analysis():
    """
    
    \f

    """
    
    sensitivity_analysis()



                                   
                                   
def sensitivity_analysis(testing_directory, reflectance_path, extracted_cloudiness_path, args_to_test, update_masked_vi = False, overwrite = True, name_column = "id"):
    """
    

    Parameters
    ----------
    testing_directory : str
        DESCRIPTION.
    reflectance_path : str
        DESCRIPTION.
    extracted_cloudiness_path : str
        DESCRIPTION.
    args_to_test : dict or str
        DESCRIPTION.
    update_masked_vi : bool, optional
        DESCRIPTION. The default is False.
    overwrite : bool, optional
        DESCRIPTION. The default is True.
    name_column : str, optional
        DESCRIPTION. The default is "id".



    """
    
    
    testing_directory = Path(testing_directory)
    test_info_path = testing_directory / "test_info.csv"

    args_dict = get_args(args_to_test)
    
    for combs in product(*args_dict.values()):
        print(combs)
        args_dataframe = get_args_dataframe(dict(zip(args_dict.keys(), combs)))
        test_id = get_test_id(test_info_path, args_dataframe)
    
        if test_id is not None:
        
            if overwrite:
                dir_path = testing_directory / "last_test_directory"
            else:
                dir_path = testing_directory / '__'.join([list(args_dict.keys())[i] + "_" + str(combs[i]) for i in range(len(combs))])
     
            dir_path.mkdir(parents=True, exist_ok=True) 
    
            masked_vi_path = dir_path / "masked_vi.csv"
            pixel_info_path = dir_path / "pixel_info.csv"
            periods_path = dir_path / "periods.csv"
            
            mask_vi_from_dataframe(reflectance_path = reflectance_path,
                                    masked_vi_path = masked_vi_path,
                                    periods_path = periods_path,
                                    name_column = name_column,
                                    cloudiness_path = extracted_cloudiness_path,
                                    **filter_args(mask_vi_from_dataframe, args_dict, combs))
         
            
            train_model_from_dataframe(masked_vi_path = masked_vi_path,
                                        pixel_info_path = pixel_info_path,
                                        periods_path = periods_path,
                                        name_column = name_column,
                                        **filter_args(train_model_from_dataframe, args_dict, combs)
                                        )
            
            # train_model_from_dataframe(masked_vi_path = masked_vi_path,
            #                            export_path = pixel_info_path,
            #                            name_column = name_column
            #                            )
            
            dieback_detection_from_dataframe(masked_vi_path = masked_vi_path, 
                                             pixel_info_path = pixel_info_path, 
                                             periods_path = periods_path, 
                                             name_column = name_column,
                                             update_masked_vi = update_masked_vi,
                                             **filter_args(dieback_detection_from_dataframe, args_dict, combs))
            
            # export_csv(data_directory = dir_path / str(area_name),
            #             obs_shape = obs_area, name_column = name_column)
            # additional_output(masked_vi_path = masked_vi_path,
            #                                   pixel_info_path = pixel_info_path,
            #                                   periods_path = periods_path,
            #                                   export_path = additional_data_path,
            #                                   name_column = name_column)

                
            combine_validation_results(csv_path_list = [pixel_info_path, 
                                                        periods_path],
                                       merged_csv_path_list = [testing_directory / "merged_pixel_info.csv", 
                                                        testing_directory / "merged_periods.csv"],
                                       test_info_path = test_info_path,
                                       args_dataframe = args_dataframe, test_id = test_id)

    
if __name__ == '__main__':
    start_time_debut = time.time()
    # args_to_test = {"stress_index_mode" : ["mean","weighted_mean"], "threshold_anomaly" : [0.15,0.16], "list_bands" :  ["B2","B3","B4", "B8A", "B11","B12"]}
    args_to_test = {"threshold_anomaly" : [0.16], 
                    "list_bands" :  [["B2","B3","B4", "B8A", "B11","B12"]], 
                    "vi" : ["CRSWIR"]}

    # args_to_test = "D:/fordead/Data/Validation/results_from_raster/Feuillu/args_dict.txt"
    
    sensitivity_analysis(testing_directory = "D:/fordead/fordead_data/output",
                       reflectance_path = "D:/fordead/fordead_data/output/reflectance_tuto.csv",
                       extracted_cloudiness_path = "D:/fordead/fordead_data/output/cloudiness_tuto.csv",
                       # tiles = ["T31UGP"],
                       args_to_test = args_to_test,
                       overwrite = True)
    
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))