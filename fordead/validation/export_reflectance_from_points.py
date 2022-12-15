# -*- coding: utf-8 -*-
"""
Created on Tue Dec 13 10:52:12 2022

@author: rdutrieux
"""
import time
import geopandas as gp
import rasterio

def extract_raster_value(points,raster):
    
    reproj_points = points.to_crs(raster.crs)
    coord_list = [(x,y) for x,y in zip(reproj_points['geometry'].x , reproj_points['geometry'].y)]
    points['value'] = [x[0] for x in raster.sample(coord_list)]

    return points
        
if __name__ == '__main__':
    start_time_debut = time.time()

    points_path = "D:/fordead/Data/Test_programme/grid_scolytes.shp"
    raster_path = "D:/fordead/Data/Sentinel/SENTINEL2B_20220611-104734-621_L2A_T32ULU_C_V3-0_FRE_B8A.tif"

    points = gp.read_file(points_path)#.to_crs(raster_metadata["crs"])
    raster = rasterio.open(raster_path)
    
    points = extract_raster_value(points = points,
                         raster = raster)
    
    points.to_file("D:/fordead/Data/Test_programme/points_with_value.shp")
        

    print("Export reflectance : %s secondes ---" % (time.time() - start_time_debut))