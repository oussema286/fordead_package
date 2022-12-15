# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 10:52:12 2022

@author: rdutrieux
"""
import time
import geopandas as gp
from pathlib import Path
# import rasterio
from fordead.validation import preprocess_polygons, get_grid_points, get_reflectance_at_points

def export_reflectance_from_polygons(polygons_path, sentinel_dir, export_dir, buffer = None, name_column = "id"):
    
    sentinel_dir = Path(sentinel_dir)
    polygons = gp.read_file(polygons_path)
    
    print("Preprocessing polygons")
    preprocessed_polygons = preprocess_polygons(polygons, sentinel_dir, buffer, name_column)
    
    print("Making grid points")
    grid_points = get_grid_points(preprocessed_polygons, sentinel_dir, name_column)
    
    print("Extracting reflectance")
    reflectance = get_reflectance_at_points(grid_points,sentinel_dir)
        
    print("Writing reflectance")
    grid_points.to_file(Path(export_dir) / (str(Path(polygons_path).stem) + "_grid.shp"))
    reflectance.to_csv(Path(export_dir) / "reflectance.csv", index=False)

if __name__ == '__main__':
    start_time_debut = time.time()

    # sentinel_dir = "D:/fordead/Data/Sentinel"
    
    
    # raster_path = "D:/fordead/Data/Sentinel/SENTINEL2B_20220611-104734-621_L2A_T32ULU_C_V3-0_FRE_B8A.tif"

    export_reflectance_from_polygons(
        polygons_path = "/mnt/fordead/Data/Vecteurs/ObservationsTerrain/ValidatedScolytes.shp",
        sentinel_dir = "/mnt/fordead/Data/Sentinel", 
        export_dir = "/mnt/fordead/Data",
        name_column = "Id")
    
    # export_reflectance_from_polygons(
    #     polygons_path = "D:/fordead/Data/Validation/Validation_data/Scolytes/ValidatedScolytes.shp",
    #     sentinel_dir = "D:/fordead/Data/Sentinel", 
    #     export_dir = "D:/fordead/Data/Test_programme",
    #     name_column = "Id")
    
    # points.to_file("D:/fordead/Data/Test_programme/points_with_value.shp")
        

    print("Export reflectance : %s secondes ---" % (time.time() - start_time_debut))