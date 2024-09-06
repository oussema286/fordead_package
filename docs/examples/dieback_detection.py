from path import Path
import shutil

from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.steps.step2_train_model import train_model
from fordead.steps.step3_dieback_detection import dieback_detection
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
from fordead.steps.step5_export_results import export_results

from fordead.visualisation.create_timelapse import create_timelapse
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

# get current file directory
try:
    base_dir = Path(__file__).parent
except:
    base_dir = Path.getcwd()

fordead_data_dir = base_dir / "fordead_data" 
sentinel_dir = fordead_data_dir / "sentinel_data" / "dieback_detection_tutorial" / "study_area"
forest_mask_path = fordead_data_dir / "vector" / "area_interest.shp"
points_path = fordead_data_dir / "vector" / "points_for_graphs.shp"

output_dir =  base_dir / "outputs" / "dieback_detection"

if not fordead_data_dir.exists():
    raise FileNotFoundError("`fordead_data` directory not found, please download the data with download_data.py or adapt `base_dir` path")

# Remove if existing and recreate base output directory
print(f"Creating output directory: {output_dir}")
output_dir.rmtree_p().makedirs()


# #########################################################
# print("Test theia_preprocess")

# from fordead.cli.cli_theia_preprocess import theia_preprocess
# download_dir = (base_output_dir / "download").mkdir()
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


#########################################################
print("Testing dieback detection")

compute_masked_vegetationindex(input_directory = sentinel_dir, 
                            data_directory = output_dir, 
                            lim_perc_cloud = 0.4, 
                            interpolation_order = 0, 
                            sentinel_source  = "THEIA", 
                            soil_detection = False, 
                            formula_mask = "B2 > 600", 
                            vi = "CRSWIR", 
                            apply_source_mask = True)

train_model(data_directory = output_dir, 
            nb_min_date = 10, 
            min_last_date_training="2018-01-01", 
            max_last_date_training="2018-06-01")

dieback_detection(data_directory = output_dir, 
                threshold_anomaly = 0.16,
                stress_index_mode = "weighted_mean")

compute_forest_mask(data_directory = output_dir, 
                    forest_mask_source = "vector", 
                    vector_path = forest_mask_path)

export_results(data_directory = output_dir, 
            frequency= "ME", 
            multiple_files = False, 
            conf_threshold_list = [0.265],
            conf_classes_list = ["Low anomaly","Severe anomaly"])

create_timelapse(data_directory = output_dir, 
                x = 643069, 
                y = 5452565, 
                buffer = 1500)

vi_series_visualisation(data_directory = output_dir, 
                        shape_path = points_path, 
                        name_column = "id", 
                        ymin = 0, 
                        ymax = 2, 
                        chunks = 100)
