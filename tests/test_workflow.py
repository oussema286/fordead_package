from path import Path
from tempfile import TemporaryDirectory
from fordead.import_data import TileInfo
from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
from fordead.steps.step2_train_model import train_model
from fordead.steps.step3_dieback_detection import dieback_detection
from fordead.steps.step4_compute_forest_mask import compute_forest_mask
from fordead.steps.step5_export_results import export_results
from fordead.cli.cli_process_tiles import process_tiles
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation

def test_fordead_steps(input_dir, output_dir):
   
    test_output_dir = (output_dir / "workflow_steps").rmtree_p().mkdir()
    data_directory = test_output_dir / "dieback_detection"
    start_date = "2016-01-01"

    compute_masked_vegetationindex(
        input_directory = input_dir / "sentinel_data" / "dieback_detection_tutorial" / "study_area", 
        data_directory = data_directory,
        start_date=start_date,
        lim_perc_cloud = 0.4, 
        interpolation_order = 0, 
        sentinel_source  = "THEIA", 
        soil_detection = False, 
        formula_mask = "B2 > 600", 
        vi = "CRSWIR", 
        apply_source_mask = True)

    tile = TileInfo(data_directory)
    tile = tile.import_info()
    assert min(list(tile.paths["VegetationIndex"].keys())) >= start_date

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
    test_output_dir = (output_dir / "workflow_process_tiles").rmtree_p().mkdir()
    sentinel_dir = input_dir / "sentinel_data" / "dieback_detection_tutorial"
    forest_mask_source = input_dir / "vector" / "area_interest.shp"
    process_tiles(test_output_dir, sentinel_dir, tiles=["study_area"], forest_mask_source=forest_mask_source)

    # check result files exist
    res_dir = test_output_dir / "study_area" / "Results"
    expected_files = ["stress_periods.shp", "periodic_results_dieback.shp"]
    for f in expected_files:
        assert (res_dir / f).exists()

def test_visualisation(output_dir):
    test_output_dir = (output_dir / "workflow_process_tiles" / "study_area")
    x = [642385.] # index=122
    y = [5451865.] # index=219
    import geopandas as gpd
    points = gpd.GeoDataFrame(gpd.points_from_xy(x, y, crs=32631))
    points["id"]=0
    points_path = output_dir / "points.json"
    points.to_file(points_path)
    vi_series_visualisation(data_directory = test_output_dir, 
                        shape_path = points_path, 
                        name_column = "id",
                        ymin = 0, 
                        ymax = 2, 
                        chunks = 100)
    assert (test_output_dir / "TimeSeries" / "0.png").exists()