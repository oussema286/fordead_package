# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 14:21:33 2023

@author: rdutrieux
"""

import pandas as pd
from fordead.validation_process import get_last_training_date_dataframe, model_vi_dataframe, update_training_period
from pathlib import Path
import time
# import numpy as np

#Pas besoin de recalculer les masques si compute_vegetation_index change
#Sortir première date de bare_ground


def train_model_from_dataframe(masked_vi_path,
                           pixel_info_path,
                           periods_path,
                           name_column = 'id',
                           min_last_date_training = "2018-01-01",
                           max_last_date_training = "2018-06-01",
                           nb_min_date = 10
                           ):
    """
    
    Adjusts an harmonic model to predict the temporal periodicity of the vegetation index, based on the acquisitions of a specified training period.

    Parameters
    ----------
    masked_vi_path : str
        Path of the csv containing the vegetation index for each pixel of each observation, for each valid Sentinel-2 acquisition. Must have the following columns : epsg, area_name, id, id_pixel, Date and vi.
    pixel_info_path : str
        Path used to write the csv containing pixel info such as the validity of the model and its coefficients.
    periods_path : str
        Path of the csv containing pixel periods, it will be updated with the last_date of the training.
    name_column : str
        Name of the ID column. The default is 'id'.
    min_last_date_training : str, optional
        The date in YYYY-MM-DD format after which SENTINEL dates are no longer used for training, as long as there are at least nb_min_date dates valid for the pixel. The default is "2018-01-01".
    max_last_date_training : str, optional
        Date in YYYY-MM-DD format until which SENTINEL dates can be used for training to reach the number of nb_min_date valid dates. The default is "2018-06-01".
    nb_min_date : int, optional
        Minimum number of valid dates to calculate a model. The default is 10.

    """
        
    masked_vi = pd.read_csv(masked_vi_path)
    if "bare_ground" in masked_vi.columns:
        masked_vi = masked_vi[~masked_vi["bare_ground"]]

    last_date_training = get_last_training_date_dataframe(masked_vi, min_last_date_training, max_last_date_training, nb_min_date, name_column) #masked_vi[["id_pixel","Date","mask"]]

    masked_vi = masked_vi.merge(last_date_training, on = ["area_name",name_column,"id_pixel"], how='left')

    masked_vi = masked_vi[masked_vi["Date"] <= masked_vi["last_training_date"]].reset_index()
    
    coeff_model = model_vi_dataframe(masked_vi, name_column)
    
    pixel_info = last_date_training.merge(coeff_model, on = ["area_name",name_column,"id_pixel"], how='outer')

    update_training_period(last_date_training, periods_path, name_column)
    
    pixel_info.to_csv(pixel_info_path, mode='w', index=False,header=True)




if __name__ == '__main__':
    start_time_debut = time.time()
    # Exemple tuto
    output_dir = Path("D:/fordead/fordead_data/output/calval_tuto")
    train_model_from_dataframe(masked_vi_path = output_dir / "mask_vi_tuto.csv",
                            pixel_info_path = output_dir / "pixel_info_tuto.csv",
                            periods_path = output_dir / "periods_tuto.csv",
                            name_column = "id")
    # output_dir = Path("D:/fordead/Data/Validation/scolytes/02_calibrating_vi_threshold_anomaly/03_RESULTS/fordead_results3")

    # train_model_from_dataframe(masked_vi_path = output_dir / "masked_vi_scolytes.csv",
    #                            pixel_info_path = output_dir / "pixel_info_tuto.csv",
    #                            periods_path = output_dir / "periods_scolytes.csv",
    #                            name_column = "Id")
        
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))
