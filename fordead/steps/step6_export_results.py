# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:32:57 2020

@author: Raphaël Dutrieux
"""

import click
from fordead.import_data import import_dieback_data, TileInfo, import_forest_mask, import_soil_data
from fordead.writing_data import get_bins, convert_dateindex_to_datenumber, get_periodic_results_as_shapefile, get_state_at_date, union_confidence_class

@click.command(name='export_results')
@click.option("-d", "--data_directory",  type=str, help="Path of the output directory", show_default=True)
@click.option("--start_date",  type=str, default='2015-06-23',
                    help="Start date for exporting results", show_default=True)
@click.option("--end_date",  type=str, default="2022-01-02",
                    help="End date for exporting results", show_default=True)
@click.option("--frequency",  type=str, default='M',
                    help="Frequency used to aggregate results, if value is 'sentinel', then periods correspond to the period between sentinel dates used in the detection, or it can be the frequency as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)", show_default=True)
@click.option("--multiple_files",  is_flag=True,
                    help="If True, one shapefile is exported for each period containing the areas in dieback at the end of the period. Else, a single shapefile is exported containing diebackd areas associated with the period of dieback", show_default=True)
@click.option("--intersection_confidence_class",  is_flag=True, help = "If True, detected results are intersected with the confidence class, only if multiple_files is False", show_default=True)
def cli_export_results(
    data_directory,
    start_date = '2015-06-23',
    end_date = "2022-01-02",
    frequency = 'M',
    multiple_files = False,
    intersection_confidence_class = False
    ):
    """
    Export results to files
    \f

    Parameters
    ----------
    data_directory
    start_date
    end_date
    frequency
    multiple_files
    intersection_confidence_class

    Returns
    -------

    """
    export_results(data_directory, start_date, end_date, frequency, multiple_files,intersection_confidence_class)



def export_results(
    data_directory,
    start_date = '2015-06-23',
    end_date = "2022-01-02",
    frequency = 'M',
    multiple_files = False,
    intersection_confidence_class = False
    ):
    """
    Writes results in the chosen period, form and using chosen frequency.
    See details here : https://fordead.gitlab.io/fordead_package/docs/user_guides/english/06_export_results/
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
    intersection_confidence_class : bool
        If True, detected results are intersected with the confidence class, only if multiple_files is False
    Returns
    -------

    """
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    dieback_data = import_dieback_data(tile.paths, chunks= None)
    tile.add_parameters({"start_date" : start_date,"end_date" : end_date, "frequency" : frequency, "multiple_files" : multiple_files, "intersection_confidence_class": intersection_confidence_class})
    if tile.parameters["Overwrite"] : 
        tile.delete_dirs("periodic_results_dieback","result_files") #Deleting previous detection results if they exist
        tile.delete_attributes("last_date_export")
    
    exporting = (tile.dates[-1] != tile.last_date_export) if hasattr(tile, "last_date_export") else True
    if exporting:
        print("Exporting results")
        bins_as_date, bins_as_datenumber = get_bins(start_date,end_date,frequency,tile.dates)
        first_date_number = convert_dateindex_to_datenumber(dieback_data, tile.dates)
    
        if tile.parameters["soil_detection"]:
            soil_data = import_soil_data(tile.paths, chunks= 1280)
            first_date_number_soil = convert_dateindex_to_datenumber(soil_data, tile.dates)
            
        forest_mask = import_forest_mask(tile.paths["ForestMask"], chunks= 1280)
        valid_area = import_forest_mask(tile.paths["valid_area_mask"], chunks= 1280)
        relevant_area = forest_mask & valid_area
    
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
            if intersection_confidence_class:
                periodic_results = union_confidence_class(periodic_results, tile.paths["confidence_class"])
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
    