# This is a script designed to run all main fordead function, from dieback detection, visualisation tools and the calibration and validation module.
# It uses data from a small dataset available here : https://gitlab.com/fordead/fordead_data

from path import Path
import shutil

from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.steps.step2_train_model import train_model
from fordead.steps.step3_dieback_detection import dieback_detection
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
from fordead.steps.step5_export_results import export_results

from fordead.visualisation.create_timelapse import create_timelapse
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

from fordead.validation.obs_to_s2_grid import obs_to_s2_grid
from fordead.validation.extract_reflectance import extract_reflectance
from fordead.validation.extract_cloudiness import extract_cloudiness
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe
from fordead.validation.dieback_detection_from_dataframe import dieback_detection_from_dataframe
from fordead.validation.sensitivity_analysis import sensitivity_analysis


# get current file directory
try:
    base_dir = Path(__file__).parent
except:
    base_dir = Path.getcwd()

################# User defined parameters ##############
fordead_data_dir = base_dir / "fordead_data" 
output_dir = base_dir / "outputs"
# sentinel_source defines the source used for sentinel data. 
# Accepted values are:
# - "THEIA" to use S2 THEIA data downloaded from https://gitlab.com/fordead/fordead_data
# - "Planetary" to use S2 Planetary Computer (i.e. Sen2Cor processed data)
# - "theiastac" to use S2 from CDS THEIA STAC catalog (i.e. remote THEIA data)

# sentinel_source = "THEIA"
# sentinel_source = "Planetary"
sentinel_source = "theiastac"

obs_path = fordead_data_dir / "vector/observations_tuto.shp"
calval_dir = (output_dir / f"calval_{sentinel_source}").rmtree_p().makedirs_p()

print(f"Calibration Validation using {sentinel_source} data")
print(f"Outputs are saved in : {calval_dir}")

make_sensitivity_analysis = True #, set to True to activate sensitivity analysis
sensitivity_dir = (calval_dir / "sensitivity_analysis").mkdir_p()
args_to_test = {"threshold_anomaly" : [0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19], 
                "vi" : ["CRSWIR","NDVI"]}
########################################################

if sentinel_source == "THEIA":
    if not fordead_data_dir.exists():
        raise FileNotFoundError("`fordead_data` directory not found, please download the data with download_data.py or adapt `base_dir` path")
    
    sentinel_source = fordead_data_dir / "sentinel_data" / "validation_tutorial" / "sentinel_data"
    cloudiness_path = calval_dir / "extracted_cloudiness.csv"
else:
    cloudiness_path = None

preprocessed_obs_path = calval_dir / "preprocessed_obs.geojson"
reflectance_path = calval_dir / "extracted_reflectance.csv"

obs_to_s2_grid(
    obs_path = obs_path,
    sentinel_source = sentinel_source, 
    export_path = preprocessed_obs_path,
    name_column = "id")

if cloudiness_path is not None:
    # not implemented for Planetary
    extract_cloudiness(
        sentinel_dir = sentinel_source, 
        export_path = cloudiness_path,
        sentinel_source = "THEIA")

extract_reflectance(
    obs_path = preprocessed_obs_path,
    sentinel_source = sentinel_source, 
    cloudiness_path = cloudiness_path,
    lim_perc_cloud = 0.3,
    export_path = reflectance_path,
    name_column = "id",
    tile_selection="T31UGP")

if make_sensitivity_analysis:
    
    print("Sensitivity analysis")

    sensitivity_analysis(testing_directory = sensitivity_dir,
                        reflectance_path = reflectance_path,
                        name_column = 'id',
                        update_masked_vi = False,
                        args_to_test = args_to_test)
else:

    masked_vi_path = calval_dir / 'mask_vi.csv'
    periods_path = calval_dir / 'periods.csv'
    pixel_info_path = calval_dir / 'pixel_info.csv'

    mask_vi_from_dataframe(reflectance_path = reflectance_path,
                        masked_vi_path = masked_vi_path,
                        periods_path = periods_path,
                        vi = "CRSWIR",
                        soil_detection = True,
                        name_column = "id")


    train_model_from_dataframe(masked_vi_path = masked_vi_path,
                                pixel_info_path = pixel_info_path,
                                periods_path = periods_path,
                            name_column = 'id',
                            min_last_date_training = "2018-01-01",
                            max_last_date_training = "2018-06-01",
                            nb_min_date = 10)

    dieback_detection_from_dataframe(
                    masked_vi_path = masked_vi_path,
                    pixel_info_path = pixel_info_path,
                    periods_path = periods_path,
                    name_column = "id",
                    stress_index_mode = "mean",
                    update_masked_vi = True)

