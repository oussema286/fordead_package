#### Step 2 : Training a vegetation index model pixel by pixel from the first dates

In this second step, early Sentinel-2 dates are considered representative of the normal seasonal behavior of the vegetation index, thus they are used to compute a model of the vegetation index which can then be used to predict its expected value at any date of the year. Such a model probably depends on many factors, forest density, composition, topography, and so on... So a different model is computed for each pixel to take these differences into account. The periodic model used to fit the training dates is the following:
```math
a1 + b1\sin{\frac{2\pi t}{T}} + b2\cos{\frac{2\pi t}{T}} + b3\sin{\frac{4\pi t}{T}} + b4\cos{\frac{4\pi t}{T}}
```

As an example, the following graph shows the time series of the vegetation index for a single pixel based on unmasked Sentinel-2 dates, as well as the adjusted model on training dates :

![vegetation_index_model](Figures/model_X642135_Y5452255.png "vegetation_index_model")

This step's complete guide can be found [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/02_train_model/).

##### Running this step using a script

To run this step, simply add the following lines to the script :
```python
from fordead.steps.step2_train_model import train_model
train_model(data_directory = data_directory, nb_min_date = 10, min_last_date_training="2018-01-01", max_last_date_training="2018-06-01")
```

##### Running this step from the command invite

This step can also be used from the command invite with the command :

```bash
fordead train_model -o <output directory> --nb_min_date 10 --min_last_date_training 2018-01-01 --max_last_date_training 2018-06-01
```

In this case, the model will be trained on all Sentinel-2 dates until 2018-01-01. If there are not 10 valid dates on 2018-01-01, the first 10 valid dates are used unless this number is not reach on 2018-06-01 in which case the pixel is dropped and no model will be calculated. This allows, for example in the case of a relatively ancient source of anomalies such as the bark beetle crisis, to start the detection as early as 2018 if there are enough valid dates at the beginning of the year, while allowing the study of pixels in situations with less data available simply by performing the training over a longer period to retrieve other valid dates. 

It is not recommended to end the training before 2018, because since the periodic model is annual, the use of at least two years of SENTINEL-2 data is advised.

> **_NOTE :_** This step can also be used if you skipped the first step and computed a vegetation index and a mask for each date through your own means, simply by filling in the parameters **path_vi** and **path_masks** with the corresponding directories.
Again, if the model is already computed and no parameters were changed, the process is ignored. If parameters were changed, previous results from this step and subsequent steps are deleted and the model is computed anew.

##### Outputs

The outputs of this second step, in the data_directory folder, are:
- In the **DataModel** folder, two files:
    - **first_detection_date_index.tif**, a raster that contains the index of the first date that will be used for detection. It allows to know for each pixel which dates were used for training and which ones are used for detection.
    - **coeff_model.tif**, a stack with 5 bands, one for each coefficient of the vegetation index model.
- In the **ForestMask** directory, the binary raster **valid_area_mask.tif** which is 1 for pixels where the model could be computed, 0 if there were not enough valid dates.


[NEXT PAGE](https://fordead.gitlab.io/fordead_package/docs/Tutorial/03_dieback_detection)