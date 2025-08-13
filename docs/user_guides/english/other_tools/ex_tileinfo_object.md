The following script describes how to use the basic methods of TileInfo objects, which are objects meant to store and parse parameters used, paths to files, dates used.

The first step is to import the class function from the module.
```python
from fordead.import_data import TileInfo
```
Create TileInfo Object using the path of the directory where you want information stored
```python
tile = TileInfo("<data_directory>")
```
Then use the method to import information if there is already a TileInfo object saved in the directory
```python
tile = tile.import_info()
```
You can then add parameters used to the object, in the form of a dictionnary.
```python
tile.add_parameters({"parameter1" : value1, "parameter2" : value2})
```
It can then be retrieved using the parameter's key : `tile.parameters["parameter1"]`, if there is a conflict, for example if "parameter1" was already stored in the TileInfo object with a different value, `tile.parameters["Overwrite"]` is given the value `True`.

You can also add paths to the object. If directories and parent directories don't exist, they are created.
```python
tile.add_dirpath("vegetation_index_directory", tile.data_directory / "VegetationIndex") #Adding path to a directory
tile.add_path("forest_mask", tile.data_directory / TimelessMasks / "forest_mask.tif") #Adding path to a file
```
It can then be retrieved using the path's key : `tile.paths["vegetation_index_directory"]`, `tile.parameters["paths"]`.

The directories, and the parent directories to the files can be deleted :
```python
tile.delete_dirs("vegetation_index_directory","forest_mask")
```
Also, to print information stored in the object, simply use `tile.print_info()`.
Printing a TileInfo object information is also possible from the command line using the command `fordead read_tileinfo -o <data_directory>` (see [details](../../../cli.md#fordead-read_tileinfo)).

In the end, every addition and change to the object can be save using `tile.save_info()`.
