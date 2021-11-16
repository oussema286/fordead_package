# Downloading and preprocessing Sentinel-2 data from THEIA

Though this package is meant to be used with Sentinel-2 data from any provider (Scihub, PEPS or THEIA), it has been mainly used and tested using THEIA data and it provides tools to easily download and preprocess the required data.
This tool can be used either from a script or from the command line, and automatically downloads all Sentinel-2 data from THEIA between two dates under a cloudiness threshold. Then this data is unzipped, keeping only chosen bands from Flat REflectance data, and zip files can be emptied as a way to save storage space.
Finally, if two Sentinel-2 directories come from the same acquisition date, they are merged by replacing no data pixels from one directory with pixels with data in the other, before removing the latter directory.

#### INPUTS
The input parameters are:

- **zipped_directory**: Path of the directory with zipped theia data
- **unzipped_directory**: Path of the output directory
- **tiles** : Name of the tiles to be downloaded (format : T31UFQ)
- **login_theia** : Login of your theia account
- **password_theia** : Password of your theia account
- **level** : Product level for reflectance products, can be 'LEVEL1C', 'LEVEL2A' or 'LEVEL3A'
- **start_date** : start date, fmt('2015-12-22')
- **end_date** : end date, fmt('2015-12-22')
- **lim_perc_cloud** : Maximum cloudiness in SENTINEL dates downloaded (%)
- **bands** : List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, as well as CLMR2, CLMR2, EDGR1, EDGR2, SATR1, SATR2 for LEVEL2A data, and DTS1, DTS2, FLG1, FLG2, WGT1, WGT2 for LEVEL3A)
- **correction_type** : Chosen correction type ('SRE' or 'FRE' for LEVEL2A data, 'FRC' for LEVEL3A)
- **empty_zip** : If True, the zip files are emptied as a way to save space

#### OUTPUTS
In the **unzipped_directory**, a directory is created for each tile, containing a directory for each Sentinel-2 acquisition corresponding to the chosen parameters, containing a file for each chosen band in Flat REflectance.
In the **zipped_directory**, a zip file for each Sentinel-2 acquisition, empty or not depending on the **empty_zip** parameter.

## Examples of use
### From a script

```bash
from fordead.cli.cli_theia_preprocess import theia_preprocess
theia_preprocess(zipped_directory = <zipped_directory>, unzipped_directory = <unzipped_directory>, tiles = ["T31UFQ","T31UFP"], login_theia = <login_theia>, password_theia = <password_theia>, level = "LEVEL2A", start_date = "2015-01-01", end_date = "2025-01-01", lim_perc_cloud = 50, bands = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12", "CLMR2"], empty_zip = True)
```

### From the command line

```bash
fordead theia_preprocess -i <zipped_directory> -o <unzipped_directory> -t T31UFQ -t T31UFP --login_theia <login_theia> --password_theia <password_theia> --level LEVEL2A --start_date 2015-01-01 --end_date 2025-01-01 -n 50 -b B2 -b B3 -b B4 -b B5 -b B6 -b B7 -b B8 -b B8A -b B11 -b B12 -b CLMR2 --empty_zip
```

See detailed documentation on the [site](https://fordead.gitlab.io/fordead_package/docs/cli/#fordead-theia_preprocess)

## Other ways to download THEIA data

Information about THEIA products can be found on the [THEIA website](https://www.theia-land.fr/), and you can find the catalog [here](https://theia.cnes.fr/atdistrib/rocket/#/search?collection=SENTINEL2).
You can also use the [theia_download package by Olivier Hagolle](https://github.com/olivierhagolle/theia_download) whose simplified code is used in this tool.