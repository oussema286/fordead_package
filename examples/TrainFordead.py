# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:21:15 2020

@author: Raphaël Dutrieux
"""
#%% =============================================================================
#   LIBRAIRIES
# =============================================================================

import argparse
# from pathlib import Path
from fordead.ImportData import import_forest_mask, import_stackedmaskedVI, TileInfo
from fordead.ModelVegetationIndex import get_last_training_date, model_vi
from fordead.writing_data import write_tif
import time

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str,default = "G:/Deperissement/Out/PackageVersion/ZoneTest", help = "Dossier avec les indices de végétations et les masques")
    parser.add_argument("-s", "--threshold_outliers", dest = "threshold_outliers",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-k", "--remove_outliers", dest = "remove_outliers", action="store_false",default = True, help = "Si activé, garde les outliers dans les deux premières années")
    parser.add_argument("-l", "--min_last_date_training", dest = "min_last_date_training",type = str,default = "2018-01-01", help = "Première date de la détection")
    parser.add_argument("-g", "--date_lim_training", dest = "date_lim_training",type = str,default = "2018-06-01", help = "Dernière date pouvant servir pour l'apprentissage")

    parser.add_argument("-v", "--path_vi", dest = "path_vi",type = str,default = None, help = "Première date de la détection")    
    parser.add_argument("-m", "--path_masks", dest = "path_masks",type = str,default = None, help = "Première date de la détection")    
    parser.add_argument("-f", "--path_forestmask", dest = "path_forestmask",type = str,default = None, help = "Première date de la détection")    
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    
    return dictArgs


def train_model(
    data_directory,
    threshold_outliers=0.16,
    remove_outliers=True,
    min_last_date_training="2018-01-01",
    date_lim_training="2018-06-01",
    path_vi=None,
    path_masks = None,
    path_forestmask = None
    ):

    data_directory="G:/Deperissement/Out/PackageVersion/ZoneTest"
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    
    if path_vi==None : path_vi = tile.paths["VegetationIndexDir"]
    if path_masks==None : path_masks = tile.paths["MaskDir"]
    if path_forestmask == None : path_forestmask = tile.paths["ForestMask"] #Paths are imported from previous TileInfo if not given as arguments
    
    tile.add_parameters({"threshold_outliers" : threshold_outliers, "remove_outliers" : remove_outliers, "min_last_date_training" : min_last_date_training, "date_lim_training" : date_lim_training})
    # tile.delete_results()
    
    tile.getdict_paths(path_vi = path_vi,
                        path_masks = path_masks,
                        path_forestmask = path_forestmask)
    
    # Import du masque forêt
    forest_mask = import_forest_mask(tile.paths["ForestMask"])
    
    # Import des index de végétations et des masques
    stack_vi, stack_masks = import_stackedmaskedVI(tile, date_lim_learning=date_lim_training)
    
    last_training_date=get_last_training_date(stack_masks,
                                          min_last_date_training = min_last_date_training,
                                          nb_min_date = 10)
    
    #Fusion du masque forêt et des zones non utilisables par manque de données
    used_area_mask = forest_mask.where(last_training_date!=0,False)

    # Modéliser le CRSWIR tout en retirant outliers
    coeff_model = model_vi(stack_vi, stack_masks,used_area_mask, last_training_date,
                           threshold_outliers=threshold_outliers, remove_outliers=remove_outliers)
        
    #Create missing directories and add paths to TileInfo object
    tile.add_path("coeff_model", tile.data_directory / "DataModel" / "coeff_model.tif")
    tile.add_path("last_training_date", tile.data_directory / "DataModel" / "Last_training_date.tif")
    tile.add_path("used_area_mask", tile.paths["ForestMask"].parent / "Used_area_mask.tif")

    #Ecrire rasters de l'index de la dernière date utilisée, les coefficients, la zone utilisable
    write_tif(last_training_date,stack_vi.attrs, tile.paths["last_training_date"],nodata=0)
    write_tif(coeff_model,stack_vi.attrs, tile.paths["coeff_model"])
    write_tif(used_area_mask,stack_vi.attrs, tile.paths["used_area_mask"],nodata=0)
    #Save the TileInfo object
    tile.save_info()

    
if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    start_time = time.time()
    train_model(**dictArgs)
    print("Temps d execution : %s secondes ---" % (time.time() - start_time))


