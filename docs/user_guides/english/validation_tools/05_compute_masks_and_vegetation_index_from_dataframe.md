
Computes the vegetation index for each pixel of each observation, for each valid Sentinel-2 acquisition.
Filters out data by applying the fordead mask (if soil_detection is True) or a user mask defined by the user. 
(optional) Filters out acquisition by applying a limit on the percentage of cloud cover as calculated by the [extract_cloudiness function](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/03_extract_cloudiness/)
Writes the results in a csv file, as well as the first date of the training period for each pixel and, if soil_detection is True, the first date of detected bare ground.

----------
## INPUT PARAMETERS
----------
- reflectance_path *str* : Path of the csv file with extracted reflectance.
- masked_vi_path str : Path used to write the csv containing the vegetation index for each pixel of each observation, for each valid Sentinel-2 acquisition.
- periods_path *str* : Path used to write the csv containing the first date of the training periods for each pixel and, if soil_detection is True, the first date of detected bare ground.
- name_column *str* : Name of the ID column. The default is 'id'.
- cloudiness_path : *str* (optional) : Path of a csv with the columns 'area_name','Date' and 'cloudiness' used to filter acquisitions, can be calculated by the [extract_cloudiness function](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/03_extract_cloudiness/) Not used if None.
- vi : str (optional) : Chosen vegetation index. If using a custom one or one unavailable in this package, it can be added using the path_dict_vi parameter. The default is "CRSWIR".
- lim_perc_cloud : *float* (optional): The maximum percentage of clouds of the whole area. If the cloudiness percentage of the SENTINEL acquisition, calculated from the provider's classification, is higher than this threshold, the acquisition is filtered out. Only used if cloudiness_path is not None. The default is 0.45.
- soil_detection : bool  (optional) : If True, bare ground is detected and used as mask, but the process might not be adapted to other situations than THEIA data on France's coniferous forests. If False, mask from formula_mask is applied. The default is True.
- formula_mask : *str* (optional) : Formula whose result would be binary, format described [here](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#compute_vegetation_index). Is only used if soil_detection is False.. The default is "(B2 >= 700)".
- path_dict_vi : *str* (optional) :	Path to a text file used to add potential vegetation indices. If not filled in, only the indices provided in the package can be used (CRSWIR, NDVI, NDWI). The file [ex_dict_vi.txt](https://gitlab.com/fordead/fordead_package/-/blob/master/docs/examples/ex_dict_vi.txt) gives an example for how to format this file. One must fill the index's name, formula, and "+" or "-" according to whether the index increases or decreases when anomalies occur.. The default is None.
- list_bands : *list of str* (optional) : List of the bands used. The default is ["B2","B3","B4", "B8", "B8A", "B11","B12"].
- apply_source_mask : *bool* (optional) : If True, the mask of the provider is also used to mask the data. The default is False.
- sentinel_source : *str* (optional) : Provider of the data among 'THEIA' and 'Scihub' and 'PEPS'.. The default is "THEIA".

----------
## OUPUT FILE
----------
This step outputs two csv file:
- One written at masked_vi_path with the following columns :
	- **epsg** : The CRS of the Sentinel-2 tile from which data was extracted
	- **area_name** : The name of the Sentinel-2 tile from which data was extracted
	- an ID column corresponding to the **name_column** parameter
	- **id_pixel** : The ID of the pixel
	- **Date** : The date of the Sentinel-2 acquisition
	- **vi** : The value of the vegetation index
	- bare_ground : Value of the bare ground mask (if soil_detection is True), could be filtered.
- The other written at periods_path with the following columns :
	- **area_name** : The name of the Sentinel-2 tile from which data was extracted
	- an ID column corresponding to the **name_column** parameter
	- **id_pixel** : The ID of the pixel
	- **first_date** : The first date of the period
	- **state** : The period state, which so far can be "Training" or "Bare ground".

----------
## Running this step
----------

#### Using a script

```python
from fordead.validation.mask_vi_from_dataframe import mask_vi_from_dataframe

mask_vi_from_dataframe(reflectance_path = <reflectance_path>,
					   masked_vi_path = <masked_vi_path>,
					   periods_path = <periods_path>,
					   name_column = <name_column>,
					   cloudiness_path = <cloudiness_path>,
					   vi = "CRSWIR",
					   lim_perc_cloud = 0.45,
					   soil_detection = True,
					   formula_mask = "(B2 >= 700)",
					   path_dict_vi = None,
					   list_bands =  ["B2","B3","B4", "B8", "B8A", "B11","B12"],
					   apply_source_mask = False,
					   sentinel_source = "THEIA"
					   )
```
