from path import Path
from tempfile import TemporaryDirectory
from fordead.validation.obs_to_s2_grid import obs_to_s2_grid
from fordead.validation.extract_cloudiness import extract_cloudiness
from fordead.validation.extract_reflectance import extract_reflectance
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe
from fordead.validation.dieback_detection_from_dataframe import dieback_detection_from_dataframe

def test_local_calibration(input_dir):

    obs_path = input_dir / "vector/observations_tuto.shp"
    sentinel_dir = input_dir / "sentinel_data" / "validation_tutorial" / "sentinel_data"

    with TemporaryDirectory(prefix="fordead-tests_") as tempdir:
        calval_dir = Path(tempdir)
        #########################################################
        print("Using local THEIA data")

        preprocessed_obs_path = calval_dir / "preprocessed_obs_theia.gpkg"

        obs_to_s2_grid(
            obs_path = obs_path,
            sentinel_source = sentinel_dir, 
            export_path = preprocessed_obs_path,
            name_column = "id")

        cloudiness_path = calval_dir / "extracted_cloudiness.csv"
        reflectance_path = calval_dir / "extracted_reflectance_theia.csv"

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
                            masked_vi_path = calval_dir / "mask_vi_theia.csv",
                            periods_path = calval_dir / "periods_theia.csv",
                            vi = "CRSWIR",
                            soil_detection = True,
                            name_column = "id")


        train_model_from_dataframe(masked_vi_path = calval_dir / "mask_vi_theia.csv",
                                    pixel_info_path = calval_dir / "pixel_info_theia.csv",
                                    periods_path = calval_dir / "periods_theia.csv",
                                name_column = 'id',
                                min_last_date_training = "2018-01-01",
                                max_last_date_training = "2018-06-01",
                                nb_min_date = 10)

        dieback_detection_from_dataframe(
                        masked_vi_path = calval_dir / "mask_vi_theia.csv",
                        pixel_info_path = calval_dir / "pixel_info_theia.csv",
                        periods_path = calval_dir / "periods_theia.csv",
                        name_column = "id",
                        stress_index_mode = "mean",
                        update_masked_vi = True)

def test_pc_calibration(input_dir):

    obs_path = input_dir / "vector/observations_tuto.shp"
    sentinel_dir = input_dir / "sentinel_data" / "validation_tutorial" / "sentinel_data"

    with TemporaryDirectory(prefix="fordead-tests_") as tempdir:
        calval_dir = Path(tempdir)

        #########################################################
        print("Using Planetary Computer")

        preprocessed_obs_path = calval_dir / "preprocessed_obs_planetary.gpkg"

        obs_to_s2_grid(
            obs_path = obs_path,
            sentinel_source = "Planetary", 
            export_path = preprocessed_obs_path,
            name_column = "id")

        reflectance_path = calval_dir / "extracted_reflectance_planetary.csv"

        # extracting may take time as it downloads the data from the net
        extract_reflectance(
            obs_path = preprocessed_obs_path,
            sentinel_source = "Planetary", 
            lim_perc_cloud = 0.3,
            export_path = reflectance_path,
            name_column = "id")

        print("Applying FORDEAD")

        mask_vi_from_dataframe(reflectance_path = reflectance_path,
                            masked_vi_path = calval_dir / "mask_vi_theia.csv",
                            periods_path = calval_dir / "periods_theia.csv",
                            vi = "CRSWIR",
                            soil_detection = True,
                            name_column = "id")


        train_model_from_dataframe(masked_vi_path = calval_dir / "mask_vi_theia.csv",
                                    pixel_info_path = calval_dir / "pixel_info_theia.csv",
                                    periods_path = calval_dir / "periods_theia.csv",
                                name_column = 'id',
                                min_last_date_training = "2018-01-01",
                                max_last_date_training = "2018-06-01",
                                nb_min_date = 10)

        dieback_detection_from_dataframe(
                        masked_vi_path = calval_dir / "mask_vi_theia.csv",
                        pixel_info_path = calval_dir / "pixel_info_theia.csv",
                        periods_path = calval_dir / "periods_theia.csv",
                        name_column = "id",
                        stress_index_mode = "mean",
                        update_masked_vi = True)
