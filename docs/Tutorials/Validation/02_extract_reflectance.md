# <div align="center"> Extraction of reflectance from Sentinel-2 data </div>

In this step, we can use the vector file created in the previous step to extract reflectance from Sentinel-2 data.

##### Running this step using a script

To extract the reflectance, run the following instructions :

```python
from fordead.validation.extract_reflectance import extract_reflectance

extracted_reflectance_path = "<MyWorkingDirectory>/extracted_reflectance.csv"

extract_reflectance(
	obs_path = preprocessed_obs_path,
	sentinel_dir = sentinel_dir, 
	export_path = extracted_reflectance_path,
	name_column = "id")

```

You can add these instructions to your script, but if you try to run the previous step again, it will raise an error because the preprocess observations file already exist.

##### Running this step from the command invite

This step can also be ran from the command prompt. The command `fordead extract_reflectance -h` will print the help information of this step. For example, to use it with the same parameters, the following command can be used:
```bash
fordead extract_reflectance --obs_path <MyWorkingDirectory>/vector/preprocessed_obs_tuto.shp --sentinel_dir <MyWorkingDirectory>/sentinel_data/validation_tutorial/sentinel_data/ --export_path <MyWorkingDirectory>/extracted_reflectance.csv --name_column id
```

This step yields a csv file at export_path, with the following attributes : 

![extracted_reflectance](Figures/extracted_reflectance.png "extracted_reflectance")

If you run the script again, the file will stay untouched as there is no new data to extract. Unless you add observations or new Sentinel-2 acquisitions.
To test this, you can add the Sentinel-2 data in the <MyWorkingDirectory>/validation_tutorial/sentinel_data_update to the sentinel_data directory and run this step again.

[PREVIOUS PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/01_preprocessing_observations)

