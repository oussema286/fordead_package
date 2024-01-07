
# <div align="center"> Applying the FORDEAD method </div>

Here we will apply the main three steps of the fordead method, as shown in the second part of the workflow diagram.

![workflow_calval](Figures/workflow_calval.png "workflow_calval")

First, for each pixel of each observation, for each valid Sentinel-2 acquisition, we will calculate a chosen vegetation index, as well as masks.
Then, we will compute the harmonic model of the vegetation index for each pixel.
Finally, the dieback and stress detection is performed.
##### Running this step in a script

Run the following instructions, replacing 

```python
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe
from fordead.validation.dieback_detection_from_dataframe import dieback_detection_from_dataframe


mask_vi_from_dataframe(reflectance_path = reflectance_path,
					masked_vi_path = output_dir / "mask_vi_tuto.csv",
					periods_path = output_dir / "periods_tuto.csv",
					vi = "CRSWIR",
					soil_detection = True,
					name_column = "id")


train_model_from_dataframe(masked_vi_path = output_dir / "mask_vi_tuto.csv",
							pixel_info_path = output_dir / "pixel_info_tuto.csv",
							periods_path = output_dir / "periods_tuto.csv",
						   name_column = 'id',
						   min_last_date_training = "2018-01-01",
						   max_last_date_training = "2018-06-01",
						   nb_min_date = 10)

dieback_detection_from_dataframe(
				masked_vi_path = output_dir / "fordead_results/mask_vi_tuto.csv",
                pixel_info_path = output_dir / "fordead_results/pixel_info_tuto.csv",
                periods_path = output_dir / "fordead_results/periods_tuto.csv",
                name_column = "id",
                update_masked_vi = True)
```

The complete user guides can be found here :
-  [mask_vi_from_dataframe](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/05_compute_masks_and_vegetation_index_from_dataframe)
- [train_model_from_dataframe](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/06_training_model_from_dataframe)
- [dieback_detection_from_dataframe](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/07_dieback_detection_from_dataframe)

-----
### OUTPUT
-----
The results are condensed in the csv at *periods_path* , giving information on all periods :

![periods_final](Figures/periods_final.jpg "periods_final")

A more detailed csv is updated at *masked_vi_path*, and now holds the following information : 

![masked_vi_updated](Figures/masked_vi_updated.jpg "masked_vi_updated")

