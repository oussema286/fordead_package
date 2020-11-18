# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:25:23 2020

@author: Raphaël Dutrieux
"""


import argparse
import pickle
from pathlib import Path
import numpy as np
from fordead.ImportData import import_forest_mask, import_coeff_model, import_decline_data, initialize_decline_data, import_masked_vi
from fordead.writing_data import write_tif
from fordead.decline_detection import detection_anomalies, prediction_vegetation_index, detection_decline


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest", help = "Dossier avec les données")
    parser.add_argument("-s", "--threshold_anomaly", dest = "threshold_anomaly",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    # parser.add_argument("-x", "--ExportAsShapefile", dest = "ExportAsShapefile", action="store_true",default = False, help = "Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")
    parser.add_argument("-o", "--Overwrite", dest = "Overwrite", action="store_false",default = True, help = "Si vrai, recommence la détection du début. Sinon, reprends de la dernière date analysée")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def decline_detection(
    data_directory = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest",
    threshold_anomaly=0.16,
    # ExportAsShapefile = False,
    Overwrite=True
    ):
    
    with open(Path(data_directory) / "PathsInfo", 'rb') as f:
        tuile = pickle.load(f)

    if Overwrite:
        tuile.delete_dir("AnomaliesDir")
        tuile.delete_dir("state_decline")
    
    tuile.add_dirpath("AnomaliesDir", tuile.data_directory / "DataAnomalies")
    tuile.getdict_datepaths("Anomalies",tuile.paths["AnomaliesDir"])
    tuile.search_new_dates()
    
    #Verify if there are new SENTINEL dates
    NbNewDates=np.sum(tuile.dates>"2018-01-01") - len(tuile.paths["Anomalies"])
    if  NbNewDates == 0:
        print("Pas de nouvelles dates SENTINEL-2")
    else:
        print(str(NbNewDates)+ " nouvelles dates")
               
        forest_mask = import_forest_mask(tuile.paths["ForestMask"])
    
        coeff_model = import_coeff_model(tuile.paths["coeff_model"])
        
        if "state_decline" in tuile.paths and not(Overwrite):
            decline_data = import_decline_data(tuile.paths)
        else:
            decline_data = initialize_decline_data(forest_mask.shape,forest_mask.coords)
            
            tuile.add_path("state_decline", tuile.data_directory / "DataDecline" / "state_decline.tif")
            tuile.add_path("first_date_decline", tuile.data_directory / "DataDecline" / "first_date_decline.tif")
            tuile.add_path("count_decline", tuile.data_directory / "DataDecline" / "count_decline.tif")
        
        for date_index, date in enumerate(tuile.dates):
            print(date)
            if date < "2018-01-01" or date in tuile.paths["Anomalies"]: #Si anomalies pas encore écrites, ou avant la date de début de détection
                continue
            else:
                masked_vi = import_masked_vi(tuile.paths,date)
            
                predicted_vi=prediction_vegetation_index(coeff_model,date)
                anomalies = detection_anomalies(masked_vi, predicted_vi, threshold_anomaly)
                                
                decline_data = detection_decline(decline_data, anomalies, masked_vi["mask"], date_index)
                               
                # Writing anomalies
                write_tif(anomalies, forest_mask.attrs, tuile.paths["AnomaliesDir"] / str("Anomalies_" + date + ".tif"),nodata=0)
        
        #Writing decline data to rasters        
        write_tif(decline_data["state"], forest_mask.attrs,tuile.paths["state_decline"],nodata=0)
        write_tif(decline_data["first_date"], forest_mask.attrs,tuile.paths["first_date_decline"],nodata=0)
        write_tif(decline_data["count"], forest_mask.attrs,tuile.paths["count_decline"],nodata=0)
                
        # print("Détection du déperissement")
    tuile.save_info()



if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    decline_detection(**dictArgs)