# Extracting reflectance from Sentinel-2 data

This step aims at extracting reflectance from Sentinel-2 data using a vector file containing points and exporting the data to a csv file. 
If new acquisitions are added to the Sentinel-2 directory, new data is extracted and added to the existing csv file.

#### INPUTS

The input parameters are :

- **obs_path** : The path to a vector file containing observation points, must have an ID column corresponding to name_column parameter, an 'area_name' column with the name of the Sentinel-2 tile from which to extract reflectance, and a 'espg' column containing the espg integer corresponding to the CRS of the Sentinel-2 tile.
- **sentinel_dir** :  The path of the directory containing Sentinel-2 data.
- **export_path** : The path to write csv file with extracted reflectance
- **name_column** *(optional)* : The name of the ID column. The default is "id".
- **bands_to_extract** *(optional)* : List of bands to extract
