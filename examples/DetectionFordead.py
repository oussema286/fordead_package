# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 09:25:23 2020

@author: Raphaël Dutrieux
"""



# import os
import argparse
import pickle
from pathlib import Path
import numpy as np
# from fordead.DetectionDeperissement import DetectAnomalies,PredictVegetationIndex
from fordead.ImportData import import_forest_mask, import_coeff_model, import_decline_data, initialize_decline_data


def parse_command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest", help = "Dossier avec les données")
    parser.add_argument("-s", "--threshold_anomaly", dest = "threshold_anomaly",type = float,default = 0.16, help = "Seuil minimum pour détection d'anomalies")
    parser.add_argument("-x", "--ExportAsShapefile", dest = "ExportAsShapefile", action="store_true",default = False, help = "Si activé, exporte les résultats sous la forme de shapefiles plutôt que de rasters")
    parser.add_argument("-o", "--Overwrite", dest = "Overwrite", action="store_true",default = False, help = "Si vrai, recommence la détection du début. Sinon, reprends de la dernière date analysée")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def DetectionScolytes(
    data_directory = "C:/Users/admin/Documents/Deperissement/fordead_data/tests/OutputFordead/ZoneTest",
    threshold_anomaly=0.16,
    ExportAsShapefile = False,
    Overwrite=False
    ):
    
    with open(Path(data_directory) / "PathsInfo", 'rb') as f:
        tuile = pickle.load(f)
     
    # if Overwrite: OverwriteUpdate(tuile,DataDirectory)
    
    tuile.add_path("Anomalies", tuile.data_directory / "DataAnomalies" / "dir")
    tuile.getdict_datepaths("Anomalies",tuile.paths["Anomalies"].parent)
    tuile.search_new_dates()
    
    
    NbNewDates=np.sum(tuile.dates>"2018-01-01") - len(tuile.paths["Anomalies"])
    if  NbNewDates == 0:
        print("Pas de nouvelles dates SENTINEL-2")
    else:
        print(str(NbNewDates)+ " nouvelles dates")
               
        forest_mask = import_forest_mask(tuile.paths["ForestMask"])
    
        coeff_model = import_coeff_model(tuile.paths["coeff_model"])
        
        if "state_decline" in tuile.paths:
            state_decline, first_date_decline, count_decline = import_decline_data(tuile)
        else:
            decline_data = initialize_decline_data(forest_mask.shape,forest_mask.coords)
            

            
            
        
        
        # print("Détection du déperissement")
        
        # for DateIndex,date in enumerate(Dates):
        #     if date < "2018-01-01" or os.path.exists(os.path.join(DataDirectory,"DataAnomalies",tuile,"Anomalies_"+date+".tif")): #Si anomalies pas encore écrites, ou avant la date de début de détection
        #         continue
        #     else:
        #         VegetationIndex, Mask = ImportMaskedVI(DataDirectory,tuile,date)
            
        #     Anomalies = DetectAnomalies(VegetationIndex, PredictVegetationIndex(StackP,date),Mask, rasterSigma, CoeffAnomalie)



if __name__ == '__main__':
    dictArgs=parse_command_line()
    print(dictArgs)
    DetectionScolytes(**dictArgs)