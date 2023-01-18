# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 10:52:12 2022

@author: rdutrieux
"""
import time
import click
import geopandas as gp
from pathlib import Path
from fordead.validation_module import preprocess_obs, get_grid_points, get_reflectance_at_points


import cProfile
import pstats

@click.command(name='export_reflectance')
@click.option("--obs_path", type = str,default = None, help = "", show_default=True)
@click.option("--sentinel_dir", type = str,default = None, help = "", show_default=True)
@click.option("--export_dir", type = str,default = None, help = "", show_default=True)
@click.option("--buffer", type = int,default = None, help = "", show_default=True)
@click.option("--name_column", type = str,default = None, help = "", show_default=True)
@click.option("--from_polygons",  is_flag=True, help = "If True, applies the mask from SENTINEL-data supplier", show_default=True)
def cli_export_reflectance(obs_path, sentinel_dir, export_dir, buffer, name_column, from_polygons):
    start_time_debut = time.time()

    with cProfile.Profile() as pr:
        export_reflectance(obs_path, sentinel_dir, export_dir, buffer, name_column, from_polygons)
        
    print("Export reflectance : %s secondes ---" % (time.time() - start_time_debut))
    
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(Path(export_dir) / "profiling_stats.prof")


def export_reflectance(obs_path, sentinel_dir, export_dir, buffer = None, name_column = "id", from_polygons = False):
    
    sentinel_dir = Path(sentinel_dir)
    obs = gp.read_file(obs_path)
    
    preprocessed_obs = preprocess_obs(obs, sentinel_dir, buffer, name_column)
    
    if from_polygons or (buffer is not None and buffer > 0):
        points = get_grid_points(preprocessed_obs, sentinel_dir, name_column)
        points.to_crs(preprocessed_obs.crs).to_file(Path(export_dir) / (str(Path(obs_path).stem) + "_grid.shp"))
    else:
        points = obs
    print("Extracting reflectance")
    reflectance = get_reflectance_at_points(points,sentinel_dir)

    reflectance.to_csv(Path(export_dir) / "reflectance.csv", index=False)

if __name__ == '__main__':

        # export_reflectance_from_polygons(
        #     obs_path = "D:/fordead/Data/Validation/Validation_data/Scolytes/ValidatedScolytes.shp",
        #     sentinel_dir = "D:/fordead/Data/Sentinel", 
        #     export_dir = "D:/fordead/Data/Test_programme",
        #     name_column = "Id")
        # export_reflectance_from_polygons(
        #     obs_path = "/mnt/fordead/Data/Vecteurs/ObservationsTerrain/ValidatedScolytes.shp",
        #     sentinel_dir = "/mnt/fordead/Data/Sentinel", 
        #     export_dir = "/mnt/fordead/Data",
        #     name_column = "Id")
        # export_reflectance_from_polygons(
        #     obs_path = "/mnt/fordead/Data/Vecteurs/Export_57_2022.shp",
        #     sentinel_dir = "/mnt/fordead/Data/Sentinel", 
        #     export_dir = "/mnt/fordead/Out/Validation/Gilette")
        export_reflectance(
            obs_path = "D:/fordead/Data/Test_programme/export_reflectance/Export_57_2022_grid.shp",
            sentinel_dir = "D:/fordead/Data/Test_programme/export_reflectance", 
            export_dir = "D:/fordead/Data/Test_programme/export_reflectance")
