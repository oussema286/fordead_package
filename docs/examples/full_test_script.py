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


test_dieback_detection=True
test_calibration_theia_local=True
test_calibration_pc_remote=True

# output_dir = Path("<MyOutputDirectory>")
output_dir = Path(__file__).parent
input_dir = Path(__file__).parent / "fordead_data"



#########################################################
test_output_dir = output_dir / "test_output_dir"
#########################################################
# Creating directories
if test_output_dir.exists():
    test_output_dir.rmtree()
test_output_dir.mkdir()
(test_output_dir / "dieback_detection").mkdir()
(test_output_dir / "calibration_validation").mkdir()

# #########################################################
# print("Test theia_preprocess")

# from fordead.cli.cli_theia_preprocess import theia_preprocess
# download_dir = (test_output_dir / "download").mkdir()
# zipped_directory = download_dir / "zip"
# unzipped_directory = download_dir / "unzip"
# theia_preprocess(zipped_directory=zipped_directory,
#                  unzipped_directory=unzipped_directory,
#                  tiles = ["T31UFR"],
#                  start_date='2018-01-18',
#                  end_date='2018-01-19',
#                 #  login_theia = <login_theia>,
#                 #  password_theia = <password_theia>,
#                  level = "LEVEL2A", 
#                  lim_perc_cloud = 100,
#                  empty_zip = True)


if test_dieback_detection:
    #########################################################
    print("Testing dieback detection")

    data_directory = test_output_dir / "dieback_detection"

    compute_masked_vegetationindex(input_directory = input_dir / "sentinel_data" / "dieback_detection_tutorial" / "study_area", 
                                data_directory = data_directory, 
                                lim_perc_cloud = 0.4, 
                                interpolation_order = 0, 
                                sentinel_source  = "THEIA", 
                                soil_detection = False, 
                                formula_mask = "B2 > 600", 
                                vi = "CRSWIR", 
                                apply_source_mask = True)

    train_model(data_directory = data_directory, 
                nb_min_date = 10, 
                min_last_date_training="2018-01-01", 
                max_last_date_training="2018-06-01")

    dieback_detection(data_directory = data_directory, 
                    threshold_anomaly = 0.16,
                    stress_index_mode = "weighted_mean")

    compute_forest_mask(data_directory, 
                        forest_mask_source = "vector", 
                        vector_path = input_dir / "vector/area_interest.shp")

    export_results(data_directory = data_directory, 
                frequency= "ME", 
                multiple_files = False, 
                conf_threshold_list = [0.265],
                conf_classes_list = ["Low anomaly","Severe anomaly"])

    create_timelapse(data_directory = data_directory, 
                    x = 643069, 
                    y = 5452565, 
                    buffer = 1500)

    vi_series_visualisation(data_directory = data_directory, 
                            shape_path = input_dir / "vector/points_for_graphs.shp", 
                            name_column = "id", 
                            ymin = 0, 
                            ymax = 2, 
                            chunks = 100)





#########################################################
print("Testing calibration validation module")

obs_path = input_dir / "vector/observations_tuto.shp"
sentinel_dir = input_dir / "sentinel_data/validation_tutorial/sentinel_data/"

if test_calibration_theia_local:
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


if test_calibration_pc_remote:
    #########################################################
    print("Using Planetary Computer")

    preprocessed_obs_path = test_output_dir / "calibration_validation" / "preprocessed_obs_planetary.gpkg"

    obs_to_s2_grid(
        obs_path = obs_path,
        sentinel_source = "Planetary", 
        export_path = preprocessed_obs_path,
        name_column = "id")

    reflectance_path = test_output_dir / "calibration_validation" / "extracted_reflectance_planetary.csv"

    # extracting may take time as it downloads the data from the net
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
    sensitivity_dir.mkdir_p()

    args_to_test = {"threshold_anomaly" : [0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19], 
                    "vi" : ["CRSWIR","NDVI"]}

    sensitivity_analysis(testing_directory = sensitivity_dir,
                        reflectance_path = reflectance_path,
                        name_column = 'id',
                        update_masked_vi = False,
                        args_to_test = args_to_test)