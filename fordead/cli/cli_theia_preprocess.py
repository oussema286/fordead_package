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
@click.option('--level', type = click.Choice(['LEVEL1C', 'LEVEL2A', 'LEVEL3A'], case_sensitive=False),  help='Product level for reflectance products', default='LEVEL2A', show_default=True)
@click.option("--start_date", type = str, default = "2015-06-23",help = "start date, fmt('2015-12-22')", show_default=True)
@click.option("--end_date", type = str, default = "2023-06-23", help = "end date, fmt('2015-12-22')", show_default=True)
@click.option("-n", "--lim_perc_cloud", type = int,default = 50, help = "Maximum cloudiness in SENTINEL dates downloaded (%)", show_default=True)
@click.option("-b", "--bands", multiple=True, default=["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12", "CLMR2"],help = "List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, as well as CLMR2, CLMR2, EDGR1, EDGR2, SATR1, SATR2 for LEVEL2A data, and DTS1, DTS2, FLG1, FLG2, WGT1, WGT2 for LEVEL3A)", show_default=True)
@click.option('--correction_type', type = click.Choice(['SRE', 'FRE', 'FRC'], case_sensitive=False),  help='Chosen correction type (SRE or FRE for LEVEL2A data, FRC for LEVEL3A)', default='FRE', show_default=True)
@click.option("--empty_zip",  is_flag=True, help = "If True, the zip files are emptied as a way to save space.", show_default=True)
def cli_theia_preprocess(zipped_directory, unzipped_directory, tiles, login_theia, password_theia, level, start_date = "2015-06-23", end_date = "2023-06-23", lim_perc_cloud = 50, bands = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12", "CLMR2"], correction_type = "FRE", empty_zip = False):
    """
    Automatically downloads all Sentinel-2 data from THEIA between two dates under a cloudiness threshold. Then this data is unzipped, keeping only chosen bands from Flat REflectance data, and zip files can be emptied as a way to save storage space.
    Finally, if two Sentinel-2 directories come from the same acquisition date, they are merged by replacing no data pixels from one directory with pixels with data in the other, before removing the latter directory.

    \f
    Parameters
    ----------
    zipped_directory
    unzipped_directory
    tiles
    login_theia
    password_theia
    level
    start_date
    end_date
    lim_perc_cloud
    bands
    correction_type
    empty_zip

    """
    
    theia_preprocess(zipped_directory, unzipped_directory, tiles, login_theia, password_theia, level, start_date, end_date, lim_perc_cloud, bands, correction_type, empty_zip)

def theia_preprocess(zipped_directory, unzipped_directory, tiles, login_theia, password_theia, level = "LEVEL2A", start_date = "2015-06-23", end_date = "2023-06-23", lim_perc_cloud = 50, bands = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12", "CLMR2"], correction_type = "FRE", empty_zip = False):
    """
    Automatically downloads all Sentinel-2 data from THEIA between two dates under a cloudiness threshold. Then this data is unzipped, keeping only chosen bands from Flat REflectance data, and zip files can be emptied as a way to save storage space.
    Finally, if two Sentinel-2 directories come from the same acquisition date, they are merged by replacing no data pixels from one directory with pixels with data in the other, before removing the latter directory.

    Parameters
    ----------
    zipped_directory : str
        Path of the directory with zipped theia data.
    unzipped_directory : str
        Path of the output directory.
    tiles : list of str
        Name of the tiles to be downloaded (format : T31UFQ)
    login_theia : str
        Login of your theia account.
    password_theia : str
        Password of your theia account.
    level : str
        Product level for reflectance products, can be 'LEVEL1C', 'LEVEL2A' or 'LEVEL3A'
    start_date : str, optional
        start date, fmt('2015-12-22'). The default is "2015-06-23".
    end_date : str, optional
        end date, fmt('2015-12-22'). The default is "2023-06-23".
    lim_perc_cloud : int, optional
        Maximum cloudiness in SENTINEL dates downloaded (%). The default is 50.
    bands : list of str
        List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, as well as CLMR2, CLMR2, EDGR1, EDGR2, SATR1, SATR2 for LEVEL2A data, and DTS1, DTS2, FLG1, FLG2, WGT1, WGT2 for LEVEL3A). The default is ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12", "CLMR2"].
    correction_type : str
        Chosen correction type (SRE or FRE for LEVEL2A data, FRC for LEVEL3A)
    empty_zip : bool, optional
        If True, the zip files are emptied as a way to save space. The default is False.

    """
    
    if level == "LEVEL3A" : correction_type = "FRC"
    
    zipped_directory = Path(zipped_directory)
    unzipped_directory = Path(unzipped_directory)
    for tuile in tiles:
        print("\n Downloading THEIA data for tile " + tuile + "\n")
        (zipped_directory / tuile).mkdir(exist_ok=True)   
        (unzipped_directory / tuile).mkdir(exist_ok=True)
        
        delete_empty_zip(zipped_directory / tuile, unzipped_directory / tuile) #Deletes empty zip files if the unzipped directory is missing
        
        while missing_theia_acquisitions(tuile,start_date, end_date, str(zipped_directory / tuile), lim_perc_cloud, login_theia, password_theia, level):
            try:
                theia_download(tuile, start_date, end_date, str(zipped_directory / tuile), lim_perc_cloud, login_theia, password_theia, level)
                
                tmp_files = (zipped_directory / tuile).glob("*.tmp")
                for file in tmp_files:
                    file.unlink()
            except Exception: 
                pass
        print("\nAll available Sentinel-2 acquisitions downloaded\n")
            
        unzip_theia(bands,zipped_directory / tuile, unzipped_directory / tuile, empty_zip, correction_type)
        merge_same_date(bands,unzipped_directory / tuile)

if __name__ == '__main__':
    # start_time_debut = time.time()
    cli_theia_preprocess()
    # print("Calcul des masques et du CRSWIR : %s secondes ---" % (time.time() - start_time_debut))

