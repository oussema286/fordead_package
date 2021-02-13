# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 18:20:18 2020

@author: Raphael Dutrieux
"""
import click
from fordead.ImportData import TileInfo
from fordead.masking_vi import rasterize_bdforet, clip_oso, raster_full
from fordead.writing_data import write_tif

@click.command(name='forest_mask')
@click.option("-o", "--data_directory",  type=str, help="Path of the output directory")
@click.option("-f", "--forest_mask_source",  type=str, default=None,
                    help="Source of the forest mask, accepts 'BDFORET', 'OSO', or None in which case all pixels will be considered valid")
@click.option("--dep_path",  type=str,
                    help="Path to shapefile containg departements with code insee. Optionnal, only used if forest_mask_source equals 'BDFORET'")
@click.option("--bdforet_dirpath",  type=str,
                    help="Path to directory containing BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
@click.option("--list_forest_type",  type=str,
                    default=["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"],
                    help="List of forest types to be kept in the forest mask, corresponds to the CODE_TFV of the BD FORET. Optionnal, only used if forest_mask_source equals 'BDFORET'")
@click.option("--path_oso",  type=str,
                    help="Path to soil occupation raster, only used if forest_mask_source = 'OSO' ")
@click.option("--list_code_oso",  type=str, default=[32],
                    help="List of values used to filter the soil occupation raster. Only used if forest_mask_source = 'OSO'")
@click.option("--path_example_raster",  type=str, default=None,
                    help="Path to raster from which to copy the extent, resolution, CRS...")
def compute_forest_mask(data_directory,
                        forest_mask_source = None,

                        list_forest_type = ["FF2-00-00", "FF2-90-90", "FF2-91-91", "FF2G61-61"],
                        dep_path = None,
                        bdforet_dirpath = None,
                        
                        path_oso = None,
                        list_code_oso = [32],
                        
                        path_example_raster = None
                        ):
    """
    Compute forest mask
    \f
    Parameters
    ----------
    data_directory
    forest_mask_source
    list_forest_type
    dep_path
    bdforet_dirpath
    path_oso
    list_code_oso
    path_example_raster

    Returns
    -------

    """
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.add_parameters({"forest_mask_source" : forest_mask_source, "list_forest_type" : list_forest_type, "list_code_oso" : list_code_oso})
    if tile.parameters["Overwrite"] : tile.delete_files("ForestMask" ,"periodic_results_decline","result_files","timelapse")

    if path_example_raster == None : path_example_raster = tile.paths["state_decline"]
    tile.add_path("ForestMask", tile.data_directory / "ForestMask" / "Forest_Mask.tif")
    
    if tile.paths["ForestMask"].exists():
        print("Forest mask already calculated")
    else:
        if forest_mask_source=="BDFORET":
            print("Computing forest mask from BDFORET")
            forest_mask = rasterize_bdforet(path_example_raster, dep_path, bdforet_dirpath, list_forest_type = list_forest_type)
            
        elif  forest_mask_source=="OSO":
            print("Computing forest mask from OSO")
            forest_mask = clip_oso(path_oso, path_example_raster, list_code_oso)
            
        elif forest_mask_source==None:
            print("No mask used, computing forest mask with every pixel marked as True")
            forest_mask = raster_full(path_example_raster, fill_value = 1, dtype = bool)
            
        else:
            print("Unrecognized forest_mask_source")

        write_tif(forest_mask, forest_mask.attrs,nodata = 0, path = tile.paths["ForestMask"])
        tile.save_info()
        
if __name__ == '__main__':
    # print(dictArgs)
    # start_time_debut = time.time()
    compute_forest_mask()
    # print("Computing forest mask : %s secondes ---" % (time.time() - start_time_debut))
