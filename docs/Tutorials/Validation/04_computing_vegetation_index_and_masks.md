# <div align="center"> Computing vegetation index et masks </div>


In this step, for each pixel of each observation, for each valid Sentinel-2 acquisition, we will calculate a chosen vegetation index, as well as masks.

##### Running this step in a script

Run the following instructions :

```python
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe

mask_vi_from_dataframe(reflectance_path = output_dir / "reflectance_tuto.csv",
					masked_vi_path = output_dir / "fordead_results/mask_vi_tuto.csv",
					periods_path = output_dir / "fordead_results/periods_tuto.csv",
					cloudiness_path = output_dir / "cloudiness_tuto.csv",
					vi = "CRSWIR",
					lim_perc_cloud = 0.45,
					soil_detection = True,
					name_column = "id")

```

See complete user guide [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/05_compute_masks_and_vegetation_index_from_dataframe).
