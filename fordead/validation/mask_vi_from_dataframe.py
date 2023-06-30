# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 12:48:06 2023

@author: Raphaël Dutrieux
"""

import pandas as pd
from fordead.validation_process import compute_and_apply_mask, filter_cloudy_acquisitions, get_mask_vi_periods
from fordead.masking_vi import compute_vegetation_index
from pathlib import Path
import time
import numpy as np
#Pas besoin de recalculer les masques si compute_vegetation_index change
#Sortir première date de bare_ground


def mask_vi_from_dataframe(reflectance_path,
                           masked_vi_path,
                           periods_path,
                           name_column,
                           cloudiness_path,
                           vi = "CRSWIR",
                           lim_perc_cloud = 0.45,
                           soil_detection = True,
                           formula_mask = "(B2 >= 700)",
                           path_dict_vi = None,
                           list_bands =  ["B2","B3","B4", "B8", "B8A", "B11","B12"],
                           apply_source_mask = False,
                           sentinel_source = "THEIA"
                           ):

    
    reflect = pd.read_csv(reflectance_path)
    if cloudiness_path is not None:
        reflect = filter_cloudy_acquisitions(reflect, cloudiness_path, lim_perc_cloud)
        
    reflect = reflect.sort_values(by=["area_name",name_column,'id_pixel', 'Date'])
    
    reflect, first_date_bare_ground = compute_and_apply_mask(reflect, soil_detection, formula_mask, list_bands, apply_source_mask, sentinel_source, name_column)

    reflect["vi"] = compute_vegetation_index(reflect, vi = vi, formula = None, path_dict_vi = None)
    reflect = reflect[~reflect["vi"].isnull()]
    reflect = reflect[~np.isinf(reflect["vi"])]
    
    reflect = reflect[["epsg", "area_name", name_column, "id_pixel", "Date","vi", "bare_ground"]]
    # reflect = reflect.drop(columns=list_bands + ["soil_anomaly", "Mask"]) #soil_anomaly shouldn't be added in the first place
    
    mask_vi_periods = get_mask_vi_periods(reflect, first_date_bare_ground, name_column)
    
    mask_vi_periods.to_csv(periods_path, mode='w', index=False,header=True)
    reflect.to_csv(masked_vi_path, mode='w', index=False,header=True)


if __name__ == '__main__':
    start_time_debut = time.time()
    
    # Exemple tuto
    mask_vi_from_dataframe(reflectance_path = "D:/fordead/fordead_data/output/reflectance_tuto.csv",
                        masked_vi_path = "D:/fordead/fordead_data/output/calval_tuto/mask_vi_tuto.csv",
                        periods_path = "D:/fordead/fordead_data/output/calval_tuto/periods_tuto.csv",
                        cloudiness_path = "D:/fordead/fordead_data/output/cloudiness_tuto.csv",
                        vi = "CRSWIR",
                        name_column = "id")
    
    # Données de scolytes
    # output_dir = Path("D:/fordead/Data/Validation/scolytes/02_calibrating_vi_threshold_anomaly/03_RESULTS/fordead_results3")
    # mask_vi_from_dataframe(reflectance_path = "D:/fordead/Data/Validation/scolytes/02_calibrating_vi_threshold_anomaly/01_DATA/reflectance_scolytes.csv",
    #                     masked_vi_path = output_dir / "masked_vi_scolytes.csv",
    #                     periods_path = output_dir / "periods_scolytes.csv",
    #                     cloudiness_path = "D:/fordead/Data/Validation/scolytes/02_calibrating_vi_threshold_anomaly/01_DATA/extracted_cloudiness.csv",
    #                     vi = "CRSWIR",
    #                     name_column = "Id")
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))
