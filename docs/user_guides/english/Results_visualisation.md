# Visualization of results
The package also contains two tools to visualize the results. The first one allows to make a timelapse to visualize the results at each Sentinel-2 date used, with the Sentinel-2 data in RGB in the background and a slider to navigate between the different dates.
The second one allows to visualize for a particular pixel the time series of the vegetation index with the associated model, the anomaly detection threshold and the associated detections.

## Create timelapses
#### INPUTS
The input parameters are :

- **data_directory**: The path of the folder in which the already calculated results are written, and in which the timelapses will be saved
- **shape_path** : Path of a shapefile containing polygons or points used to define the timelapse areas. Not used if the timelapse is defined from coordinates through the **x** and **y** parameters.
- **name_column** : Name of the column containing the id or unique name of the polygon or point if **shape_path** is used. (Default: "id")
- **x** : x coordinate in the projection system of the Sentinel-2 tile, used as the center of the area to visualize as timelapse. Not used if the timelapse is defined from a shapefile by the **shape_path** parameter.
- **y** : y coordinate in the projection system of the Sentinel-2 tile, used as the center of the area to visualize as timelapse. Not used if the timelapse is defined from a shapefile by the **shape_path** parameter.
- **buffer** : Buffer zone around the polygons or points to define the timelapse extent.
- **vector_display_path** : Optionnal, path of a vector to display in the timelapse, can contain points, lines and polygons.
- **hover_column_list** : String or list strings corresponding to columns in the **vector_display_path** file, whose information to display when hovering mouse over its objects. To use only if **vector_display_path** is used
- **max_date** : Exclude from the timelapse all Sentinel-2 dates after this date (format : "YYYY-MM-DD"). By default, the timelapse uses all available Sentinel-2 dates.
- **show_confidence_class** : If True, detected dieback is shown with the confidence class, indicative of the pixel's state at the last date used, as computed in the step [05_compute_confidence](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/05_compute_confidence/)
- **zip_results**: If True, the html files containing the timelapses are transferred in a compressed zip file.

Required parameters are **data_directory** and either **shape_path** or **x** and **y**.

#### OUTPUTS
The outputs are in the folder data_directory/Timelapses, with for each polygon or point a .html file with as file name the value in the column **name_column** if made using **shape_path**, or x_y.html if made using **x** and **y** coordinates.
If zip_results is True, the resulting timelapses are zipped in a Timelapses.zip file. Zipping html files reduces their size by 70%.

This tool may not work on large areas, it is recommended to avoid launching this operation on areas larger than 20 km².

#### ANALYSIS
The slider allows you to move temporally from SENTINEL date to SENTINEL date
The image corresponds to the RGB bands of the SENTINEL data
The results appear as polygons :
- Detected dieback appears in white, or from white to red depending on the confidence class if **show_confidence_class** is True.
If the detection includes bare ground detection (see [01_compute_masked_vegetationindex](https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/)) :
- Black polygons: bare ground
- Blue polygons: areas detected as bare ground after being detected as dieback

A legend is included, and clicking on a legend item toggles its visibility, double clicking makes it the sole visible item on the graph.

The polygons appear at the date of the first anomaly, if confirmed with 3 successive anomalies, and if there is no return to normal with 3 successive dates without anomalies afterwards. So false detections related to temporary water stress which are subsequently corrected do not appear. Also, in the last dates, there may be anomalies not appearing yet due to the lack of future data to confirm the detection.

If vector_display_path is filled in, the points, lines or polygons inside the shapefile are displayed in dark violet. The user can move the mouse over the objects to obtain the information from the columns listed in **hover_column_list**.
It is also possible to zoom in on the desired area by holding down the click while delimiting an area. It is then possible to zoom out by double clicking on the image. Passing the mouse over a pixel also allows you to obtain its information :

- x : coordinates in x
- y : coordinates in y
- z : `[<reflectance in red>,<reflectance in green>,<reflectance in blue>]`, that is to say the value of the corresponding SENTINEL band at the given date.

## How to use
### From a script
#### From a shapefile containing the areas of interest
```bash
from fordead.visualisation.create_timelapse import create_timelapse
create_timelapse(data_directory = <data_directory>, shape_path = <shape_path>, buffer = 100, name_column = "id")
```
#### From coordinates
```bash
from fordead.visualisation.create_timelapse import create_timelapse
create_timelapse(data_directory = <data_directory>, x = <x>, y = <y>, buffer = 100)
```
### From the command prompt
```bash
fordead timelapse [OPTIONS]
```
See detailed documentation at [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-timelapse)

***

## Create graphs showing the evolution of the time series
#### INPUTS
The input parameters are:

- **data_directory**: The path of the folder in which the already computed results are written, and in which the graphs will be saved
- **x** : x coordinate in the Sentinel-2 data CRS of the pixel of interest. Not used if **shape_path** parameter is used.
- **y** : y coordinate in the Sentinel-2 data CRS of the pixel of interest. Not used if **shape_path** parameter is used.
- **shape_path** : Path of a shapefile containing the points where the graphs will be made.
- **name_column** : Name of the column containing the identifier or unique name of the point (default : "id")
- **ymin** : ymin limit of the graph, to be adapted to the vegetation index used (Default : 0)
- **ymax** : ymax limit of the graph, to be adapted to the vegetation index used (default : 2)
- **chunks** : int, If the results used were calculated on a large scale such as a tile, giving a chunk size (e.g. 1280)  allows to import the data much faster, and saves RAM.

#### OUTPUTS
The outputs are in the folder data_directory/TimeSeries, with for each point a .png file with as file name the value in the column **name_column**, or in the format *Xx_coord_Yy_coord.png* if coordinates are used.

## How to use
### From a script
#### From a shapefile containing the points of interest
```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualisation(data_directory = <data_directory>, shape_path = <shape_path>, name_column = "id", ymin = 0, ymax = 2, chunks = 100)
```
#### From coordinates
Coordinates must be in the CRS of the Sentinel-2 tile.
```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualisation(data_directory = <data_directory>, x = <x_coord>, y = <y_coord>, ymin = 0, ymax = 2, chunks = 100)
```

#### From prompt loop
If neither **x** and **y**, or **shape_path** are given, the user will be prompted to give either X and Y coordinates in the projection system of the Sentinel-2 data used, or the pixel indices starting from (xmin,ymax) of the whole are, which can be useful if a timelapse has been created over the whole computed area in which case the index corresponds to the coordinates in the timelapse.
After each plot, the user is prompted again to give other coordinates. Input X = -1 to end the loop. Input <ENTER> to plot a random pixel inside the area of interest.

```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualisation(data_directory = <data_directory>, ymin = 0, ymax = 2, chunks = 100)
```

> **_NOTE :_** The **chunks** parameter can be ignored only if computed area is small.

### From the command prompt
```bash
fordead graph_series [OPTIONS]
```
See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-graph_series)

#### EXAMPLE
![anomaly_detection_X642135_Y5452255](Diagrams/anomaly_detection_X642135_Y5452255.png "anomaly_detection_X642135_Y5452255")