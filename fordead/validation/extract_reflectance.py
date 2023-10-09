# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 10:52:12 2022

@author: rdutrieux
"""
import time
import click
import geopandas as gp
from pathlib import Path
from fordead.validation_module import get_reflectance_at_points, get_already_extracted


@click.command(name='extract_reflectance')
@click.option("--obs_path", type = str,default = None, help = "Path to a vector file containing observation points, must have an ID column corresponding to name_column parameter, an 'area_name' column with the name of the Sentinel-2 tile from which to extract reflectance, and a 'espg' column containing the espg integer corresponding to the CRS of the Sentinel-2 tile.", show_default=True)
@click.option("--sentinel_dir", type = str,default = None, help = "Path of the directory containing Sentinel-2 data.", show_default=True)
@click.option("--export_path", type = str,default = None, help = "Path to write csv file with extracted reflectance", show_default=True)
@click.option("--name_column", type = str,default = "id", help = "Name of the ID column", show_default=True)
@click.option("-b","--bands_to_extract", type = list, default = ["B2","B3","B4","B5","B6","B7","B8","B8A","B11", "B12", "Mask"], help = "Bands to extract ex : -b B2 -b  B3 -b B11", show_default=True)
@click.option("-t","--tile_selection", type = list, default = None, help = "List of tiles from which to extract reflectance (ex : -t T31UFQ -t T31UGQ). If None, all tiles are extracted.", show_default=True)
# @click.option("--export_path_cloudiness", type = str, default = None, help = "Path to ", show_default=True)
def cli_extract_reflectance(obs_path, sentinel_dir, export_path, name_column, bands_to_extract, tile_selection):
    """
    Extracts reflectance from Sentinel-2 data using a vector file containing points, exports the data to a csv file.
    If new acquisitions are added to the Sentinel-2 directory, new data is extracted and added to the existing csv file.
    
    \f

    """
    
    start_time_debut = time.time()
    extract_reflectance(**locals())
    print("Exporting reflectance : %s secondes ---" % (time.time() - start_time_debut))


def extract_reflectance(obs_path, sentinel_dir, export_path, name_column = "id", 
                        bands_to_extract = ["B2","B3","B4","B5","B6","B7","B8","B8A","B11", "B12", "Mask"],
                        tile_selection = None):
    """
    Extracts reflectance from Sentinel-2 data using a vector file containing points, exports the data to a csv file.
    If new acquisitions are added to the Sentinel-2 directory, new data is extracted and added to the existing csv file.

    Parameters
    ----------
    obs_path : str
        Path to a vector file containing observation points, must have an ID column corresponding to name_column parameter, an 'area_name' column with the name of the Sentinel-2 tile from which to extract reflectance, and a 'espg' column containing the espg integer corresponding to the CRS of the Sentinel-2 tile.
    sentinel_dir : str
        Path of the directory containing Sentinel-2 data.
    export_path : str
        Path to write csv file with extracted reflectance.
    name_column : str, optional
        Name of the ID column. The default is "id".
    bands_to_extract : list
        List of bands to extract
    tile_selection : list
        List of tiles from which to extract reflectance (ex : ["T31UFQ", "T31UGQ"]). If None, all tiles are extracted.
    """
    
    sentinel_dir = Path(sentinel_dir) ; export_path = Path(export_path)
    obs = gp.read_file(obs_path)
    
    extracted_reflectance = get_already_extracted(export_path, obs, obs_path, name_column)

    reflectance = get_reflectance_at_points(obs, sentinel_dir, extracted_reflectance, name_column, bands_to_extract, tile_selection)
    
    if reflectance is None:
        print("No new data to extract")
    else:
        print("Data extracted")
        reflectance.to_csv(export_path, mode='a', index=False, header=not(export_path.exists()))

if __name__ == '__main__':

        extract_reflectance(
            obs_path = "D:/fordead/fordead_data/output/pp_observations_tuto.shp",
            sentinel_dir = "D:/fordead/fordead_data/sentinel_data/validation_tutorial/sentinel_data", 
            export_path = "D:/fordead/fordead_data/output/reflectance_tuto.csv",
            name_column = "id")
        
