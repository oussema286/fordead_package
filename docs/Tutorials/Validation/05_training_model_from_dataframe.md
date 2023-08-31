# <div align="center"> Training harmonic model for each pixel </div>


Now we will compute the harmonic model of the vegetation index for each pixel.

##### Running this step in a script

Run the following instructions :

```python
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe

train_model_from_dataframe(masked_vi_path = fordead_results_dirpath / "mask_vi_tuto.csv",
							pixel_info_path = fordead_results_dirpath / "pixel_info_tuto.csv",
							periods_path = fordead_results_dirpath / "periods_tuto.csv",
						   name_column = 'id',
						   min_last_date_training = "2018-01-01",
						   max_last_date_training = "2018-06-01",
						   nb_min_date = 10)

```

See complete user guide [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/06_training_model_from_dataframe).
