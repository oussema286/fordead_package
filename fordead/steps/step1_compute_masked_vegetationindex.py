# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 16:06:51 2020

@author: Raphaël Dutrieux

"""

#%% =============================================================================
#   LIBRARIES
# =============================================================================

# import time
import click
# from pathlib import Path
# import geopandas as gp

#%% ===========================================================================
#   IMPORT FORDEAD MODULES 
# =============================================================================



from fordead.fordead_process import process_info

#%% =============================================================================
#   FONCTIONS
# =============================================================================

@click.command(name='masked_vi')
@click.option("-i", "--input_directory", type = str, help = "Path of the directory with Sentinel dates")
@click.option("-o", "--data_directory", type = str, help = "Path of the output directory")
@click.option("-n", "--lim_perc_cloud", type = float,default = 0.4, help = "Maximum cloudiness at the tile scale, used to filter used SENTINEL dates. Set parameter as -1 to not filter based on cloudiness", show_default=True)
@click.option("--interpolation_order", type = int,default = 0, help ="interpolation order for bands at 20m resolution : 0 = nearest neighbour, 1 = linear, 2 = bilinéaire, 3 = cubique", show_default=True)
@click.option("--sentinel_source", type = str,default = "THEIA", help = "Source of data, can be 'THEIA' et 'Scihub' et 'PEPS'", show_default=True)
@click.option("--apply_source_mask",  is_flag=True, help = "If True, applies the mask from SENTINEL-data supplier", show_default=True)
@click.option("--soil_detection",  is_flag=True, help = "If True, bare ground is detected and used as mask, but the process has not been tested on other data than THEIA data in France (see https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/). If False, mask from formula_mask is applied.", show_default=True)
@click.option("--formula_mask", type = str,default = "(B2 >= 700)", help = "formula whose result would be binary, as described here https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#compute_vegetation_index. Is only used if soil_detection is False.", show_default=True)
@click.option("--vi", type = str,default = "CRSWIR", help = "Chosen vegetation index", show_default=True)
@click.option("--compress_vi",  is_flag=True, help = "Stores the vegetation index as low-resolution floating-point data as small integers in a netCDF file. Uses less disk space but can lead to very small difference in results as the vegetation is rounded to three decimal places", show_default=True)
@click.option("--ignored_period", multiple=True, type = str, default = None, help = "Period whose Sentinel dates to ignore (format 'MM-DD', ex : --ignored_period 11-01 --ignored_period 05-01", show_default=True)
@click.option("--extent_shape_path", type = str,default = None, help = "Path of shapefile used as extent of detection, if None, the whole tile is used", show_default=True)
@click.option("--path_dict_vi", type = str,default = None, help = "Path of text file to add vegetation index formula, if None, only built-in vegetation indices can be used (CRSWIR, NDVI)", show_default=True)
def cli_compute_masked_vegetationindex(
    input_directory,
    data_directory,
    lim_perc_cloud=0.4,
    interpolation_order = 0,
    sentinel_source = "THEIA",
    apply_source_mask = False,
    soil_detection = False, 
    formula_mask = "(B2 >= 700)",
    vi = "CRSWIR",
    compress_vi = False,
    ignored_period = None,
    extent_shape_path=None,
    path_dict_vi = None,
    ):
    """
    Computes masks and masked vegetation index for each SENTINEL date under a cloudiness threshold.
    The mask includes pixels ouside satellite swath, some shadows, and the mask from SENTINEL data provider if the option is chosen.
    Also, if soil detection is activated, the mask includes bare ground detection and cloud detection, but the process might only be adapted to THEIA data in France's coniferous forests.
    If it is not activated, then the user can choose a mask of his own using the formula_mask parameter.
    Results are written in the chosen directory.
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/
    \f

    """
    compute_masked_vegetationindex(input_directory,data_directory, lim_perc_cloud, interpolation_order, sentinel_source, apply_source_mask, soil_detection, formula_mask, vi, compress_vi, ignored_period, extent_shape_path, path_dict_vi)


def compute_masked_vegetationindex(
    input_directory,
    data_directory,
    lim_perc_cloud=0.4,
    interpolation_order = 0,
    sentinel_source = "THEIA",
    apply_source_mask = False,
    soil_detection = True,
    formula_mask = "(B2 >= 700)",
    vi = "CRSWIR",
    compress_vi = False,
    ignored_period = None,
    extent_shape_path=None,
    path_dict_vi = None
    ):
    """
    Computes masks and masked vegetation index for each SENTINEL date under a cloudiness threshold.
    Masks include shadows, clouds, soil, pixels ouside satellite swath, and the mask from SENTINEL data provider if the option is chosen.
    Results are written in the chosen directory.
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/
    
    Parameters
    ----------
    input_directory : str
        Path of the directory with Sentinel dates
    data_directory : str
        Path of the output directory
    lim_perc_cloud : float
        Maximum cloudiness at the tile scale, used to filter used SENTINEL dates. Set parameter as -1 to not filter based on cloudiness
    interpolation_order : int
        interpolation order for bands at 20m resolution : 0 = nearest neighbour, 1 = linear, 2 = bilinéaire, 3 = cubique
    sentinel_source : str
        Source of data, can be 'THEIA' et 'Scihub' et 'PEPS'
    apply_source_mask : bool
        If True, applies the mask from SENTINEL-data supplier
    soil_detection : bool
        If True, bare ground is detected and used as mask, but the process has not been tested on other data than THEIA data in France (see https://fordead.gitlab.io/fordead_package/docs/user_guides/english/01_compute_masked_vegetationindex/). If False, mask from formula_mask is applied.
    formula_mask : str
        formula whose result would be binary, as described here https://fordead.gitlab.io/fordead_package/reference/fordead/masking_vi/#compute_vegetation_index. Is only used if soil_detection is False.
    vi : str
        Chosen vegetation index
    compress_vi : bool
        If True, stores the vegetation index as low-resolution floating-point data as small integers in a netCDF file. Uses less disk space but can lead to very small difference in results as the vegetation index is rounded to three decimal places
    ignored_period : list of two strings
        Period whose Sentinel dates to ignore (format 'MM-DD', ex : ["11-01","05-01"]
    extent_shape_path : str
        Path of shapefile used as extent of detection, if None, the whole tile is used
    path_dict_vi : str
        Path of text file to add vegetation index formula, if None, only built-in vegetation indices can be used (CRSWIR, NDVI)

    """
    # Creation of TileInfo object. If it already exists in the specified directory, it is imported. 
    fordead_process = process_info(data_directory)
    # fordead_process = fordead_process.import_info()
    
    fordead_process.init_step("compute_vegetation_index_and_masks", 
                              {"lim_perc_cloud" : lim_perc_cloud, 
                               "interpolation_order" : interpolation_order, 
                               "sentinel_source" : sentinel_source, 
                               "apply_source_mask" : apply_source_mask, 
                               "vi" : vi, "extent_shape_path" : extent_shape_path, 
                               "path_dict_vi" : path_dict_vi, 
                               "soil_detection" : soil_detection,
                               "formula_mask" : formula_mask, 
                               "ignored_period" : ignored_period, 
                               "compress_vi" : compress_vi})
    
    fordead_process.compute_vegetation_index_and_masks()
    fordead_process.update_step()
    
    
if __name__ == '__main__':
    # start_time_debut = time.time()
    cli_compute_masked_vegetationindex()
    # print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))


