# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 13:01:07 2023

@author: rdutrieux
"""
import pandas as pd
import time
from fordead.validation_process import detect_state_changes, detection_anomalies_dataframe, compute_stress_index, prediction_vegetation_index_dataframe


def dieback_detection_from_dataframe(masked_vi_path, pixel_info_path, export_path, name_column,
                                     threshold_anomaly = 0.16, max_nb_stress_periods = 5, vi = "CRSWIR", path_dict_vi = None):
    
    
    masked_vi = pd.read_csv(masked_vi_path)
    pixel_info = pd.read_csv(pixel_info_path)

    pixel_info["coeff"] = pixel_info[["coeff1","coeff2","coeff3", "coeff4","coeff5"]].values.tolist()
    
    if "bare_ground" in masked_vi.columns:
        period_bare_ground = masked_vi[masked_vi["bare_ground"]]
        period_bare_ground = period_bare_ground.groupby(by = ["area_name", name_column,"id_pixel"]).first().reset_index()
        period_bare_ground["state"] = "Bare ground"
        period_bare_ground = period_bare_ground.rename(columns={"Date": "start_date"}).drop(columns = ["vi", "bare_ground", "epsg"])
        masked_vi = masked_vi[~masked_vi["bare_ground"]]
    
    # test = masked_vi[(masked_vi[name_column] == 5) & (masked_vi["id_pixel"] == 41)]
    
    masked_vi = masked_vi.merge(pixel_info, on=["epsg", "area_name",name_column,"id_pixel"], how='left')
    masked_vi = masked_vi[masked_vi["Date"] > masked_vi["last_date_training"]].reset_index()

    masked_vi["predicted_vi"] = prediction_vegetation_index_dataframe(masked_vi, pixel_info, name_column)
    
    masked_vi["anomaly"], masked_vi["diff_vi"] = detection_anomalies_dataframe(masked_vi, threshold_anomaly, vi = vi, path_dict_vi = path_dict_vi)

    periods = detect_state_changes(masked_vi, name_column)

    periods_data = compute_stress_index(masked_vi, periods, max_nb_stress_periods, name_column)
    # dieback_data = dieback_detection(masked_vi, dated_changes, name_column)

    periods_tot = pd.concat([periods_data, period_bare_ground]).sort_values(["area_name",name_column,"id_pixel"], ascending = True)

    periods_tot.to_csv(export_path, mode='w', index=False,header=True)
    # dieback_data.to_csv(Path(export_directory) / 'dieback_data.csv', mode='w', index=False,header=True)

    
if __name__ == '__main__':
    start_time_debut = time.time()
    
    dieback_detection_from_dataframe(masked_vi_path = "D:/fordead/fordead_data/output/mask_vi_tuto.csv",
                                     pixel_info_path = "D:/fordead/fordead_data/output/pixel_info_tuto.csv",
                                       export_path = "D:/fordead/fordead_data/output/periods_data_tuto.csv",
                                       name_column = "id")
    print("Temps de calcul : %s secondes ---" % (time.time() - start_time_debut))
