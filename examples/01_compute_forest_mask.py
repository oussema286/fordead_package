# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 18:20:18 2020

@author: admin
"""
import rioxarray
import argparse
import time
from fordead.ImportData import TileInfo
from fordead.masking_vi import rasterize_bdforet
from fordead.writing_data import write_tif
import xarray as xr

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--data_directory", dest = "data_directory",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/output_detection/ZoneTest", help = "Path of the output directory")
    parser.add_argument("-e", "--path_example_raster", dest = "path_example_raster",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/input_sentinel/ZoneTest/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1/SENTINEL2A_20151203-105818-575_L2A_T31UFQ_D_V1-1_FRE_B2.tif", help = "Path to raster from which to copy the extent, resolution, CRS...")
    parser.add_argument("-f", "--forest_mask_source", dest = "forest_mask_source",type = str,default = "OSO", help = "Source of the forest mask, accepts 'BDFORET', 'OSO', or None in which case all pixels will be considered valid")
    parser.add_argument("-d", "--dep_path", dest = "dep_path",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/Departements/departements-20140306-100m.shp", help = "Path to shapefile containg departements with code insee. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("-b", "--bdforet_dirpath", dest = "bdforet_dirpath",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/Vecteurs/BDFORET", help = "Path to directory containing BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("-l", "--list_forest_type", dest = "list_forest_type",type = str,default = ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"], help = "List of forest types to be kept in the forest mask, corresponds to the CODE_TFV of the BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
    parser.add_argument("-s", "--path_oso", dest = "path_oso",type = str,default = "C:/Users/admin/Documents/Deperissement/fordead_data/OCS_2017_CESBIO.tif", help = "Path to soil occupation raster, only used if forest_mask_source = 'OSO' ")
    parser.add_argument("-n", "--list_code_oso", dest = "list_code_oso",type = str,default = [32], help = "List of values used to filter the soil occupation raster. Only used if forest_mask_source = 'OSO'")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs

def compute_forest_mask(data_directory,
                        path_example_raster,
                        forest_mask_source,
                        
                        list_forest_type = None,
                        dep_path = None,
                        bdforet_dirpath = None,
                        
                        path_oso = None,
                        list_code_oso = None
                        ):
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"forest_mask_source" : forest_mask_source, "list_forest_type" : list_forest_type})
    if tile.parameters["Overwrite"] : tile.delete_dirs("VegetationIndexDir", "MaskDir", "ForestMask","coeff_model", "AnomaliesDir","state_decline")

    tile.add_path("ForestMask", tile.data_directory / "ForestMask" / "Forest_Mask.tif")
    
    if tile.paths["ForestMask"].exists():
        print("Forest mask already calculated")
    else:
        if forest_mask_source=="BDFORET":
            forest_mask = rasterize_bdforet(path_example_raster, dep_path, bdforet_dirpath, list_forest_type = list_forest_type)
            
        elif  forest_mask_source=="OSO":
            example_raster = xr.open_rasterio(path_example_raster)
            OSO = xr.open_rasterio(path_oso)
            example_raster.attrs["nodata"] = 0 #Avoids bug in reproject when nodata = nan and dtype = int
            reprojected_corner1 = example_raster.isel(x=[0,1],y=[0,1]).rio.reproject(OSO.crs).isel(x=0,y=0)
            reprojected_corner2 = example_raster.isel(x=[-2,-1],y=[-2,-1]).rio.reproject(OSO.crs).isel(x=-1,y=-1)
            clipped_OSO = OSO.rio.clip_box(
                                        minx=float(reprojected_corner1.x),
                                        miny=float(reprojected_corner2.y),
                                        maxx=float(reprojected_corner2.x),
                                        maxy=float(reprojected_corner1.y),
                                        )
            reprojected_clipped_OSO = clipped_OSO.rio.reproject(example_raster.crs)
            forest_mask = reprojected_clipped_OSO.isin(list_code_oso)
            forest_mask.attrs = example_raster.attrs
            forest_mask=forest_mask.sel(band=1)
            
        elif forest_mask_source==None:
            example_raster = xr.open_rasterio(path_example_raster)
            example_raster.squeeze
            example_raster=example_raster.sel(band=1)
            example_raster.attrs["crs"]=example_raster.crs.replace("+init=","") #Remove "+init=" which it deprecated
            example_raster[:,:]=1
            forest_mask=example_raster.astype(bool)
        else:
            print("Unrecognized forest_mask_source")


        write_tif(forest_mask, forest_mask.attrs,nodata = 0, path = tile.paths["ForestMask"])
        tile.save_info()
if __name__ == '__main__':
    dictArgs=parse_command_line()
    # print(dictArgs)
    start_time_debut = time.time()
    compute_forest_mask(**dictArgs)
    print("Computing forest mask : %s secondes ---" % (time.time() - start_time_debut))
