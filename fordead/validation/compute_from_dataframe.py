# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 11:00:53 2023

@author: rdutrieux
"""

import pandas as pd
from fordead.validation_process import get_dated_changes, compute_and_apply_mask, get_last_training_date_dataframe, model_vi_dataframe,prediction_vegetation_index_dataframe, detection_anomalies_dataframe, stress_detection, dieback_detection
from fordead.masking_vi import compute_vegetation_index
from pathlib import Path
import time
import numpy as np
#Pas besoin de recalculer les masques si compute_vegetation_index change
#Sortir première date de bare_ground


def compute_from_dataframe(reflectance_path,
                           export_directory,
                           name_column,
                       vi,
                       soil_detection = True,
                       formula_mask = "(B2 >= 700)",
                       path_dict_vi = None,
                       list_bands =  ["B2","B3","B4","B5", "B6", "B7", "B8", "B8A", "B11","B12"],
                       apply_source_mask = False,
                       sentinel_source = "THEIA",
                       min_last_date_training = "2018-01-01",
                       max_last_date_training = "2018-06-01",
                       nb_min_date = 10,
                       threshold_anomaly = 0.16,
                       max_nb_stress_periods = 5
                       ):
    
    reflect = pd.read_csv(reflectance_path)
    reflect = reflect.sort_values(by=[name_column,'id_pixel', 'Date'])
    
    reflect = compute_and_apply_mask(reflect, soil_detection, formula_mask, list_bands, apply_source_mask, sentinel_source, name_column)

    reflect["vi"] = compute_vegetation_index(reflect, vi = "CRSWIR", formula = None, path_dict_vi = None)
    reflect = reflect[~reflect["vi"].isnull()]
    reflect = reflect[~np.isinf(reflect["vi"])]


    last_date_training = get_last_training_date_dataframe(reflect, min_last_date_training, max_last_date_training, nb_min_date) #reflect[["id_pixel","Date","mask"]]

    reflect = reflect.merge(last_date_training, on=['id_pixel'], how='left')

    coeff_model = model_vi_dataframe(reflect)

    reflect = reflect.merge(coeff_model, on=['id_pixel'], how='left')

    #Make list of abandonned pixels and remove them
    reflect = reflect[reflect["Date"] > reflect["last_date_training"]].reset_index()

    reflect["predicted_vi"] = prediction_vegetation_index_dataframe(reflect)

    reflect["anomaly"], reflect["diff_vi"] = detection_anomalies_dataframe(reflect, threshold_anomaly, vi = vi, path_dict_vi = path_dict_vi)

    dated_changes = get_dated_changes(reflect, name_column)

    stress_data = stress_detection(reflect, dated_changes, max_nb_stress_periods, name_column)

    dieback_data = dieback_detection(reflect, dated_changes, name_column)

    stress_data.to_csv(Path(export_directory) / 'stress_data.csv', mode='w', index=False,header=True)
    dieback_data.to_csv(Path(export_directory) / 'dieback_data.csv', mode='w', index=False,header=True)


if __name__ == '__main__':
    start_time_debut = time.time()
    
    compute_from_dataframe(reflectance_path = "D:/fordead/fordead_data/output/reflectance_tuto.csv",
                       export_directory = "D:/fordead/fordead_data/output/results_tuto.csv",
                           vi = "CRSWIR",
                           name_column = "id")
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))
