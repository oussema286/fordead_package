# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 12:02:24 2020

@author: Raphael Dutrieux
"""

from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.steps.step2_train_model import train_model
from fordead.steps.step3_dieback_detection import dieback_detection
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
from fordead.steps.step5_export_results import export_results

from fordead.visualisation.create_timelapse import create_timelapse
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

from fordead.import_data import TileInfo

from pathlib import Path
import time
import datetime
import gc
import geopandas as gpd



import click

@click.command(name='process_tiles')
@click.option("-i", "--sentinel_directory", required=True, type = click.Path(), help = "Path of the directory with a directory containing Sentinel data for each tile")
@click.option("-o", "--output_directory", required=True, type = click.Path(), help = "Output directory")
@click.option('-t', '--tiles', multiple=True, required=True, default = ["study_area"], help="List of tiles to process : -t T31UGP -t T31UGQ -t study_area")
@click.option("--extent_shape_path", type = click.Path(), default = None, help = "Path of shapefile used as extent of detection")
@click.option("-c", "--lim_perc_cloud", type = float, default = 0.3, help = "Maximum cloudiness at the tile or zone scale, used to filter used SENTINEL dates")
@click.option("--vi", type = str, default = "CRSWIR", help = "Chosen vegetation index")
@click.option("--compress_vi", is_flag=True, default = False, help = "If activated, stores the vegetation index as low-resolution floating-point data as small integers in a netCDF file. Uses less disk space but can lead to very small difference in results as the vegetation is rounded to three decimal places")
@click.option("-s", "--threshold_anomaly", type = float, default = 0.16, help = "Minimum threshold for anomaly detection")
@click.option("--nb_min_date", type = int, default = 10, help = "Minimum number of valid dates reqquired for modelling the vegetation index")
@click.option('--ignored_period', multiple=True, default = None, help="Period whose date to ignore (format 'MM-DD', ex : --ignored_period 11-01 05-01")
@click.option(" -f", "--forest_mask_source", type = str, default = "BDFORET", help = "Source of the forest mask, accepts 'BDFORET', 'OSO', the path to a vector file or a binary raster with the extent and resolution of the computed area, or None in which case all pixels will be considered valid")
@click.option("--dep_path", type = click.Path(), default = "/mnt/Data/Vecteurs/Departements/departements-20140306-100m.shp", help = "Path to shapefile containg departements with code insee. Optionnal, only used if forest_mask_source equals 'BDFORET'")
@click.option("--bdforet_dirpath", type = click.Path(), default = "/mnt/Data/Vecteurs/BDFORET", help = "Path to directory containing BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
@click.option("--list_forest_type", multiple = True, default = ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], help = "List of forest types to be kept in the forest mask, corresponds to the CODE_TFV of the BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
@click.option("--path_oso", type = click.Path(), default = "/mnt/fordead/Data/Classif_Seed_0_2021.tif", help = "Path to soil occupation raster, only used if forest_mask_source = 'OSO' ")
@click.option("--list_code_oso", type = str, default = [17], help = "List of values used to filter the soil occupation raster. Only used if forest_mask_source = 'OSO'")
@click.option("--sentinel_source", type = click.Choice(["THEIA", "Scihub", "PEPS"]), default = "THEIA", help = "Source of Sentinel data: 'THEIA', 'Scihub' or 'PEPS'")
@click.option("--apply_source_mask", is_flag=True, default = False, help = "If activated, applies the mask from SENTINEL-data supplier")
@click.option("--soil_detection", is_flag=True, default = False, help = "If activated, detects bare ground")
@click.option("--min_last_date_training", type = str, default = "2018-01-01", help = "First date that can be used for detection")
@click.option("--max_last_date_training", type = str, default = "2018-06-01", help = "Last date that can be used for training")
@click.option("--start_date_results", type = str, default = '2015-06-23', help = "Start date for results export")
@click.option("--end_date_results", type = str, default = "2022-01-01", help = "End date for results export")
@click.option("--results_frequency", type = str, default = 'M', help = "Frequency used to aggregate results, if value is 'sentinel', then periods correspond to the period between sentinel dates used in the detection, or it can be the frequency as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)")
@click.option("--multiple_files", is_flag=True, default = False, help = "If activated, one shapefile is exported for each period containing the areas suffering from dieback at the end of the period. Else, a single shapefile is exported containing diebackd areas associated with the period of dieback")
@click.option("--correct_vi", is_flag=True, default = False, help = "If True, corrects vi using large scale median vi")
@click.option("--stress_index_mode", type = click.Choice(['mean', 'weighted_mean']), default = "weighted_mean", help = "Chosen stress index, if 'mean', the index is the mean of the difference between the vegetation index and the predicted vegetation index for all unmasked dates after the first anomaly subsequently confirmed. If 'weighted_mean', the index is a weighted mean, where for each date used, the weight corresponds to the number of the date (1, 2, 3, etc...) from the first anomaly. If None, the stress periods are not detected, and no information is saved")
@click.option("--path_dict_vi", type = click.Path(), default = None, help = "Path of text file to add vegetation index formula, if None, only built-in vegetation indices can be used")
@click.option('--threshold_list', multiple=True, default = [0.2, 0.265], help="List of thresholds used to classify the levels of dieback by discretising the confidence index")
@click.option('--classes_list', multiple=True, default = ["1-Faible anomalie","2-Moyenne anomalie","3-Forte anomalie"], help="List of class names for discretising the confidence index. If threshold_list has length n, classes_list must have length n+1.")
def cli_process_tiles(**kwargs):
    """Apply full fordead processing to several tiles: compute_masked_vegetationindex > compute_forest_mask > train_model > dieback_detection > export_results
    """
    # execute only if run as a script
    process_tiles(**kwargs)

def process_tiles(output_directory, sentinel_directory, tiles=["study_area"], forest_mask_source="BDFORET", 
                  extent_shape_path=None, ignored_period=None,
                  dep_path=None, bdforet_dirpath=None, list_forest_type=["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"],
                  path_oso=None, list_code_oso=[17], #compute_forest_mask arguments
                  lim_perc_cloud=0.3, vi="CRSWIR", compress_vi=False, sentinel_source="THEIA",
                  apply_source_mask=False, soil_detection=False, #compute_masked_vegetationindex arguments
                  min_last_date_training="2018-01-01", max_last_date_training="2018-06-01", nb_min_date=10,#Train_model arguments
                  threshold_anomaly=0.16,
                  start_date_results="2015-06-23", end_date_results="2022-01-01",
                  results_frequency="M", multiple_files=False,
                  correct_vi=False, stress_index_mode="weighted_mean", path_dict_vi=None,
                  threshold_list=[0.2, 0.265], classes_list=["1-Faible anomalie","2-Moyenne anomalie","3-Forte anomalie"]):
    """
    Apply full fordead processing to several tiles: compute_masked_vegetationindex > compute_forest_mask > train_model > dieback_detection > export_results

    Parameters
    ----------
    output_directory : str
        Path of the output directory
    sentinel_directory : str
        Path of the directory with a directory containing Sentinel data for each tile
    tiles : list
        List of tiles to process
    forest_mask_source : str
        Source of the forest mask, accepts 'BDFORET', 'OSO', 
        the path to a binary raster with the extent and resolution of the computed area,
        or None in which case all pixels will be considered valid
    extent_shape_path : str
        Path of shapefile used as extent of detection
    ignored_period : list
        Period whose Sentinel dates to ignore (format 'MM-DD', ex : ["11-01","05-01"])
    dep_path : str
        Path to shapefile containg departements with code insee. Optionnal, only used if forest_mask_source equals 'BDFORET'
    bdforet_dirpath : str
        Path to directory containing BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'
    list_forest_type : list
        List of forest types to be kept in the forest mask, corresponds to the CODE_TFV of the BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'
    path_oso : str
        Path to soil occupation raster, only used if forest_mask_source = 'OSO'
    list_code_oso : list
        List of values used to filter the soil occupation raster. Only used if forest_mask_source = 'OSO'
    lim_perc_cloud : float
        Maximum cloudiness at the tile or zone scale, used to filter SENTINEL scenes
    vi : str
        Chosen vegetation index
    compress_vi : bool
        If True, stores the vegetation index as low-resolution floating-point data as small integers in a netCDF file.
        Uses less disk space but can lead to very small difference in results as the vegetation is rounded to three decimal places
    sentinel_source : str
        Source of Sentinel data: 'THEIA', 'Scihub' or 'PEPS'
    apply_source_mask : bool
        If True, applies the mask from SENTINEL-data provider
    soil_detection : bool
        If True, performs soil detection (bare ground)
    min_last_date_training : str
        First date that can be used for detection
    max_last_date_training : str
        Last date that can be used for training
    nb_min_date : int
        Minimum number of valid dates to compute a vegetation index model for the pixel
    threshold_anomaly : float
        Threshold for anomaly detection
    start_date_results : str
        Start date for results export
    end_date_results : str
        End date for results export
    results_frequency : str
        Frequency used to aggregate results, if value is 'sentinel',
        then periods correspond to the period between sentinel dates used in the detection,
        or it can be the frequency as used in pandas.date_range. 
        Examples 'M' (monthly), '3M' (three months), '15D' (fifteen days)
    multiple_files : bool
        If True, one shapefile is exported for each period containing
        the areas suffering from dieback at the end of the period.
        Else, a single shapefile is exported containing diebackd areas associated with the period of dieback
    correct_vi : bool
        If True, corrects the vegetation index for the forest mask
    stress_index_mode : str
        If 'mean', the index is the mean of the difference
        between the vegetation index and the predicted vegetation index
        for all unmasked dates after the first anomaly subsequently confirmed.
        If 'weighted_mean', the index is a weighted mean, where for each date used,
        the weight corresponds to the number of the date (1, 2, 3, etc...) from the first anomaly.
        If None, the stress periods are not detected, and no information is saved
    path_dict_vi : str
        Path of text file to add vegetation index formula, if None, only built-in vegetation indices can be used
    threshold_list : list
        List of thresholds used to classify the levels of dieback by discretising the confidence index
    classes_list : list
        List of class names for discretising the confidence index.
        If threshold_list has length n, classes_list must have length n+1.
    """
    
    sentinel_directory = Path(sentinel_directory)
    output_directory = Path(output_directory)
    logpath = output_directory / (datetime.datetime.now().strftime("%Y-%m-%d-%HH%Mm%Ss") + ".txt")
    file = open(logpath, "w") 
    file.close()
    
    # check if vector
    vector_path = None
    if forest_mask_source not in ["BDFORET", "OSO", None]:
        try:
            gpd.read_file(forest_mask_source)
            vector_path = forest_mask_source
            forest_mask_source = 'vector'
        except:
            pass

    for tile in tiles:
        data_directory = output_directory / tile
        print(tile)
        file = open(logpath, "a") 
        file.write("Tile : " + tile + "\n") ; start_time = time.time()
        file.close()
        
        start_time = time.time()
        
        compute_masked_vegetationindex(input_directory = sentinel_directory / tile,
                                       data_directory = data_directory,
                                       lim_perc_cloud = lim_perc_cloud,
                                       vi = vi,
                                       sentinel_source = sentinel_source,
                                       apply_source_mask = apply_source_mask,
                                       extent_shape_path = extent_shape_path,
                                       soil_detection = soil_detection,
                                       ignored_period = ignored_period,
                                       compress_vi = compress_vi,
                                       path_dict_vi = path_dict_vi)
        file = open(logpath, "a") 
        file.write("compute_masked_vegetationindex : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
        gc.collect()
        
# =====================================================================================================================

        compute_forest_mask(data_directory = data_directory,
                            forest_mask_source = forest_mask_source,
                            dep_path = dep_path,
                            bdforet_dirpath = bdforet_dirpath,
                            list_forest_type = list_forest_type,
                            path_oso = path_oso,
                            list_code_oso = list_code_oso,
                            vector_path=vector_path)
        
        file = open(logpath, "a") 
        file.write("compute_forest_mask : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
        gc.collect()
# =====================================================================================================================
            
        train_model(data_directory = data_directory,
                    min_last_date_training = min_last_date_training,
                    max_last_date_training = max_last_date_training,
                    nb_min_date = nb_min_date, correct_vi = correct_vi)
        file = open(logpath, "a")
        file.write("train_model : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
        gc.collect()
# =====================================================================================================================    

        dieback_detection(data_directory=data_directory, 
                                          threshold_anomaly = threshold_anomaly, stress_index_mode = stress_index_mode, path_dict_vi = path_dict_vi)
        file = open(logpath, "a")
        file.write("dieback_detection : " + str(time.time() - start_time) + "\n") ; start_time = time.time()
        file.close()
        gc.collect()
        
# # =====================================================================================================================

        export_results(
            data_directory = data_directory,
            start_date = start_date_results,
            end_date = end_date_results,
            frequency= results_frequency,
            multiple_files = multiple_files, 
            conf_threshold_list = threshold_list,
            conf_classes_list = classes_list
            )
        file = open(logpath, "a")
        file.write("Exporting results : " + str(time.time() - start_time) + "\n\n") ; start_time = time.time()
        file.close()
        gc.collect()

        # create_timelapse(data_directory = data_directory,
        #                   shape_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/" + tile + ".shp", 
        #                   obs_terrain_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/ObservationsTerrain/ValidatedScolytes.shp",
        #                   name_column = "id", max_date = None, zip_results = True)
        # vi_series_visualisation(data_directory = data_directory, ymin = 0, ymax = 2)
        # vi_series_visualisation(data_directory = data_directory, ymin = 0, ymax = 2, shape_path = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/points_visualisation.shp")

    tile = TileInfo(data_directory)
    tile = tile.import_info()
    file = open(logpath, "a")
    for parameter in tile.parameters:
        file.write(parameter + " : " +  str(tile.parameters[parameter]) + "\n")
    file.close()

if __name__ == '__main__':
    cli_process_tiles()

