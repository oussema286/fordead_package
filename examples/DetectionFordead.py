# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:25:23 2020

@author: Raphaël Dutrieux
"""


import argparse
import numpy as np
from fordead.ImportData import import_forest_mask, import_coeff_model, import_decline_data, initialize_decline_data, import_masked_vi, import_last_training_date, TileInfo
from fordead.writing_data import write_tif
from fordead.decline_detection import detection_anomalies, prediction_vegetation_index, detection_decline
import time


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection/ZoneTest", help = "Dossier avec les données")
    parser.add_argument("-s", "--threshold_anomaly", dest = "threshold_anomaly",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    # parser.add_argument("-x", "--ExportAsShapefile", dest = "ExportAsShapefile", action="store_true",default = False, help = "Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")
    # parser.add_argument("-o", "--Overwrite", dest = "Overwrite", action="store_false",default = True, help = "Si vrai, recommence la détection du début. Sinon, reprends de la dernière date analysée")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def decline_detection(
    data_directory,
    threshold_anomaly=0.16,
    # ExportAsShapefile = False,
    ):
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"threshold_anomaly" : threshold_anomaly})
    if tile.parameters["Overwrite"] : tile.delete_dirs("AnomaliesDir","state_decline") #Deleting previous detection results if they exist
    
    tile.add_dirpath("AnomaliesDir", tile.data_directory / "DataAnomalies") #Choose anomalies directory
    tile.getdict_datepaths("Anomalies",tile.paths["AnomaliesDir"]) # Get paths and dates to previously calculated anomalies
    tile.search_new_dates() #Get paths and dates to all vegetation index dates
    
    tile.add_path("state_decline", tile.data_directory / "DataDecline" / "state_decline.tif")
    tile.add_path("first_date_decline", tile.data_directory / "DataDecline" / "first_date_decline.tif")
    tile.add_path("count_decline", tile.data_directory / "DataDecline" / "count_decline.tif")
    
    #Verify if there are new SENTINEL dates
    NbNewDates=np.sum(tile.dates>tile.parameters["min_last_date_training"]) - len(tile.paths["Anomalies"])
    if  NbNewDates == 0:
        print("Pas de nouvelles dates SENTINEL-2")
    else:
        print(str(NbNewDates)+ " nouvelles dates")
        
        #IMPORTING DATA
        forest_mask = import_forest_mask(tile.paths["ForestMask"])
        last_training_date = import_last_training_date(tile.paths["last_training_date"])
        coeff_model = import_coeff_model(tile.paths["coeff_model"])
        
        if tile.paths["state_decline"].exists():
            decline_data = import_decline_data(tile.paths)
        else:
            decline_data = initialize_decline_data(forest_mask.shape,forest_mask.coords)
            

        
        #DECLINE DETECTION
        for date_index, date in enumerate(tile.dates):
            if date < tile.parameters["min_last_date_training"] or date in tile.paths["Anomalies"]: #Ignoring dates used for training and dates already used
                continue
            else:
                print(date)
                masked_vi = import_masked_vi(tile.paths,date)
                masked_vi["mask"] = masked_vi["mask"] | (date_index <= last_training_date) #Masking pixels where date was used for training

                predicted_vi=prediction_vegetation_index(coeff_model,date)
                anomalies = detection_anomalies(masked_vi["vegetation_index"], predicted_vi, threshold_anomaly)
                                
                decline_data = detection_decline(decline_data, anomalies, masked_vi["mask"], date_index)
                               
                write_tif(anomalies, forest_mask.attrs, tile.paths["AnomaliesDir"] / str("Anomalies_" + date + ".tif"),nodata=0)
        
        
        #Writing decline data to rasters        
        write_tif(decline_data["state"], forest_mask.attrs,tile.paths["state_decline"],nodata=0)
        write_tif(decline_data["first_date"], forest_mask.attrs,tile.paths["first_date_decline"],nodata=0)
        write_tif(decline_data["count"], forest_mask.attrs,tile.paths["count_decline"],nodata=0)
                
        # print("Détection du déperissement")
    tile.save_info()



if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    start_time = time.time()
    decline_detection(**dictArgs)
    print("Temps d execution : %s secondes ---" % (time.time() - start_time))
