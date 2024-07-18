from path import Path
import pytest
from fordead.validation.obs_to_s2_grid import obs_to_s2_grid
from fordead.validation.extract_cloudiness import extract_cloudiness
from fordead.validation.extract_reflectance import extract_reflectance
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe
from fordead.validation.dieback_detection_from_dataframe import dieback_detection_from_dataframe
import subprocess

@pytest.mark.parametrize("sentinel_source", ["THEIA", "Planetary"])
def test_calibration(input_dir, output_dir, sentinel_source):
    
    print(f"Using {sentinel_source} data")
    ########################################################
    obs_path = input_dir / "vector/observations_tuto.shp"
    calval_dir = (output_dir / f"calval_{sentinel_source}").rmtree_p().mkdir()

    if sentinel_source == "THEIA":
        sentinel_source = input_dir / "sentinel_data" / "validation_tutorial" / "sentinel_data"
        cloudiness_path = calval_dir / "extracted_cloudiness.csv"
    else:
        cloudiness_path = None

    preprocessed_obs_path = calval_dir / "preprocessed_obs.geojson"
    reflectance_path = calval_dir / "extracted_reflectance.csv"
    masked_vi_path = calval_dir / 'mask_vi.csv'
    periods_path = calval_dir / 'periods.csv'
    pixel_info_path = calval_dir / 'pixel_info.csv'
    #########################################################

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

@pytest.mark.parametrize("sentinel_source", ["THEIA", "Planetary"])
def test_calibration_cli(input_dir, output_dir, sentinel_source):
    # TODO: maybe use CliRunner for pytest https://click.palletsprojects.com/en/8.1.x/testing/
    # First not were not successful because of an isolation error...
    print(f"Using {sentinel_source} data")
    ########################################################
    obs_path = input_dir / "vector/observations_tuto.shp"
    calval_dir = (output_dir / f"calval_{sentinel_source}_cli").rmtree_p().mkdir()

    if sentinel_source == "THEIA":
        sentinel_source = input_dir / "sentinel_data" / "validation_tutorial" / "sentinel_data"
        cloudiness_path = calval_dir / "extracted_cloudiness.csv"
    else:
        cloudiness_path = None

    preprocessed_obs_path = calval_dir / "preprocessed_obs.geojson"
    reflectance_path = calval_dir / "extracted_reflectance.csv"
    masked_vi_path = calval_dir / 'mask_vi.csv'
    periods_path = calval_dir / 'periods.csv'
    pixel_info_path = calval_dir / 'pixel_info.csv'
    #########################################################

    def run_cmd(cmd):
        cmd = ["fordead"] + cmd
        print(" ".join(cmd))
        subprocess.run(" ".join(cmd), check=True, shell=True)

    # obs_to_s2_grid
    cmd = [
        "obs_to_s2_grid",
        f"--obs_path {obs_path}", 
        f"--sentinel_source {sentinel_source}",
        f"--export_path {preprocessed_obs_path}",
        f"--name_column id"]
    run_cmd(cmd)

    if cloudiness_path is not None:
        # not implemented for Planetary
        cmd = [
            "extract_cloudiness",
            f"--sentinel_dir {sentinel_source}",
            f"--export_path {cloudiness_path}",
            f"--sentinel_source THEIA"]
        run_cmd(cmd)

    cmd = [
        "extract_reflectance",
        f"--obs_path {preprocessed_obs_path}",
        f"--sentinel_source {sentinel_source}", 
        f"--lim_perc_cloud 0.3",
        f"--export_path {reflectance_path}",
        f"--name_column id",
        f"--tile_selection T31UGP",
        ]
    if cloudiness_path is not None:
        cmd += [f"--cloudiness_path {cloudiness_path}"]

    run_cmd(cmd)

    cmd = [
        "calval_masked_vi",
        f"--reflectance_path {reflectance_path}",
        f"--masked_vi_path {masked_vi_path}",
        f"--periods_path {periods_path}",
        f"--vi CRSWIR",
        f"--soil_detection",
        f"--name_column id"]
    
    run_cmd(cmd)

    cmd = [
        "calval_train_model",
        f"--masked_vi_path {masked_vi_path}",
        f"--pixel_info_path {pixel_info_path}",
        f"--periods_path {periods_path}",
        f"--name_column id",
        f"--min_last_date_training 2018-01-01",
        f"--max_last_date_training 2018-06-01",
        f"--nb_min_date 10"]
    run_cmd(cmd)

    cmd = [
        "calval_dieback_detection",
        f"--masked_vi_path {masked_vi_path}",
        f"--pixel_info_path {pixel_info_path}",
        f"--periods_path {periods_path}",
        f"--name_column id",
        f"--stress_index_mode mean",
        f"--update_masked_vi"]
    run_cmd(cmd)
