from path import Path
from tempfile import TemporaryDirectory

from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.steps.step2_train_model import train_model
from fordead.steps.step3_dieback_detection import dieback_detection
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
from fordead.steps.step5_export_results import export_results
from fordead.cli.cli_process_tiles import process_tiles
def test_fordead_steps(input_dir, output_dir):
   
    test_output_dir = (output_dir / "workflow_steps").rmtree_p().mkdir()
    data_directory = test_output_dir / "dieback_detection"

    compute_masked_vegetationindex(
        input_directory = input_dir / "sentinel_data" / "dieback_detection_tutorial" / "study_area", 
        data_directory = data_directory, 
        lim_perc_cloud = 0.4, 
        interpolation_order = 0, 
        sentinel_source  = "THEIA", 
        soil_detection = False, 
        formula_mask = "B2 > 600", 
        vi = "CRSWIR", 
        apply_source_mask = True)

    train_model(
        data_directory = data_directory, 
        nb_min_date = 10, 
        min_last_date_training="2018-01-01", 
        max_last_date_training="2018-06-01")

    dieback_detection(
        data_directory = data_directory, 
        threshold_anomaly = 0.16,
        stress_index_mode = "weighted_mean")

    compute_forest_mask(
        data_directory, 
        forest_mask_source = "vector", 
        vector_path = input_dir / "vector" / "area_interest.shp")

    export_results(
        data_directory = data_directory, 
        frequency= "ME", 
        multiple_files = False, 
        conf_threshold_list = [0.265],
        conf_classes_list = ["Low anomaly","Severe anomaly"])

def test_process_tiles(input_dir, output_dir):
    test_ouptut_dir = (output_dir / "workflow_process_tiles").rmtree_p().mkdir()
    sentinel_dir = input_dir / "sentinel_data" / "dieback_detection_tutorial"
    forest_mask_source = input_dir / "vector" / "area_interest.shp"
    process_tiles(test_ouptut_dir, sentinel_dir, tiles=["study_area"], forest_mask_source=forest_mask_source)

    # check result files exist
    res_dir = test_ouptut_dir / "study_area" / "Results"
    expected_files = ["stress_periods.shp", "periodic_results_dieback.shp"]
    for f in expected_files:
        assert (res_dir / f).exists()


