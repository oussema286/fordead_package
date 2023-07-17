# <div align="center"> Extraction of cloudiness from Sentinel-2 data </div>

In this step, we will extract the percentage of pixels in the mask provided by the Sentinel-2 data provider for each acquisition.
The results are exported in a csv file and can be used in the following step to filter out acquisitions which are too cloudy at the tile level. 
Even though we are using a smaller dataset in this tutorial, we will perform this step for the example, but it can be skipped.

##### Running this step in a script

Run the following instructions :

```python
from fordead.validation.extract_cloudiness import extract_cloudiness

extracted_cloudiness_path = output_dir / "extracted_cloudiness.csv"

extract_cloudiness(
	sentinel_dir = sentinel_dir, 
	export_path = extracted_cloudiness_path,
	tile_selection = ["T31UGP"],
	sentinel_source = "THEIA")
```

----------
## OUPUT FILE
----------
The results are exported in a csv file at *export_path*, with the columns :
- *area_name* : the name of the Sentinel-2 tile
- *Date* : the date of the Sentinel-2 acquisition
- *cloudiness* : the percentage of cloudy pixels


See complete user guide [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/03_extract_cloudiness).
