# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 10:52:12 2022

@author: rdutrieux
"""
import time
from datetime import timedelta
import click
import geopandas as gp
import pandas as pd
from pathlib import Path
# from fordead.reflectance_extraction import get_reflectance_at_points
from fordead.cli.utils import empty_to_none
from fordead.reflectance_extraction import get_already_extracted, extract_raster_values
from fordead.stac.stac_module import get_bbox, get_harmonized_planetary_collection, get_harmonized_theia_collection, get_harmonized_dinamis_collection
import traceback

import numpy as np

@click.command(name='extract_reflectance')
@click.option("--obs_path", type = str,default = None, help = "Path to a vector file containing observation points, must have an ID column corresponding to name_column parameter, an 'area_name' column with the name of the Sentinel-2 tile from which to extract reflectance, and a 'espg' column containing the espg integer corresponding to the CRS of the Sentinel-2 tile.", show_default=True)
@click.option("--sentinel_source", type = str,default = None, help = "Can be either the path of the directory containing Sentinel-2 Theia data, or 'Planetary' for 'sentinel-2-l2a' Microsoft Planetary Computer STAC collection, or 'Dinamis' for 's2-theia' CDS Theia Montpellier S2 STAC collection.", show_default=True)
@click.option("--export_path", type = str,default = None, help = "Path to write csv file with extracted reflectance", show_default=True)
@click.option("--cloudiness_path", type = str, default = None, help = "Path of a csv with the columns 'area_name','Date' and 'cloudiness', can be calculated by the [extract_cloudiness function](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/03_extract_cloudiness/). Can be ignored if sentinel_source is 'Planetary'")
@click.option("-n", "--lim_perc_cloud", type = float,default = 0.4, help = "Maximum cloudiness at the tile scale, used to filter used SENTINEL dates. Set parameter as -1 to not filter based on cloudiness", show_default=True)
@click.option("--name_column", type = str,default = "id", help = "Name of the ID column", show_default=True)
@click.option("-b","--bands_to_extract", type=str, multiple=True, default = ["B2","B3","B4","B5","B6","B7","B8","B8A","B11", "B12", "Mask"], help = "Bands to extract ex : -b B2 -b  B3 -b B11", show_default=True)
@click.option("-t","--tile_selection", type=str, multiple=True, default = None, help = "List of tiles from which to extract reflectance (ex : -t T31UFQ -t T31UGQ). If None, all tiles are extracted.", show_default=True)
@click.option("--start_date", type = str,default = "2015-01-01", help = "First date of the period from which to extract reflectance.", show_default=True)
@click.option("--end_date", type = str,default = "2030-01-01", help = "Last date of the period from which to extract reflectance.", show_default=True)
def cli_extract_reflectance(**kwargs):
    """
    Extracts reflectance from Sentinel-2 data using a vector file containing points, exports the data to a csv file.
    If new acquisitions are added to the Sentinel-2 directory, new data is extracted and added to the existing csv file.
    
    \f

    """
    empty_to_none(kwargs, "bands_to_extract")
    empty_to_none(kwargs, "tile_selection")
    extract_reflectance(**kwargs)

def extract_reflectance(obs_path,
                        sentinel_source, 
                        export_path, 
                        name_column = "id", 
                        cloudiness_path = None, 
                        lim_perc_cloud = 1,
                        bands_to_extract = ["B2","B3","B4","B5","B6","B7","B8","B8A","B11", "B12", "Mask"],
                        tile_selection = None,
                        start_date = "2015-01-01",
                        end_date = "2030-01-01",
                        overwrite = False):
    """
    Extracts reflectance from Sentinel-2 data using a vector file containing points, exports the data to a csv file.
    If new acquisitions are added to the Sentinel-2 directory, new data is extracted and added to the existing csv file.

    Parameters
    ----------
    obs_path : str
        Path to a vector file containing observation points, must have an ID column corresponding to name_column parameter, an 'area_name' column with the name of the Sentinel-2 tile from which to extract reflectance, and a 'espg' column containing the espg integer corresponding to the CRS of the Sentinel-2 tile.
    sentinel_source : str
        Can be either the path of the directory containing Sentinel-2 Theia data, or 'Planetary' for 'sentinel-2-l2a' Microsoft Planetary Computer STAC collection, or 'Dinamis' for 's2-theia' CDS Theia Montpellier S2 STAC collection.
    export_path : str
        Path to write csv file with extracted reflectance.
    cloudiness_path : str
        Path of a csv with the columns 'area_name','Date' and 'cloudiness', can be calculated by the [extract_cloudiness function](https://fordead.gitlab.io/fordead_package/docs/Tutorials/Validation/03_extract_cloudiness/). Can be ignored if sentinel_source is 'Planetary'
    lim_perc_cloud : float
        Maximum cloudiness at the tile scale, used to filter used SENTINEL dates. Between 0 and 1.
    name_column : str, optional
        Name of the ID column. The default is "id".
    bands_to_extract : list
        List of bands to extract
    tile_selection : list
        List of tiles from which to extract reflectance (ex : ["T31UFQ", "T31UGQ"]). If None, all tiles are extracted.
    start_date : str
        First date of the period from which to extract reflectance
    end_date : str
        Last date of the period from which to extract reflectance
    overwrite : bool
        If True, overwrites the csv file if it already exists. The default is False.
    
    """
    
    # if sentinel_source == 'Planetary':
        
    
    export_path = Path(export_path)
    if export_path.exists():
        if not overwrite:
            print("File already exists:"+ str(export_path))
            print("It will be completed with new observations.")
        else:
            print("Removing " + str(export_path))
            export_path.unlink()
    obs = gp.read_file(obs_path)
    
    if (sentinel_source != "Planetary") and (cloudiness_path is not None):
        cloudiness = pd.read_csv(cloudiness_path)

    if tile_selection is None:
        tile_selection = np.unique(obs.area_name)

    if isinstance(tile_selection, str):
        tile_selection = [tile_selection]

    extracted_reflectance = get_already_extracted(export_path, name_column, bands_to_extract)

    start = time.time()
    for tile in tile_selection:

        tile_obs = obs[obs["area_name"] == tile]
        if len(tile_obs)==0:
            print("No observations in selected tile "+ tile)
        else:
            start_tile = time.time()
            tile_obs = tile_obs.to_crs(epsg = tile_obs.epsg.values[0])
            
            unfinished = True
            by_chunk = True
            chunksize = 512
            while unfinished:
                try:                    
                    tile_already_extracted = None
                    if extracted_reflectance is not None:
                        tile_already_extracted = extracted_reflectance[extracted_reflectance["area_name"] == tile]
                    
                    if sentinel_source == "Planetary":
                        collection = get_harmonized_planetary_collection(
                            start_date, end_date, get_bbox(tile_obs),
                            lim_perc_cloud, tile, sign=True)
                    elif sentinel_source == "Dinamis":
                        collection = get_harmonized_dinamis_collection(
                            start_date, end_date, get_bbox(tile_obs),
                            lim_perc_cloud, tile, sign=True)
                    else:                        
                        tile_cloudiness = cloudiness[cloudiness["area_name"] == tile] if cloudiness_path is not None else None
                        collection = get_harmonized_theia_collection(sentinel_source, tile_cloudiness, start_date, end_date, lim_perc_cloud, tile)
                        chunksize = 100
                    extract_raster_values(
                        collection, tile_obs, bands_to_extract, tile_already_extracted,
                        export_path, by_chunk=by_chunk, chunksize=chunksize,
                        dropna=True, dtype=int
                        )
                    unfinished = False
                except Exception as e:
                    # traceback_str = traceback.format_exc()
                    # print(f"Error: {e}")
                    print(traceback.format_exc())
                    # print(f"Error: {e}\nTraceback:\n{traceback_str}")
                    print("Retrying...")
                    extracted_reflectance = get_already_extracted(export_path, name_column, bands_to_extract)
            end_tile = time.time()
            print(f"Time for reflectance extraction in {tile}: {timedelta(seconds=end_tile-start_tile)}")
    end = time.time()
    print(f"Total time for reflectance extraction: {timedelta(seconds=end-start)}")


if __name__ == '__main__':
        
        #Locally
        # extract_reflectance(
        #     obs_path = "D:/fordead/fordead_data/calval_output/preprocessed_obs_tuto.shp",
        #     sentinel_source = "D:/fordead/fordead_data/sentinel_data/validation_tutorial/sentinel_data", 
        #     cloudiness_path = "D:/fordead/fordead_data/calval_output/extracted_cloudiness.csv",
        #     lim_perc_cloud = 0.4,
        #     export_path = "D:/fordead/fordead_data/calval_output/test_extract_theia1.csv",
        #     name_column = "id",
        #     start_date = "2018-01-01",
        #     end_date = "2018-03-01")
        
        # extract_reflectance(
        #     obs_path = "D:/fordead/fordead_data/calval_output/preprocessed_obs_tuto.shp",
        #     sentinel_source = "D:/fordead/fordead_data/sentinel_data/validation_tutorial/sentinel_data", 
        #     # cloudiness_path = "D:/fordead/fordead_data/calval_output/extracted_cloudiness.csv",
        #     # lim_perc_cloud = 0.4,
        #     export_path = "D:/fordead/fordead_data/calval_output/test_extract_theia2.csv",
        #     name_column = "id",
        #     start_date = "2018-01-01",
        #     end_date = "2018-03-01")
        
        # # #Planetary
        extract_reflectance(
            obs_path = "D:/fordead/fordead_data/calval_output/preprocessed_obs_tuto.shp",
            sentinel_source = "Planetary", 
            export_path = "D:/fordead/fordead_data/calval_output/test_extract_planetary.csv",
            name_column = "id",
            lim_perc_cloud = 0.4,
            start_date = "2022-01-01",
            end_date = "2022-04-01")