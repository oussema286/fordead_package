# This is a script designed to run all main fordead function, from dieback detection, visualisation tools and the calibration and validation module.
# It uses data from a small dataset available here : https://gitlab.com/fordead/fordead_data

from pathlib import Path
import shutil

from fordead.validation.obs_to_s2_grid import obs_to_s2_grid
from fordead.validation.extract_reflectance import extract_reflectance
from fordead.validation.extract_cloudiness import extract_cloudiness
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe
from fordead.validation.dieback_detection_from_dataframe import dieback_detection_from_dataframe
from fordead.validation.sensitivity_analysis import sensitivity_analysis


# output_dir = Path("<MyOutputDirectory>")
output_dir = Path("D:/fordead/05_SUBPROJECTS/13_test_tuto/")
input_dir = Path("D:/fordead/05_SUBPROJECTS/13_test_tuto/fordead_data")



#########################################################
obs_path = input_dir / "vector/observations_tuto.shp"
sentinel_dir = input_dir / "sentinel_data/validation_tutorial/sentinel_data/"
test_output_dir = output_dir / "test_output_dir"
#########################################################
# Creating directories
if test_output_dir.exists():
    shutil.rmtree(test_output_dir)
test_output_dir.mkdir(parents=True, exist_ok=True)
(test_output_dir / "dieback_detection").mkdir(parents=True, exist_ok=True)
(test_output_dir / "calibration_validation").mkdir(parents=True, exist_ok=True)
# (test_output_dir / "dieback_detection").mkdir(parents=True, exist_ok=True)


#########################################################
print("Testing calibration validation module")
#########################################################
print("Using local THEIA data")


preprocessed_obs_path = test_output_dir / "calibration_validation" / "preprocessed_obs_theia.gpkg"

obs_to_s2_grid(
	obs_path = obs_path,
	sentinel_source = sentinel_dir, 
	export_path = preprocessed_obs_path,
	name_column = "id")

cloudiness_path = test_output_dir / "calibration_validation" / "extracted_cloudiness.csv"
reflectance_path = test_output_dir / "calibration_validation" / "extracted_reflectance_theia.csv"

extract_cloudiness(
	sentinel_dir = sentinel_dir, 
	export_path = cloudiness_path,
	sentinel_source = "THEIA")

extract_reflectance(
    obs_path = preprocessed_obs_path,
    sentinel_source = sentinel_dir, 
    cloudiness_path = cloudiness_path,
    lim_perc_cloud = 0.3,
    export_path = reflectance_path,
    name_column = "id")

print("Applying FORDEAD")

mask_vi_from_dataframe(reflectance_path = reflectance_path,
					masked_vi_path = test_output_dir / "calibration_validation" / "mask_vi_theia.csv",
					periods_path = test_output_dir / "calibration_validation" / "periods_theia.csv",
					vi = "CRSWIR",
					soil_detection = True,
					name_column = "id")


train_model_from_dataframe(masked_vi_path = test_output_dir / "calibration_validation" / "mask_vi_theia.csv",
							pixel_info_path = test_output_dir / "calibration_validation" / "pixel_info_theia.csv",
							periods_path = test_output_dir / "calibration_validation" / "periods_theia.csv",
						   name_column = 'id',
						   min_last_date_training = "2018-01-01",
						   max_last_date_training = "2018-06-01",
						   nb_min_date = 10)

dieback_detection_from_dataframe(
				masked_vi_path = test_output_dir / "calibration_validation" / "mask_vi_theia.csv",
                pixel_info_path = test_output_dir / "calibration_validation" / "pixel_info_theia.csv",
                periods_path = output_dir / test_output_dir / "calibration_validation" / "periods_theia.csv",
                name_column = "id",
                stress_index_mode = "mean",
                update_masked_vi = True)


#########################################################
print("Using Planetary Computer")

preprocessed_obs_path = output_dir / "preprocessed_obs_planetary.gpkg"

obs_to_s2_grid(
	obs_path = obs_path,
	sentinel_source = "Planetary", 
	export_path = preprocessed_obs_path,
	name_column = "id")

reflectance_path = test_output_dir / "calibration_validation" / "extracted_reflectance_planetary.csv"

extract_reflectance(
    obs_path = preprocessed_obs_path,
    sentinel_source = "Planetary", 
    lim_perc_cloud = 0.3,
    export_path = reflectance_path,
    name_column = "id")

print("Applying FORDEAD")

#########################################################
print("Sensitivity analysis")
sensitivity_dir = (test_output_dir / "calibration_validation" / "sensitivity_analysis")
sensitivity_dir.mkdir(parents=True, exist_ok=True)

args_to_test = {"threshold_anomaly" : [0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19], 
                "vi" : ["CRSWIR","NDVI"]}

sensitivity_analysis(testing_directory = sensitivity_dir,
                    reflectance_path = reflectance_path,
                    name_column = 'id',
                    update_masked_vi = False,
                    args_to_test = args_to_test)