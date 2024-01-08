# Adding an ID and applying a buffer

This step aims at preprocessing a vector file containing observation points or polygons. It adds an ID column if one does not already exist, and can also apply a buffer to erode or dilate observations.

It is optional if one uses a dataset which already contains an ID column and does not which to apply a buffer to it.

#### INPUTS

The input parameters are:

- **obs_path** : Path of vector file containing observation points or polygons to preprocess
- **export_path** : Path used to export the resulting preprocessed observation points or polygons
- **buffer** *(optional)* : Length in meters of the buffer used to dilate (positive integer) or erode (negative integer) the observations. If None, no buffer is applied. Some observations may disappear completely if a negative buffer is applied. 
- **name_column** (*optional*) : Name of the column used to identify observations. If the column doesn't already exists, it is added as an integer between 1 and the number of observations. The default is "id".

#### OUTPUT

The output is a vector file at **export_path** derived from the vector file at **obs_path**, with up to two modifications :
- An ID attribute named after the **name_column** parameter is added, if not already present.
- A buffer can be applied, positive or negative

## How to use
### From a script

```bash
from fordead.validation.preprocess_obs import preprocess_obs

preprocess_obs(obs_path = <obs_path>, export_path = <export_path>, name_column = <name_column>, buffer = <buffer>)

```

### From the command line

```bash
fordead preprocess_obs [OPTIONS]
```

See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-preprocess_obs)

## How it works

### Importing the vector file containing observations
The vector file at **obs_path** is imported using the geopandas package.

### Adding an ID column to the vector
If **name_column** does not exist in the vector file, each observation is attributed an ID from 1 to the length of the GeoDataFrame object.
> **_Functions used:_** [attribute_id_to_obs()](https://fordead.gitlab.io/fordead_package/reference/fordead/reflectance_extraction/#attribute_id_to_obs)

### Applying a buffer
If the **buffer** parameter is used, a buffer is applied on the observations to erode if buffer is negative, or to dilate if it is positive.
> **_Functions used:_** [buffer_obs()](https://fordead.gitlab.io/fordead_package/reference/fordead/reflectance_extraction/#buffer_obs)

### Exporting the resulting the vector file
The modified GeoDataFrame object is exported to **export_path**.