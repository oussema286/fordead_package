# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 10:52:12 2022

@author: rdutrieux, kose
"""

import os
import click
import geopandas as gp
import pandas as pd
from pathlib import Path
from validation_stac_module import get_grid_points #, process_points
from stac_module import get_vectorBbox, getItemCollection

# @click.command(name='obs_to_s2_grid')
# @click.option("--obs_path", type = str,default = None, help = "Path to a vector file containing observation points or polygons, must have an ID column corresponding to name_column parameter", show_default=True)
# @click.option("--item_collection", type = str,default = None, help = "pystac itemcollection object", show_default=True)
# @click.option("--export_path", type = str,default = None, help = "Path used to write resulting vector file, with added 'epsg','area_name' and 'id_pixel' columns", show_default=True)
# @click.option("--name_column", type = str,default = "id", help = "Name of the ID column", show_default=True)
# def cli_obs_to_s2_grid(obs_path, sentinel_dir, export_path, buffer, name_column):
#     """
#     Attributes intersecting Sentinel-2 tiles to observation points or polygons, adding their epsg and name. If polygons are used, they are converted to grid points located at the centroid of Sentinel-2 pixels.
#     If points or polygons intersect several Sentinel-2 tiles, they are duplicated for each of them.
#     If some intersect no Sentinel-2 tiles, they are removed and their IDs are printed.

#     \f
#     Parameters
#     ----------
#     obs_path
#     item_collection
#     export_path
#     name_column

#     """
    
#     obs_to_s2_grid(obs_path, item_collection, export_path, name_column)

def obs_to_s2_grid(obs_path, item_collection, export_path, name_column = "id"):
    """
    Attributes intersecting Sentinel-2 tiles to observation points or polygons, adding their epsg and name. If polygons are used, they are converted to grid points located at the centroid of Sentinel-2 pixels.
    If points or polygons intersect several Sentinel-2 tiles, they are duplicated for each of them.
    If some intersect no Sentinel-2 tiles, they are removed and their IDs are printed.

    Parameters
    ----------
    obs_path : str
        Path to a vector file containing observation points or polygons, must have an ID column corresponding to name_column parameter.
    item_collection : pystac item_collection object
        list of S2 items
    export_path : str
        Path used to write resulting vector file, with added "epsg","area_name" and "id_pixel" columns.
    name_column : str, optional
        Name of the ID column. The default is "id".

    """
    
    obs = gp.read_file(obs_path)

    if os.path.exists(export_path):
        raise Exception(str(export_path) + " already exists")
    
    geom_type = obs.geom_type.drop(columns = "geometry")
    points = obs[(geom_type == 'Point') | (geom_type == 'MultiPoint')]
    polygons = obs[(geom_type == 'Polygon') | (geom_type == 'MultiPolygon')]
    
    
    
    points_from_poly = get_grid_points(polygons, item_collection, name_column) if len(polygons) != 0 else None

    total_points = pd.concat([points_from_poly])#,points_from_points])
    total_points.to_file(export_path)



    
if __name__ == '__main__':

    obs_path = "D:/PROJETS/PRJ_FORDEAD/TEST_STAC/data/observations_tuto.shp"
    export_path = "D:/PROJETS/PRJ_FORDEAD/TEST_STAC/data/export01.shp"

    obs_bbox = get_vectorBbox(obs_path)
    startDate = "2021-07-01"
    endDate = "2021-12-01"
    cloudPct = 20
    coll = getItemCollection(startDate, endDate, obs_bbox, cloudPct)
    
    obs_to_s2_grid(obs_path, coll, export_path, name_column = "id")