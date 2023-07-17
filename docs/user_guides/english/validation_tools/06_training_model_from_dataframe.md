
Adjusts an harmonic model to predict the temporal periodicity of the vegetation index, based on the acquisitions of a specified training period.

----------
## INPUT PARAMETERS
----------
masked_vi_path : str
	Path of the csv containing the vegetation index for each pixel of each observation, for each valid Sentinel-2 acquisition. Must have the following columns : epsg, area_name, id, id_pixel, Date and vi.
pixel_info_path : str
	Path used to write the csv containing pixel info such as the validity of the model and its coefficients.
periods_path : str
	Path of the csv containing pixel periods, updated with the last_date of the training.
name_column : str
	Name of the ID column. The default is 'id'.
min_last_date_training : str, optional
	The date in YYYY-MM-DD format after which SENTINEL dates are no longer used for training, as long as there are at least nb_min_date dates valid for the pixel. The default is "2018-01-01".
max_last_date_training : str, optional
	Date in YYYY-MM-DD format until which SENTINEL dates can be used for training to reach the number of nb_min_date valid dates. The default is "2018-06-01".
nb_min_date : int, optional
	Minimum number of valid dates to calculate a model. The default is 10.

----------
## OUPUT
----------
This step updates the csv at *periods_path*, adding the column *last_date* and completing it for the training periods. 
It also writes a new csv file at *pixel_info_path* with the following columns :
- **epsg** : The CRS of the Sentinel-2 tile from which data was extracted
- **area_name** : The name of the Sentinel-2 tile from which data was extracted
- an ID column corresponding to the **name_column** parameter
- **id_pixel** : The ID of the pixel
- **last_training_date** : 
- **coeff1**, **coeff2**, ...,  **coeff5** : Value of the corresponding coefficient of the harmonic model :
```math
coeff1 + coeff2\sin{\frac{2\pi t}{T}} + coeff3\cos{\frac{2\pi t}{T}} + coeff4\sin{\frac{4\pi t}{T}} + coeff5\cos{\frac{4\pi t}{T}}
```
## Running this step
----------

#### Using a script

```python
from fordead.validation.train_model_from_dataframe import train_model_from_dataframe

train_model_from_dataframe(masked_vi_path = <masked_vi_path>,
                           pixel_info_path = <pixel_info_path>,
                           periods_path = <periods_path>,
                           name_column = 'id',
                           min_last_date_training = "2018-01-01",
                           max_last_date_training = "2018-06-01",
                           nb_min_date = 10
                           )
```
