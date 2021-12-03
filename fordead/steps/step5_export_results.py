# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:32:57 2020

@author: Raphaël Dutrieux
"""

import click
from fordead.import_data import import_dieback_data, TileInfo, import_forest_mask, import_soil_data, import_stress_data, import_stress_index
from fordead.writing_data import vectorizing_confidence_class, get_bins, convert_dateindex_to_datenumber, get_periodic_results_as_shapefile, get_state_at_date, union_confidence_class, write_tif
import numpy as np
import geopandas as gp
import pandas as pd

@click.command(name='export_results')
@click.option("-o", "--data_directory",  type=str, help="Path of the output directory", show_default=True)
@click.option("--start_date",  type=str, default='2015-06-23',
                    help="Start date for exporting results", show_default=True)
@click.option("--end_date",  type=str, default="2022-01-02",
                    help="End date for exporting results", show_default=True)
@click.option("--frequency",  type=str, default='M',
                    help="Frequency used to aggregate results, if value is 'sentinel', then periods correspond to the period between sentinel dates used in the detection, or it can be the frequency as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)", show_default=True)
@click.option("--multiple_files",  is_flag=True,
                    help="If True, one shapefile is exported for each period containing the areas in dieback at the end of the period. Else, a single shapefile is exported containing diebackd areas associated with the period of dieback", show_default=True)
@click.option("-t", "--conf_threshold_list", type = list, default = None, help = "List of thresholds used as bins to discretize the confidence index into several classes", show_default=True)
@click.option("-c", "--conf_classes_list", type = list, default = None, help = "List of classes names, if conf_threshold_list has n values, conf_classes_list must have n+1 values", show_default=True)
@click.option("--export_stress",  is_flag=True,
                    help="If True, stress periods are exported as polygons containing the period when each stress period started, and stress class if conf_threshold_list and conf_classes_list are given", show_default=True)
def cli_export_results(
    data_directory,
    start_date = '2015-06-23',
    end_date = "2022-01-02",
    frequency = 'M',
    multiple_files = False,
    conf_threshold_list = None,
    conf_classes_list = None,
    export_stress = False
    ):
    """
    Export results to a vectorized shapefile format.
    \f

    Parameters
    ----------
    data_directory
    start_date
    end_date
    frequency
    multiple_files
    conf_threshold_list
    conf_classes_list
    export_stress

    Returns
    -------

    """
    export_results(data_directory, start_date, end_date, frequency, multiple_files, conf_threshold_list, conf_classes_list, export_stress)



def export_results(
    data_directory,
    start_date = '2015-06-23',
    end_date = "2022-01-02",
    frequency = 'M',
    multiple_files = False,
    conf_threshold_list = None,
    conf_classes_list = None,
    export_stress = False
    ):
    """
    Writes results in the chosen period, form and using chosen frequency.
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/english/05_export_results/
    \f

    Parameters
    ----------
    data_directory : str
        Path of the output directory
    start_date : str
        Start date for exporting results (format : 'YYYY-MM-DD')
    end_date : str
        End date for exporting results (format : 'YYYY-MM-DD')
    frequency : str
        Frequency used to aggregate results, if value is 'sentinel', then periods correspond to the period between sentinel dates used in the detection, or it can be the frequency as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)
    multiple_files : bool
        If True, one shapefile is exported for each period containing the areas in dieback at the end of the period. Else, a single shapefile is exported containing diebackd areas associated with the period of dieback
    conf_threshold_list : list
        List of thresholds used as bins to discretize the confidence index into several classes
    conf_classes_list : list
        List of classes names, if conf_threshold_list has n values, conf_classes_list must have n+1 values
    export_stress : bool
        If True, stress periods are exported as polygons containing the period when each stress period started, and stress class if conf_threshold_list and conf_classes_list are given.
    
    Returns
    -------

    """
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    dieback_data = import_dieback_data(tile.paths, chunks= None)
    tile.add_parameters({"start_date" : start_date,"end_date" : end_date, "frequency" : frequency, "multiple_files" : multiple_files, "conf_threshold_list": conf_threshold_list, "conf_classes_list" : conf_classes_list, "export_stress" : export_stress})
    if tile.parameters["Overwrite"] : 
        tile.delete_dirs("periodic_results_dieback","result_files") #Deleting previous detection results if they exist
        tile.delete_attributes("last_date_export")
        
    tile.add_path("confidence_index", tile.data_directory / "Results" / "confidence_index.tif")
    tile.add_path("stress_periods", tile.data_directory / "Results" / "stress_periods.shp")

    exporting = (tile.dates[-1] != tile.last_date_export) if hasattr(tile, "last_date_export") else True
    if exporting:
        print("Exporting results")
        bins_as_date, bins_as_datenumber = get_bins(start_date,end_date,frequency,tile.dates)
        first_date_number = convert_dateindex_to_datenumber(dieback_data.first_date,dieback_data.state, tile.dates)
    
        if tile.parameters["soil_detection"]:
            soil_data = import_soil_data(tile.paths, chunks= 1280)
            first_date_number_soil = convert_dateindex_to_datenumber(soil_data.first_date, soil_data.state, tile.dates)
            
        forest_mask = import_forest_mask(tile.paths["ForestMask"], chunks= 1280)
        valid_area = import_forest_mask(tile.paths["valid_area_mask"], chunks= 1280)
        relevant_area = forest_mask & valid_area
        
        if export_stress:
            stress_index = import_stress_index(tile.paths["stress_index"])
            stress_data = import_stress_data(tile.paths)
            stress_list = []
            for period in range(tile.parameters["max_nb_stress_periods"]):
                print(period)
                stress_period = stress_index.isel(period = period)
                print("confidence")
                stress_class = vectorizing_confidence_class(stress_period, stress_data.nb_dates.isel(period = period), (relevant_area & (period < stress_data["nb_periods"])).compute(), conf_threshold_list, np.array(conf_classes_list), tile.raster_meta["attrs"])
                
                stress_start_date = stress_data["date"].isel(change = period*2)
                stress_start_date_number = convert_dateindex_to_datenumber(stress_start_date, period < stress_data["nb_periods"], tile.dates)
                print("periodic")
                vector_stress_start = get_periodic_results_as_shapefile(stress_start_date_number, bins_as_date, bins_as_datenumber, relevant_area, forest_mask.attrs)
                print("union")
                stress_list += [union_confidence_class(vector_stress_start, stress_class)]
                # if period ==0:
                #     stress_total = union_confidence_class(vector_stress_start, stress_class)
                # else:
                #     stress_total = stress_total.append(union_confidence_class(vector_stress_start, stress_class))
            print("concat")
            stress_total = gp.GeoDataFrame( pd.concat(stress_list, ignore_index=True), crs=stress_list[0].crs)
            stress_total.to_file(tile.paths["stress_periods"])
        print("dieback")
        if multiple_files:
            tile.add_dirpath("result_files", tile.data_directory / "Results")
            for date_bin_index, date_bin in enumerate(bins_as_date):
                state_code = first_date_number <= bins_as_datenumber[date_bin_index]
                if tile.parameters["soil_detection"]:
                    state_code = state_code + 2*(first_date_number_soil <= bins_as_datenumber[date_bin_index])
                period_end_results = get_state_at_date(state_code,relevant_area,dieback_data.state.attrs)
                if not(period_end_results.empty):
                    period_end_results.to_file(tile.paths["result_files"] / (date_bin.strftime('%Y-%m-%d')+".shp"))
                    
        else:
            tile.add_path("periodic_results_dieback", tile.data_directory / "Results" / "periodic_results_dieback.shp")
            periodic_results = get_periodic_results_as_shapefile(first_date_number, bins_as_date, bins_as_datenumber, relevant_area, dieback_data.state.attrs)
            if conf_threshold_list is not None and conf_classes_list is not None:
                stress_data = import_stress_data(tile.paths)
                stress_index = import_stress_index(tile.paths["stress_index"])
                confidence_area = relevant_area & dieback_data["state"] & ~soil_data["state"] if tile.parameters["soil_detection"] else relevant_area & dieback_data["state"]
           
                confidence_index = stress_index.sel(period = (stress_data["nb_periods"]+1).where(stress_data["nb_periods"]<=tile.parameters["max_nb_stress_periods"],tile.parameters["max_nb_stress_periods"])) #The selection probably makes no sense for pixels with nb_periods higher that max_nb_stress_periods, but it doesn't matter since they are excluded from result exports, but it removes bugs of inexistant period values.
                nb_dates = stress_data["nb_dates"].sel(period = (stress_data["nb_periods"]+1).where(stress_data["nb_periods"]<=tile.parameters["max_nb_stress_periods"],tile.parameters["max_nb_stress_periods"]))  #The selection probably makes no sense for pixels with nb_periods higher that max_nb_stress_periods, but it doesn't matter since they are excluded from result exports, but it removes bugs of inexistant period values.
               
                write_tif(confidence_index.where(confidence_area,0), forest_mask.attrs,nodata = 0, path = tile.paths["confidence_index"])
               
                confidence_class = vectorizing_confidence_class(confidence_index, nb_dates, confidence_area.compute(), conf_threshold_list, np.array(conf_classes_list), tile.raster_meta["attrs"])
                periodic_results = union_confidence_class(periodic_results, confidence_class)
            if not(periodic_results.empty):
                periodic_results.to_file(tile.paths["periodic_results_dieback"],index = None)
            del periodic_results
            
            if tile.parameters["soil_detection"]:
                tile.add_path("periodic_results_soil", tile.data_directory / "Results" / "periodic_results_soil.shp")
                periodic_results = get_periodic_results_as_shapefile(first_date_number_soil, bins_as_date, bins_as_datenumber, relevant_area, soil_data.state.attrs)
                if not(periodic_results.empty):
                    periodic_results.to_file(tile.paths["periodic_results_soil"])
                del periodic_results
        tile.last_date_export = tile.dates[-1]
        tile.save_info()
    else:
        print("Results already exported")

if __name__ == '__main__':
    cli_export_results()
    