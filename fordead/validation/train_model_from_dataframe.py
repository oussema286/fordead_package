# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 14:21:33 2023

@author: rdutrieux
"""

import pandas as pd
from fordead.validation_process import get_last_training_date_dataframe, model_vi_dataframe
from pathlib import Path
import time
# import numpy as np

#Pas besoin de recalculer les masques si compute_vegetation_index change
#Sortir première date de bare_ground


def train_model_from_dataframe(masked_vi_path,
                           export_path,
                           name_column,
                           soil_detection = True,
                           min_last_date_training = "2018-01-01",
                           max_last_date_training = "2018-06-01",
                           nb_min_date = 10,
                           ):
        
    masked_vi = pd.read_csv(masked_vi_path)

    last_date_training = get_last_training_date_dataframe(masked_vi, min_last_date_training, max_last_date_training, nb_min_date, name_column) #masked_vi[["id_pixel","Date","mask"]]

    masked_vi = masked_vi.merge(last_date_training, on = ["area_name",name_column,"id_pixel"], how='left')

    coeff_model = model_vi_dataframe(masked_vi, name_column)
    
    pixel_info = last_date_training.merge(coeff_model, on = ["area_name",name_column,"id_pixel"], how='outer')

    pixel_info.to_csv(export_path, mode='w', index=False,header=True)




if __name__ == '__main__':
    start_time_debut = time.time()
    
    train_model_from_dataframe(masked_vi_path = "D:/fordead/fordead_data/output/mask_vi_tuto.csv",
                           export_path = "D:/fordead/fordead_data/output/pixel_info_tuto.csv",
                           name_column = "id")
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))
