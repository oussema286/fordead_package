# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 11:32:57 2020

@author: Raphaël Dutrieux
"""

import click
from fordead.import_data import import_decline_data, TileInfo, import_forest_mask, import_soil_data
from fordead.writing_data import get_bins, convert_dateindex_to_datenumber, get_periodic_results_as_shapefile, get_state_at_date

@click.command(name='export_results')
@click.option("-d", "--data_directory",  type=str, help="Path of the output directory", show_default=True)
@click.option("--start_date",  type=str, default='2015-06-23',
                    help="Start date for exporting results", show_default=True)
@click.option("--end_date",  type=str, default="2022-01-02",
                    help="End date for exporting results", show_default=True)
@click.option("--frequency",  type=str, default='M',
                    help="Frequency used to aggregate results, if value is 'sentinel', then periods correspond to the period between sentinel dates used in the detection, or it can be the frequency as used in pandas.date_range. e.g. 'M' (monthly), '3M' (three months), '15D' (fifteen days)", show_default=True)
@click.option("--export_soil",  is_flag=True,
                    help="If True, results relating to soil detection are exported. Results of soil detection have to be computed and written in previous steps", show_default=True)
@click.option("--multiple_files",  is_flag=True,
                    help="If True, one shapefile is exported for each period containing the areas in decline at the end of the period. Else, a single shapefile is exported containing declined areas associated with the period of decline", show_default=True)
def cli_export_results(
    data_directory,
    start_date = '2015-06-23',
    end_date = "2022-01-02",
    frequency = 'M',
    export_soil = False,
    multiple_files = False
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
    export_soil
    multiple_files

    Returns
    -------

    """
    export_results(data_directory, start_date, end_date, frequency, export_soil, multiple_files)



def export_results(
    data_directory,
    start_date = '2015-06-23',
    end_date = "2022-01-02",
    frequency = 'M',
    export_soil = False,
    multiple_files = False
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
    export_soil : bool
        If True, results relating to soil detection are exported. Results of soil detection have to be computed and written in previous steps
    multiple_files : bool
        If True, one shapefile is exported for each period containing the areas in decline at the end of the period. Else, a single shapefile is exported containing declined areas associated with the period of decline

    Returns
    -------

    """
    print("Exporting results")
    
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    decline_data = import_decline_data(tile.paths, chunks= None)
    tile.add_parameters({"start_date" : start_date,"end_date" : end_date, "frequency" : frequency, "export_soil" : export_soil, "multiple_files" : multiple_files})
    if tile.parameters["Overwrite"] : tile.delete_dirs("periodic_results_decline","result_files") #Deleting previous detection results if they exist
    
    bins_as_date, bins_as_datenumber = get_bins(start_date,end_date,frequency,tile.dates)
    first_date_number = convert_dateindex_to_datenumber(decline_data, tile.dates)

    if export_soil:
        soil_data = import_soil_data(tile.paths, chunks= 1280)
        first_date_number_soil = convert_dateindex_to_datenumber(soil_data, tile.dates)
        
    forest_mask = import_forest_mask(tile.paths["ForestMask"], chunks= 1280)
    valid_area = import_forest_mask(tile.paths["valid_area_mask"], chunks= 1280)
    relevant_area = forest_mask & valid_area

    if multiple_files:
        tile.add_dirpath("result_files", tile.data_directory / "Results")
        for date_bin_index, date_bin in enumerate(bins_as_date):
            state_code = first_date_number <= bins_as_datenumber[date_bin_index]
            if export_soil:
                state_code = state_code + 2*(first_date_number_soil <= bins_as_datenumber[date_bin_index])
            period_end_results = get_state_at_date(state_code,relevant_area,decline_data.state.attrs)
            if not(period_end_results.empty):
                period_end_results.to_file(tile.paths["result_files"] / (date_bin.strftime('%Y-%m-%d')+".shp"))
                
    else:
        tile.add_path("periodic_results_decline", tile.data_directory / "Results" / "periodic_results_decline.shp")
        periodic_results = get_periodic_results_as_shapefile(first_date_number, bins_as_date, bins_as_datenumber, relevant_area, decline_data.state.attrs)
        periodic_results.to_file(tile.paths["periodic_results_decline"])
        del periodic_results
        
        if export_soil:
            tile.add_path("periodic_results_soil", tile.data_directory / "Results" / "periodic_results_soil.shp")
            periodic_results = get_periodic_results_as_shapefile(first_date_number_soil, bins_as_date, bins_as_datenumber, relevant_area, soil_data.state.attrs)
            periodic_results.to_file(tile.paths["periodic_results_soil"])
            del periodic_results
    
    tile.save_info()

if __name__ == '__main__':
    cli_export_results()
    