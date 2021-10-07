#### Step 1 : Computing the vegetation index and a mask for each SENTINEL-2 date

The first step is to calculate the vegetation index and a mask for each date. The mask corresponds to pixels that should not be used throughout the rest of the detection steps. Sentinel-2 data will simply be recognized by the algorithm, as long as in the **input_directory**, each directory corresponds to a Sentinel-2 date, with the corresponding date in its name. In those directories, there should be a file for each Sentinel-2 band with the band name in the file name (B2 or B02, and so on...).

For more details, you can find the complete guide for this step [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/).

##### Running this step using a script

```python
from fordead.steps.step1_compute_masked_vegetationindex import compute_masked_vegetationindex
input_directory = "<MyWorkingDirectory>/study_area"
data_directory = "<output directory>"

compute_masked_vegetationindex(input_directory = input_directory, data_directory = data_directory, lim_perc_cloud = 0.4, interpolation_order = 0, sentinel_source  = "THEIA", soil_detection = False, formula_mask = "B2 > 600 | (B3 == 0) | (B4 ==0)", vi = "CRSWIR", apply_source_mask = True)
```

##### Running this step from the command invite

The steps in this package can also be ran from the command invite. The command `fordead masked_vi -h` will be print the help information on this step. For example, to use it with the same parameters, one can use the following command :
```bash
fordead masked_vi -i <MyWorkingDirectory>/study_area -o <output directory> -n 0.4 --interpolation_order 0 --sentinel_source THEIA --formula_mask "(B2 > 600)" --vi CRSWIR --apply_source_mask
```

> **_NOTE :_** If the same parameters are used, the Sentinel-2 dates already computed are ignored. However, if you change any parameter, all previous results are deleted and calculated again. If new Sentinel-2 data are added in the **input_directory**, it is computed as long as it is more recent than the last computed Sentinel-2 date. This way of saving information on previous processes and paths is done using fordead's [TileInfo](https://fordead.gitlab.io/fordead_package/docs/examples/ex_tileinfo_object/) class, of which an object is saved in the data_directory and is retrieved each time a process is launched.

As you can see, this step includes many options, although only the **input_directory** and **data_directory** parameters don't have a default value, and the **sentinel_source** has to correspond to your data provider ("THEIA","Scihub" or "PEPS").

##### Outputs

Running this script will filter out all Sentinel-2 dates with a cloud percentage above **lim_perc_cloud** based on the data provider's classification, and create two directories in your **data_directory** :
- A "VegetationIndex" directory, containing the chosen vegetation index (in this case, CRSWIR) calculated for each remaining date using Sentinel-2 data interpolated at 10m resolution (in this case, `interpolation_order = 0` indicates nearest neighbour interpolation).
- A "Mask" directory, containing the associated binary raster mask which corresponds to the two default masks (any negative value in the first band of the stack is considered outside the satellite swath and any pixel with a 0 value in any band is considered a shadow) associated to the **formula_mask** which is chosen by the user, as well as the mask provided by the Sentinel-2 data provider if **apply_source_mask** is True.


Vegetation index             |  Mask
:-------------------------:|:-------------------------:
![gif_vegetation_index](Figures/gif_vegetation_index.gif "gif_vegetation_index")  |  ![gif_mask](Figures/gif_mask.gif "gif_mask")

Any logical operation formula can be used in **formula_mask** (see [compute_vegetation_index](https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#compute_vegetation_index)), although it is only used if **soil_detection** is False. If **soil_detection** is True, then the masks include bare ground detection as describe in the [step guide](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/), which can be useful but has only been tested on THEIA data on France's coniferous forests and might not be adapted to other contexts and types of data. This package has been used in France to map bark beetle infested stands, in which context this bare ground detection has been useful to filter out clear cuts, deciduous forests as well as late stage bark beetle infested forest stands. This option is described in the step guide, but will not be exploited in this tutorial.


[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/02_train_model)
