# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:25:23 2020

@author: Raphaël Dutrieux
"""


import click
from fordead.import_data import import_coeff_model, import_decline_data, initialize_decline_data, import_masked_vi, import_first_detection_date_index, TileInfo, import_forest_mask
from fordead.writing_data import write_tif
from fordead.decline_detection import detection_anomalies, detection_decline
from fordead.model_spectral_index import prediction_vegetation_index, correct_vi_date


@click.command(name='decline_detection')
@click.option("-o", "--data_directory",  type=str, help="Path of the output directory")
@click.option("-s", "--threshold_anomaly",  type=float, default=0.16,
                    help="Minimum threshold for anomaly detection", show_default=True)
@click.option("--vi",  type=str, default=None,
                    help="Chosen vegetation index, only useful if step1 was skipped", show_default=True)
@click.option("--path_dict_vi",  type=str, default=None,
                    help="Path of text file to add vegetation index formula, only useful if step1 was skipped", show_default=True)
def cli_decline_detection(
    data_directory,
    threshold_anomaly=0.16,
    vi = None,
    path_dict_vi = None
    ):
    """
    Detects anomalies by comparing the vegetation index and its prediction from the model. 
    Detects declining pixels when there are 3 successive anomalies. If pixels detected as declining have 3 successive dates without anomalies, they are considered healthy again.
    Anomalies and decline data are written in the data_directory
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/english/03_decline_detection/
    \f
    Parameters
    ----------
    data_directory
    threshold_anomaly
    vi
    path_dict_vi

    Returns
    -------

    """
    decline_detection(data_directory, threshold_anomaly, vi, path_dict_vi)


def decline_detection(
    data_directory,
    threshold_anomaly=0.16,
    vi = None,
    path_dict_vi = None
    ):
    """
    Detects anomalies by comparing the vegetation index and its prediction from the model. 
    Detects declining pixels when there are 3 successive anomalies. If pixels detected as declining have 3 successive dates without anomalies, they are considered healthy again.
    Anomalies and decline data are written in the data_directory
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/english/03_decline_detection/
    
    \f
    Parameters
    ----------
    data_directory : str
        Path of the output directory
    threshold_anomaly : float
        Minimum threshold for anomaly detection
    vi : str
        Chosen vegetation index, only useful if step1 was skipped
    path_dict_vi : str
        Path of text file to add vegetation index formula, only useful if step1 was skipped

    Returns
    -------

    """
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"threshold_anomaly" : threshold_anomaly})
    if tile.parameters["Overwrite"] : 
        tile.delete_dirs("AnomaliesDir","state_decline" ,"periodic_results_decline","result_files","timelapse","series") #Deleting previous detection results if they exist
        if hasattr(tile, "last_computed_anomaly"): delattr(tile, "last_computed_anomaly")
    if vi==None : vi = tile.parameters["vi"]
    if path_dict_vi==None : path_dict_vi = tile.parameters["path_dict_vi"] if "path_dict_vi" in tile.parameters else None
    
    tile.add_dirpath("AnomaliesDir", tile.data_directory / "DataAnomalies") #Choose anomalies directory
    tile.getdict_datepaths("Anomalies",tile.paths["AnomaliesDir"]) # Get paths and dates to previously calculated anomalies
    tile.search_new_dates() #Get list of all used dates
    
    tile.add_path("state_decline", tile.data_directory / "DataDecline" / "state_decline.tif")
    tile.add_path("first_date_decline", tile.data_directory / "DataDecline" / "first_date_decline.tif")
    tile.add_path("count_decline", tile.data_directory / "DataDecline" / "count_decline.tif")
    
    #Verify if there are new SENTINEL dates
    new_dates = tile.dates[tile.dates > tile.last_computed_anomaly] if hasattr(tile, "last_computed_anomaly") else tile.dates[tile.dates >= tile.parameters["min_last_date_training"]]
    if  len(new_dates) == 0:
        print("Decline detection : no new dates")
    else:
        print("Decline detection : " + str(len(new_dates))+ " new dates")
        
        #IMPORTING DATA
        first_detection_date_index = import_first_detection_date_index(tile.paths["first_detection_date_index"])
        coeff_model = import_coeff_model(tile.paths["coeff_model"])
        
        if tile.paths["state_decline"].exists():
            decline_data = import_decline_data(tile.paths)
        else:
            decline_data = initialize_decline_data(first_detection_date_index.shape,first_detection_date_index.coords)
        if tile.parameters["correct_vi"]:
            forest_mask = import_forest_mask(tile.paths["ForestMask"])
        #DECLINE DETECTION
        for date_index, date in enumerate(tile.dates):
            if date in new_dates:
                masked_vi = import_masked_vi(tile.paths,date)
                if tile.parameters["correct_vi"]:
                    masked_vi["vegetation_index"], tile.correction_vi = correct_vi_date(masked_vi,forest_mask, tile.large_scale_model, date, tile.correction_vi)

                masked_vi["mask"] = masked_vi["mask"] | (date_index < first_detection_date_index) #Masking pixels where date was used for training

                predicted_vi=prediction_vegetation_index(coeff_model,[date])
                
                anomalies = detection_anomalies(masked_vi["vegetation_index"], predicted_vi, threshold_anomaly, 
                                                vi = vi, path_dict_vi = path_dict_vi).squeeze("Time")
                                
                decline_data = detection_decline(decline_data, anomalies, masked_vi["mask"], date_index)
                
                write_tif(anomalies, first_detection_date_index.attrs, tile.paths["AnomaliesDir"] / str("Anomalies_" + date + ".tif"),nodata=0)
                print('\r', date, " | ", len(tile.dates)-date_index-1, " remaining", sep='', end='', flush=True) if date_index != (len(tile.dates) -1) else print('\r', "                                              ", sep='', end='\r', flush=True) 
                del masked_vi, predicted_vi, anomalies
        tile.last_computed_anomaly = new_dates[-1]
                
        #Writing decline data to rasters
        write_tif(decline_data["state"], first_detection_date_index.attrs,tile.paths["state_decline"],nodata=0)
        write_tif(decline_data["first_date"], first_detection_date_index.attrs,tile.paths["first_date_decline"],nodata=0)
        write_tif(decline_data["count"], first_detection_date_index.attrs,tile.paths["count_decline"],nodata=0)
        
        # print("Détection du déperissement")
    tile.save_info()



if __name__ == '__main__':
    # print(dictArgs)
    # start_time = time.time()
    cli_decline_detection()
    # print("Temps d execution : %s secondes ---" % (time.time() - start_time))
