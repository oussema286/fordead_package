# <div align="center"> Detecting dieback and stress </div>


In order to calibrate *fordead*, it is possible to test many parameter combinations, running the last three steps of the detection and saving the results for each combination, in a single function.

For example, we might want to test several threshold_anomaly values, on several vegetation indices. 

##### Running this step in a script

In the following script, we will test threshold_anomaly values from 0.01 to 0.2 with a 0.01 step, with three vegetation indices : CRSWIR, NDWI and NDVI. 

In a new script, run the following instructions :

```python
from fordead.validation.sensitivity_analysis import sensitivity_analysis
from pathlib import Path

sensitivity_dir = Path("<MyOutputDirectory>")

extracted_reflectance_path = output_dir / "extracted_reflectance.csv"
extracted_cloudiness_path = output_dir / "extracted_cloudiness.csv"

args_to_test = {"threshold_anomaly" : [0.01, 0.02,0.03,0.04,0.05,0.06,0.07,0.08,0.09,0.1,0.11,0.12,0.13,0.14,0.15,0.16,0.17,0.18,0.19,0.2], 
                "vi" : ["CRSWIR","NDVI", "NDWI"]}

sensitivity_analysis(testing_directory = sensitivity_dir,
                    reflectance_path = extracted_reflectance_path,
                    cloudiness_path = extracted_cloudiness_path,
                    name_column = 'id',
                    update_masked_vi = False,
                    args_to_test = args_to_test,
                    overwrite = False)

```

-----
### OUTPUT
-----

See complete user guide [here](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/validation_tools/08_sensitivity_analysis) to get more information about parameters and outputs.