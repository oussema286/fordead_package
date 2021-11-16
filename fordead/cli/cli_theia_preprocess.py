# -*- coding: utf-8 -*-
"""
Created on Wed Jan 20 09:18:18 2021

@author: Raphael Dutrieux
"""

import click
from pathlib import Path
from fordead.theia_preprocess import unzip_theia, merge_same_date, delete_empty_zip, theia_download, missing_theia_acquisitions


@click.command(name='theia_preprocess')
@click.option("-i", "--zipped_directory", type = str, help = "Path of the directory with zipped theia data")
@click.option("-o", "--unzipped_directory", type = str, help = "Path of the output directory")
@click.option("-t", "--tiles", multiple=True, help = "Name of the tiles to be downloaded (format : T31UFQ)")
@click.option("--login_theia", type = str, help = "Login of your theia account")
@click.option("--password_theia", type = str, help = "Password of your theia account")
@click.option("--start_date", type = str, default = "2015-06-23",help = "start date, fmt('2015-12-22')", show_default=True)
@click.option("--end_date", type = str, default = "2023-06-23", help = "end date, fmt('2015-12-22')", show_default=True)
@click.option("-n", "--lim_perc_cloud", type = int,default = 50, help = "Maximum cloudiness in SENTINEL dates downloaded (%)", show_default=True)
@click.option("-b", "--bands", multiple=True, default=["B2","B3","B4", "B8A", "B11", "B12", "CLMR2"],help = "Extracted bands", show_default=True)
@click.option("--empty_zip",  is_flag=True, help = "If True, the zip files are emptied as a way to save space.", show_default=True)
def theia_preprocess(zipped_directory, unzipped_directory, tiles, login_theia, password_theia, start_date, end_date, lim_perc_cloud, bands, empty_zip):
    
    zipped_directory = Path(zipped_directory)
    unzipped_directory = Path(unzipped_directory)
    for tuile in tiles:
        print("\n Downloading THEIA data for tile " + tuile + "\n")
        (zipped_directory / tuile).mkdir(exist_ok=True)   
        (unzipped_directory / tuile).mkdir(exist_ok=True)   
        
        delete_empty_zip(zipped_directory / tuile, unzipped_directory / tuile) #Deletes empty zip files if the unzipped directory is missing
        
        while missing_theia_acquisitions(tuile,start_date, end_date, str(zipped_directory / tuile), lim_perc_cloud, login_theia, password_theia):
            try:
                theia_download(tuile, start_date, end_date, str(zipped_directory / tuile), lim_perc_cloud, login_theia, password_theia)
                
                tmp_files = (zipped_directory / tuile).glob("*.tmp")
                for file in tmp_files:
                    file.unlink()
            except Exception: 
                pass
        print("\nAll available Sentinel-2 acquisitions downloaded\n")
            
        unzip_theia(bands,zipped_directory / tuile, unzipped_directory / tuile, empty_zip)
        merge_same_date(bands,unzipped_directory / tuile)
