# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:15 2020

@author: Raphaël Dutrieux
"""
#%% =============================================================================
#   LIBRAIRIES
# =============================================================================

import argparse
from fordead.ImportData import import_stackedmaskedVI, TileInfo
from fordead.ModelVegetationIndex import get_detection_dates, model_vi
from fordead.writing_data import write_tif


def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str, help = "Dossier avec les indices de végétations et les masques")
    parser.add_argument("--nb_min_date", dest = "nb_min_date",type = int,default = 10, help = "Minimum number of valid dates to compute a vegetation index model for the pixel")
    parser.add_argument("-s", "--min_last_date_training", dest = "min_last_date_training",type = str,default = "2018-01-01", help = "Première date de la détection")
    parser.add_argument("-e", "--max_last_date_training", dest = "max_last_date_training",type = str,default = "2018-06-01", help = "Dernière date pouvant servir pour l'apprentissage")

    parser.add_argument("--path_vi", dest = "path_vi",type = str,default = None, help = "Path of directory containing vegetation indices for each date. If None, the information has to be saved from a previous step")    
    parser.add_argument("--path_masks", dest = "path_masks",type = str,default = None, help = "Path of directory containing masks for each date.  If None, the information has to be saved from a previous step")    
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    
    return dictArgs


def train_model(
    data_directory,
    nb_min_date = 10,
    min_last_date_training="2018-01-01",
    max_last_date_training="2018-06-01",
    path_vi=None,
    path_masks = None,
    ):
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    
    if path_vi==None : path_vi = tile.paths["VegetationIndexDir"]
    if path_masks==None : path_masks = tile.paths["MaskDir"]
    
    tile.add_parameters({"nb_min_date" : nb_min_date, "min_last_date_training" : min_last_date_training, "max_last_date_training" : max_last_date_training})
    if tile.parameters["Overwrite"] : tile.delete_dirs("coeff_model","AnomaliesDir","state_decline", "valid_area_mask" ,"periodic_results_decline","result_files","timelapse","series") #Deleting previous training and detection results if they exist

    #Create missing directories and add paths to TileInfo object
    tile.add_path("coeff_model", tile.data_directory / "DataModel" / "coeff_model.tif")
    tile.add_path("first_detection_date_index", tile.data_directory / "DataModel" / "first_detection_date_index.tif")
    tile.add_path("valid_area_mask", tile.data_directory / "ForestMask" / "valid_area_mask.tif")
    
    if tile.paths["coeff_model"].exists():
        print("Model already calculated")
    else:
        print("Computing model")
        tile.getdict_paths(path_vi = path_vi,
                            path_masks = path_masks)
        
        # Import des index de végétations et des masques
        stack_vi, stack_masks = import_stackedmaskedVI(tile, max_last_date_training=max_last_date_training, chunks = 1280)
   
        detection_dates, first_detection_date_index = get_detection_dates(stack_masks,
                                              min_last_date_training = min_last_date_training,
                                              nb_min_date = 10)
        
        
        #Fusion du masque forêt et des zones non utilisables par manque de données
        valid_area_mask = first_detection_date_index!=0
        
        # Modéliser le CRSWIR tout en retirant outliers
        stack_masks = stack_masks | detection_dates #Masking data not used in training
        coeff_model = model_vi(stack_vi, stack_masks)
        
        #Ecrire rasters de l'index de la dernière date utilisée, les coefficients, la zone utilisable
        write_tif(first_detection_date_index,stack_vi.attrs, tile.paths["first_detection_date_index"],nodata=0)
        write_tif(coeff_model,stack_vi.attrs, tile.paths["coeff_model"])
        write_tif(valid_area_mask,stack_vi.attrs, tile.paths["valid_area_mask"],nodata=0)
        #Save the TileInfo object
        tile.save_info()

    
if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    # start_time = time.time()
    train_model(**dictArgs)
    # print("Temps d execution : %s secondes ---" % (time.time() - start_time))


