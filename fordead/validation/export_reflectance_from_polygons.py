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
    
    start_time_debut = time.time()
    preprocessed_polygons = preprocess_polygons(polygons, sentinel_dir, buffer, name_column)
    print("Preprocessing polygons : %s secondes ---" % (time.time() - start_time_debut)) ; start_time_debut = time.time()
    
    grid_points = get_grid_points(preprocessed_polygons, sentinel_dir, name_column)
    grid_points.to_crs(preprocessed_polygons.crs).to_file(Path(export_dir) / (str(Path(polygons_path).stem) + "_grid.shp"))
    print("Making grid points : %s secondes ---" % (time.time() - start_time_debut)) ; start_time_debut = time.time()

    reflectance = get_reflectance_at_points(grid_points,sentinel_dir)
    print("Extracting reflectance : %s secondes ---" % (time.time() - start_time_debut)) ; start_time_debut = time.time()

    reflectance.to_csv(Path(export_dir) / "reflectance.csv", index=False)
    print("Writing reflectance : %s secondes ---" % (time.time() - start_time_debut)) ; start_time_debut = time.time()

if __name__ == '__main__':
    start_time_debut = time.time()
    import cProfile
    import pstats

    
    with cProfile.Profile() as pr:
        # export_reflectance_from_polygons(
        #     polygons_path = "D:/fordead/Data/Validation/Validation_data/Scolytes/ValidatedScolytes.shp",
        #     sentinel_dir = "D:/fordead/Data/Sentinel", 
        #     export_dir = "D:/fordead/Data/Test_programme",
        #     name_column = "Id")
        # export_reflectance_from_polygons(
        #     polygons_path = "/mnt/fordead/Data/Vecteurs/ObservationsTerrain/ValidatedScolytes.shp",
        #     sentinel_dir = "/mnt/fordead/Data/Sentinel", 
        #     export_dir = "/mnt/fordead/Data",
        #     name_column = "Id")
        export_reflectance_from_polygons(
            polygons_path = "/mnt/fordead/Data/Vecteurs/Export_57_2022.shp",
            sentinel_dir = "/mnt/fordead/Data/Sentinel", 
            export_dir = "/mnt/fordead/Out/Validation/Gilette")
        
    print("Export reflectance : %s secondes ---" % (time.time() - start_time_debut))

    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.print_stats()
    # stats.dump_stats("D:/fordead/Data/Test_programme/profiling_stats.prof")
    # stats.dump_stats("/mnt/fordead/Data/profiling_stats.prof")
    
    
    # raster_path = "D:/fordead/Data/Sentinel/SENTINEL2B_20220611-104734-621_L2A_T32ULU_C_V3-0_FRE_B8A.tif"



    
    # points.to_file("D:/fordead/Data/Test_programme/points_with_value.shp")
        

    
    #Parquet