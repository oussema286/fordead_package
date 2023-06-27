# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 13:01:07 2023

@author: Raphael Dutrieux
"""
import pandas as pd
import time
from fordead.validation_process import fill_periods, detect_state_changes, detection_anomalies_dataframe, compute_stress_index, prediction_vegetation_index_dataframe
from pathlib import Path


def dieback_detection_from_dataframe(masked_vi_path, pixel_info_path, periods_path, name_column,
                                     threshold_anomaly = 0.16, max_nb_stress_periods = 5, vi = "CRSWIR", path_dict_vi = None):
    
    
    masked_vi = pd.read_csv(masked_vi_path)
    pixel_info = pd.read_csv(pixel_info_path)
    periods = pd.read_csv(periods_path)
    
    if "anomaly_intensity" in periods.columns:
        raise Exception(periods_path + " already exists.")
        
    pixel_info["coeff"] = pixel_info[["coeff1","coeff2","coeff3", "coeff4","coeff5"]].values.tolist()
    
    # masked_vi = remove_bare_ground(masked_vi,periods)
    
    
    if "bare_ground" in masked_vi.columns:
        # period_bare_ground = masked_vi[masked_vi["bare_ground"]]
        # period_bare_ground = period_bare_ground.groupby(by = ["area_name", name_column,"id_pixel"]).first().reset_index()
        # period_bare_ground["state"] = "Bare ground"
        # period_bare_ground = period_bare_ground.rename(columns={"Date": "start_date"}).drop(columns = ["vi", "bare_ground", "epsg"])
        detection_dates = masked_vi[~masked_vi["bare_ground"]]
    
    # test = masked_vi[(masked_vi[name_column] == 5) & (masked_vi["id_pixel"] == 41)]
    
    detection_dates = detection_dates.merge(pixel_info, on=["epsg", "area_name",name_column,"id_pixel"], how='left')
   
    # training_periods = get_training_period(masked_vi, name_column)
    
    detection_dates = detection_dates[detection_dates["Date"] > detection_dates["last_date_training"]].reset_index()

    detection_dates["predicted_vi"] = prediction_vegetation_index_dataframe(detection_dates, pixel_info, name_column)
    
    detection_dates["anomaly"], detection_dates["diff_vi"] = detection_anomalies_dataframe(detection_dates, threshold_anomaly, vi = vi, path_dict_vi = path_dict_vi)

    dated_changes = detect_state_changes(detection_dates, name_column)
 
    periods = fill_periods(periods,dated_changes, masked_vi, name_column)

    periods = compute_stress_index(detection_dates, periods, name_column)

    # periods = compute_stress_index(detection_dates, periods, name_column)
    # dieback_data = dieback_detection(detection_dates, dated_changes, name_column)


    periods.to_csv(periods_path, mode='w', index=False,header=True)
    # dieback_data.to_csv(Path(export_directory) / 'dieback_data.csv', mode='w', index=False,header=True)

    
if __name__ == '__main__':
    start_time_debut = time.time()
    #Exemple tuto
    # dieback_detection_from_dataframe(masked_vi_path = "D:/fordead/fordead_data/output/mask_vi_tuto.csv",
    #                                  pixel_info_path = "D:/fordead/fordead_data/output/pixel_info_tuto.csv",
    #                                    periods_path = "D:/fordead/fordead_data/output/periods_tuto.csv",
    #                                    name_column = "id")
    output_dir = Path("D:/fordead/Data/Validation/scolytes/02_calibrating_vi_threshold_anomaly/03_RESULTS/fordead_results3")

    dieback_detection_from_dataframe(masked_vi_path = output_dir / "masked_vi_scolytes.csv",
                                       pixel_info_path = output_dir / "pixel_info_tuto.csv",
                                       periods_path = output_dir / "periods_scolytes.csv",
                                       name_column = "Id")
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))
