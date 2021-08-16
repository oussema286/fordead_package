# Visualization of results
The package also contains two tools to visualize the results. The first one allows to make a timelapse to visualize the results at each Sentinel-2 date used, with the Sentinel-2 data in RGB in the background and a slider to navigate between the different dates.
The second one allows to visualize for a particular pixel the time series of the vegetation index with the associated model, the anomaly detection threshold and the associated detections.

## Create timelapses
#### INPUTS
The input parameters are :

- **data_directory**: The path of the folder in which the already calculated results are written, and in which the timelapses will be saved
- **observations_terrain_path** : Optional, path of the shapefile containing the field observations, with the columns "scolyte1", "organisme" and "date". "Scolyte1" can take the values "C", "V", "R", "S", "I", "G" or "X".
- **shape_path** : Path of a shapefile containing polygons or points used to define the timelapse areas. Not used if the timelapse is defined from coordinates through the **x** and **y** parameters.
- **x** : x coordinate in the projection system of the Sentinel-2 tile, used as the center of the area to visualize as timelapse. Not used if the timelapse is defined from a shapefile by the **shape_path** parameter.
- **y** : y coordinate in the projection system of the Sentinel-2 tile, used as the center of the area to visualize as timelapse. Not used if the timelapse is defined from a shapefile by the **shape_path** parameter.
- **buffer** : Buffer zone around the polygons or points to define the timelapse extent.
- **name_column** : Name of the column containing the id or unique name of the polygon or point if **shape_path** is used. (Default: "id")
- **max_date** : Exclude from the timelapse all Sentinel-2 dates after this date (format : "YYYY-MM-DD"). By default, the timelapse uses all available Sentinel-2 dates.
- **zip_results**: If True, the html files containing the timelapses are transferred in a compressed zip file.

Required parameters are **data_directory** and either **shape_path** or **x** and **y**.

#### OUTPUTS
The outputs are in the folder data_directory/Timelapses, with for each polygon or point a .html file with as file name the value in the column **name_column** if made using **shape_path**, or x_y.html if made using **x** and **y** coordinates.
If zip_results is True, a Timelapses.zip file containing the html files is also created. Zipping html files greatly reduce their size.

This tool may not work on large areas, it is recommended to avoid launching this operation on areas larger than 20 km².

#### ANALYSIS
The slider allows you to move temporally from SENTINEL date to SENTINEL date
The image corresponds to the RGB bands of the SENTINEL data
The results appear as polygons:
- Black polygons: bare ground
- Yellow polygons: areas detected as declining
- Blue polygons: areas detected as sanitary cuts (areas detected as bare soil after being detected as declining)

The polygons appear at the date of the first anomaly, if confirmed with 3 successive anomalies, and if there is no return to normal with 3 successive dates without anomalies afterwards. So false detections related to temporary water stress which are subsequently corrected do not appear. Also, in the last dates, there may be anomalies not appearing yet due to the lack of future data to confirm the detection.

If the field observation data are also displayed, move the mouse over these polygons to obtain their information: | <organization from which the data originated> : <observation date>. The color depends on the observed declining stage.
It is also possible to zoom in on the desired area by holding down the click while delimiting an area. It is then possible to zoom out by double clicking on the image. Passing the mouse over a pixel also allows you to obtain its information:

x : coordinates in x
y : coordinates in y
z : [<reflectance in red>,<reflectance in green>,<reflectance in blue>], that is to say the value of the corresponding SENTINEL band at the given date.

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

## Create graphs showing the evolution of the time series
#### INPUTS
The input parameters are:

- **data_directory**: The path of the folder in which the already computed results are written, and in which the graphs will be saved
- **shape_path** : Path of a shapefile containing the points where the graphs will be made.
- **name_column** : Name of the column containing the identifier or unique name of the point (default : "id")
- **ymin** : ymin limit of the graph, to be adapted to the vegetation index used (Default : 0)
- **ymax** : ymax limit of the graph, to be adapted to the vegetation index used (default : 2)
- **chunks** : int, If the results used were calculated on a large scale such as a tile, giving a chunk size (e.g. 1280)  allows to import the data much faster, and saves RAM.

#### OUTPUTS
The outputs are in the folder data_directory/SeriesTemporelles, with for each point a .png file with as file name the value in the column **name_column**.

## How to use
### From a script
#### From a shapefile containing the areas of interest
```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualization(data_directory = <data_directory>, shape_path = <shape_path>, name_column = "id", ymin = 0, ymax = 2, chunks = 100)
```
#### From coordinates
```bash
from fordead.visualisation.vi_series_visualisation import vi_series_visualisation
vi_series_visualization(data_directory = <data_directory>, ymin = 0, ymax = 2, chunks = 100)
```
In this mode, the user can choose to give X and Y coordinates in the projection system of the Sentinel-2 data used.
It is also possible to give the pixel index starting from (xmin,ymax), useful if a timelapse has been created over the whole computed area in which case the index corresponds to the coordinates in the timelapse.

### From the command prompt
```bash
fordead graph_series [OPTIONS]
```
See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-graph_series)

#### EXAMPLE
![graph_example](Diagrams/graph_example.png "graph_example")
