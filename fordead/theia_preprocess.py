# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:53:50 2021

@author: Raphael Dutrieux
"""
from path import Path
from zipfile import ZipFile, BadZipfile
import zipfile
import tempfile
import numpy as np
import rasterio
import shutil
import glob
import json
import time
import os
import os.path
import re
import sys
from datetime import datetime, timedelta
from eodag import EODataAccessGateway


from fordead.import_data import retrieve_date_from_string, TileInfo


# from datetime import date, datetime
if sys.version_info[0] == 2:
    from urllib import urlencode
elif sys.version_info[0] > 2:
    from urllib.parse import urlencode
    

        
def missing_theia_acquisitions(tile, start_date, end_date, write_dir, lim_perc_cloud, login_theia, password_theia, level, logpath = None):
    """
    Checks if there are undownloaded Sentinel-2 acquisitions available

    Parameters
    ----------
    tile : str
        Name of the Sentinel-2 tile (format : "T31UFQ").
    start_date : str
        Acquisitions before this date are ignored (format : "YYYY-MM-DD") 
    end_date : str
        Acquisitions after this date are ignored (format : "YYYY-MM-DD") 
    write_dir : str
        Directory where THEIA data is downloaded
    lim_perc_cloud : int
        Maximum cloud cover (%)
    login_theia : str
        Login of your theia account
    password_theia : str
        Password of your theia account
    level : str
        Product level for reflectance products, can be 'LEVEL1C', 'LEVEL2A' or 'LEVEL3A'

    Returns
    -------
    bool
        True if there are undownloaded acquisitions available, False if not

    """
    

    dict_query = {'location': tile,
                  "startDate" : start_date,
                  'completionDate': end_date, 
                  'maxRecords': 500, 
                  'processingLevel': level}
    
    config = {'serveur': 'https://theia.cnes.fr/atdistrib', 
              'resto': 'resto2', 
              'token_type': 'text', 
              'login_theia': login_theia, 
              'password_theia': password_theia}

    print("Get theia single sign on token")
    get_token = 'curl -k -s -X POST %s --data-urlencode "ident=%s" --data-urlencode "pass=%s" %s/services/authenticate/>token.json' % (
        "", config["login_theia"], config["password_theia"], config["serveur"])
    
    # print get_token
    
    os.system(get_token)

    query = "%s/%s/api/collections/%s/search.json?" % (
        config["serveur"], config["resto"], "SENTINEL2")+urlencode(dict_query)
    print(query)
    search_catalog = 'curl -k %s -o search.json "%s"' % ("", query)
    print(search_catalog)
    os.system(search_catalog)
    time.sleep(5)
    
    with open('search.json') as data_file:
        data = json.load(data_file)
    
    try:
        if logpath is not None:
            file = open(logpath, "w") 

        for i in range(len(data["features"])):
            prod = data["features"][i]["properties"]["productIdentifier"]
            cloudtemp = data["features"][i]["properties"]["cloudCover"]
            
            acqDate = data["features"][i]["properties"]["startDate"]
            prodDate = data["features"][i]["properties"]["productionDate"]
            pubDate = data["features"][i]["properties"]["published"]
            
            if cloudtemp != None:
                cloudCover = int(cloudtemp)
            else:
                cloudCover = 0
                
            if logpath is not None:
                file.write("acq date" + acqDate[0:14] + "prod date" + prodDate[0:14] + "pub date" + pubDate[0:14] + "cloudCover " +  str(cloudtemp) + "\n")
                # file.write("test")
                
            file_exists = os.path.exists("%s/%s.zip" % (write_dir, prod))
            if not(file_exists) and (cloudCover <= lim_perc_cloud):
                # download only if cloudCover below maxcloud
                return True
        if logpath is not None:
            file.close()
    except KeyError:
        print("No undownloaded product corresponds to selection criteria")
    return False
        
        
# def theia_download(tile, start_date, end_date, write_dir, lim_perc_cloud, login_theia, password_theia, level):
#     """
#     Downloads Sentinel-2 acquisitions of the specified tile from THEIA from start_date to end_date under a cloudiness threshold

#     Parameters
#     ----------
#     tile : str
#         Name of the Sentinel-2 tile (format : "T31UFQ").
#     start_date : str
#         Acquisitions before this date are ignored (format : "YYYY-MM-DD") 
#     end_date : str
#         Acquisitions after this date are ignored (format : "YYYY-MM-DD") 
#     write_dir : str
#         Directory where THEIA data is downloaded
#     lim_perc_cloud : int
#         Maximum cloud cover (%)
#     login_theia : str
#         Login of your theia account
#     password_theia : str
#         Password of your theia account
#     level : str
#         Product level for reflectance products, can be 'LEVEL1C', 'LEVEL2A' or 'LEVEL3A'

#     """

#     dict_query = {'location': tile,
#                   "startDate" : start_date,
#                   'completionDate': end_date, 
#                   'maxRecords': 500, 
#                   'processingLevel': level}
    
#     config = {'serveur': 'https://theia.cnes.fr/atdistrib', 
#               'resto': 'resto2', 
#               'token_type': 'text', 
#               'login_theia': login_theia, 
#               'password_theia': password_theia}

#     print("Get theia single sign on token")
#     get_token = 'curl -k -s -X POST %s --data-urlencode "ident=%s" --data-urlencode "pass=%s" %s/services/authenticate/>token.json' % (
#         "", config["login_theia"], config["password_theia"], config["serveur"])
        
#     os.system(get_token)
#     print("Done")
#     with open('token.json') as data_file:
#         token = data_file.readline()
    
#     query = "%s/%s/api/collections/%s/search.json?" % (
#         config["serveur"], config["resto"], "SENTINEL2")+urlencode(dict_query)
#     print(query)
#     search_catalog = 'curl -k %s -o search.json "%s"' % ("", query)
#     print(search_catalog)
#     os.system(search_catalog)
#     time.sleep(5)
    
#     # ====================
#     # Download
#     # ====================
    
#     with open('search.json') as data_file:
#         data = json.load(data_file)
    
#     try:
#         for i in range(len(data["features"])):
#             prod = data["features"][i]["properties"]["productIdentifier"]
#             feature_id = data["features"][i]["id"]
#             cloudtemp = data["features"][i]["properties"]["cloudCover"]
#             if cloudtemp != None:
#                 cloudCover = int(cloudtemp)
#             else:
#                 cloudCover = 0
#             acqDate = data["features"][i]["properties"]["startDate"]
#             prodDate = data["features"][i]["properties"]["productionDate"]
#             pubDate = data["features"][i]["properties"]["published"]
#             print ('------------------------------------------------------')
#             print(prod, feature_id)
#             print("cloudCover:", cloudCover)
#             print("acq date", acqDate[0:14], "prod date", prodDate[0:14], "pub date", pubDate[0:14])
    
#             if write_dir == None:
#                 write_dir = os.getcwd()
#             file_exists = os.path.exists("%s/%s.zip" % (write_dir, prod))
#             rac_file = '_'.join(prod.split('_')[0: -1])
#             print((">>>>>>>", rac_file))
#             fic_unzip = glob.glob("%s/%s*" % (write_dir, rac_file))
#             if len(fic_unzip) > 0:
#                 unzip_exists = True
#             else:
#                 unzip_exists = False
#             tmpfile = "%s/%s.tmp" % (write_dir, prod)
#             get_product = 'curl %s -o "%s" -k -H "Authorization: Bearer %s" %s/%s/collections/%s/%s/download/?issuerId=theia' % (
#                 "", tmpfile, token, config["serveur"], config["resto"], "SENTINEL2", feature_id)
#             print(get_product)
#             if not(file_exists) and not(unzip_exists):
#                 # download only if cloudCover below maxcloud
#                 if cloudCover <= lim_perc_cloud:
#                     os.system(get_product)
    
#                     # check if binary product
    
#                     with open(tmpfile) as f_tmp:
#                         try:
#                             tmp_data = json.load(f_tmp)
#                             print("Result is a text file")
#                             print(tmp_data)
#                         except ValueError:
#                             pass
    
#                     os.rename("%s" % tmpfile, "%s/%s.zip" % (write_dir, prod))
#                     print("product saved as : %s/%s.zip" % (write_dir, prod))
#                 else:
#                     print("cloud cover too high : %s" % (cloudCover))
#             elif file_exists:
#                 print("%s already exists" % prod)
    
#     except KeyError:
#         print(">>>no product corresponds to selection criteria")

def theia_download(tile, start_date, end_date, write_dir, lim_perc_cloud,
                   login_theia=None, password_theia=None, level='LEVEL2A', unzip_dir = None):
    """
    Downloads Sentinel-2 acquisitions of the specified tile from THEIA from start_date to end_date under a cloudiness threshold

    Parameters
    ----------
    tile : str
        Name of the Sentinel-2 tile (format : "T31UFQ").
    start_date : str
        Acquisitions before this date are ignored (format : "YYYY-MM-DD") 
    end_date : str
        Acquisitions after this date are ignored (format : "YYYY-MM-DD") 
    write_dir : str
        Directory where THEIA data is downloaded
    lim_perc_cloud : int
        Maximum cloud cover (%)
    login_theia : str
        Login of your theia account
    password_theia : str, optional (see notes)
        Password of your theia account
    level : str, optional (see notes)
        Product level for reflectance products, can be 'LEVEL1C', 'LEVEL2A' or 'LEVEL3A'
    
    Returns
    -------
    List
        Files to unzip

    Notes
    -------
    It is not recommended to write login and password
    in a script, thus it is recommended to set 
    theia credentials in $HOME/.config/eodag/eodag.yaml
    in the subsection credentials of section theia.

    In case $HOME/.config/eodag/eodag.yaml, run the following
    in a python session, it should create the file:
    ```python
    from path import Path
    from eodag import EODataAccessGateway
    EODataAccessGateway()
    print(Path("~").expand() / ".config" / "eodag" / "eodag.yml"))
    ```

    In the case there are special characters in your
    login or password, make sure to add double quotes,
    example:
    ```yaml
    theia:
        priority: # Lower value means lower priority (Default: 0)
        search:   # Search parameters configuration
        download:
            extract:
            outputs_prefix:
            dl_url_params:
        auth:
            credentials:
                ident: "myemail@inrae.fr"
                pass: "k5dFE9§~lkjqs"
    ```
    """

    if level == 'LEVEL1C':
        product_type = 'S2_MSI_L1C'
    elif level == 'LEVEL2A':
        product_type = 'S2_MSI_L2A_MAJA'
    elif level == 'LEVEL3A':
        product_type = 'S2_MSI_L3A_WASP'

    dag = EODataAccessGateway()
    dag._prune_providers_list()

    search_args = dict(
        productType=product_type,
        start=start_date,
        end=end_date,
        location=re.sub(r'^([0-9].*)', r'T\1', tile),
        cloudCover=lim_perc_cloud,
        provider="theia"
    )

    search_results = dag.search_all(**search_args)

    if login_theia is not None and password_theia is not None:
        dag.providers_config["theia"].auth.credentials.update(
            {
                "ident": login_theia,
                "pass": password_theia
            }
        )

    unzipped = []
    to_unzip = []
    to_download = [] 
    for r in search_results:
        zip_file = Path(write_dir) / (r.properties['id']+".zip")
        unzip_file = []
        if unzip_dir is not None:
            id = re.sub(r'(.*)_[A-Z]', r'\1',r.properties['id'])
            unzip_file = Path(unzip_dir).glob(f'{id}_[A-D]_V*')
        if len(unzip_file)>0:
            unzipped.append(unzip_file[0])
        elif zip_file.exists():
            # products downloaded but not unzipped
            to_unzip.append(zip_file)
        else:
            to_download.append(r)
    
    print(f"Products already unzipped:\n{'\n'.join(unzipped)}\n")
    print(f"Products already downloaded but not unzipped:\n{'\n'.join(to_unzip)}\n")
    print(f'{len(search_results)-len(to_download)} files already downloaded or unzipped, {len(to_download)} files left to download.')
    print(f"Downloading products: {to_download}")

    downloaded = []
    if len(to_download) > 0:
        downloaded = dag.download_all(to_download,
                     outputs_prefix=write_dir,
                     extract=False)
        for f in downloaded:
            if not (Path(f).exists() and f.endswith(".zip")):
                raise Exception("Something went wrong with the download")

    return to_unzip + downloaded

BAND_NAMES = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12',
              'CLMR1', 'CLMR2', 'EDGR1', 'EDGR2', 'SATR1', 'SATR2',
              "DTS1","DTS2","FLG1","FLG2","WGT1","WGT2"]

BAND_FILE_PATTERNS = dict(zip(BAND_NAMES,
    ['B2.tif', 'B3.tif', 'B4.tif', 'B5.tif', 'B6.tif', 'B7.tif',
     'B8.tif', 'B8A.tif', 'B11.tif', 'B12.tif', '_CLM_R1.tif', 
     '_CLM_R2.tif', '_EDG_R1.tif', '_EDG_R2.tif', '_SAT_R1.tif',
     '_SAT_R2.tif',"_DTS_R1.tif","_DTS_R2.tif","_FLG_R1.tif",
     "_FLG_R2.tif","_WGT_R1.tif","_WGT_R2.tif"]))

def theia_bands(correction_type):
    """
    Returns dict of expected theia bands for the specified correction type

    Parameters
    ----------
    correction_type : str
        Chosen correction type (SRE or FRE for LEVEL2A data, FRC for LEVEL3A)

    Returns
    -------
    dict
        Theia band patterns for the specified correction type
    """
    bands = {k:re.sub(r'^(B[0-9]+[A]*.tif)$', "_"+correction_type+'_\\1', v) for k, v in BAND_FILE_PATTERNS.items()}
    return bands


def s2_unzip(s2zipfile, out_dir, bands, correction_type):
    """
    Unzips Flat REflectance data from zipped theia data, then empties the zip file

    Parameters
    ----------
    s2zipfile : str
        Path of the zip file containing a Sentinel-2 acquisition downloaded from theia.
    out_dir : str
        Directory where data is extracted
    bands : list of str
        List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, as well as CLMR2, CLMR2, EDGR1, EDGR2, SATR1, SATR2 for LEVEL2A data, and DTS1, DTS2, FLG1, FLG2, WGT1, WGT2 for LEVEL3A)
    correction_type : str
        Chosen correction type (SRE or FRE for LEVEL2A data, FRC for LEVEL3A)

    Returns
    -------
    None.

    """
    s2zipfile = Path(s2zipfile).expand()
    out_dir = Path(out_dir).expand()
    corrBand = theia_bands(correction_type)
  
    
    try:
        with ZipFile(s2zipfile, 'r') as zipObj:
            root_dir, = zipfile.Path(zipObj).iterdir()
            if (out_dir / root_dir.name).exists():
                print(f'Files already extracted: {out_dir / root_dir.name}')
            else:
                print(f'Extracting files from {s2zipfile} to {out_dir / root_dir.name}')
                with tempfile.TemporaryDirectory(dir=out_dir) as tempdir:
                    tmpdir = Path(tempdir)
                    listOfFileNames = zipObj.namelist()
                    for fileName in listOfFileNames:
                            for i in bands:
                                if fileName.endswith(corrBand[i]): #Si le nom de fichier finit par ce qui correspond à la bande
                                    zipObj.extract(fileName, tmpdir)
                    (tmpdir / root_dir.name).move(out_dir)
            
    except BadZipfile:
        print(f"Bad zip file, removing file: {s2zipfile}")
        s2zipfile.remove()

def unzip_theia(bands, zip_dir, out_dir, empty_zip, correction_type):
    """
    Unzips zipped theia data, then empties the zip file

    Parameters
    ----------
    bands : list of str
        List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, as well as CLMR2, CLMR2, EDGR1, EDGR2, SATR1, SATR2 for LEVEL2A data, and DTS1, DTS2, FLG1, FLG2, WGT1, WGT2 for LEVEL3A)
    zip_dir : str or list
        Directory where zip files containing theia data are stored
        or list of zip files
    out_dir : str
        Directory where data is extracted
    empty_zip : bool
        If True, the zip file is emptied as a way to save space
    correction_type : str
        Chosen correction type (SRE or FRE for LEVEL2A data, FRC for LEVEL3A)


    Returns
    -------
    None.
    

    """
    
    out_dir = Path(out_dir).expand()
    if isinstance(zip_dir, list):
        zipList = [Path(f).expand() for f in zip_dir]
    else:
        zip_dir = Path(zip_dir).expand()
        zipList=zip_dir.glob("*.zip")
    
    out_dir.mkdir_p()
    
    for zipfile in zipList:
        s2_unzip(zipfile, out_dir, bands, correction_type)
        if zipfile.exists() and (len(ZipFile(zipfile).namelist()) != 0) and empty_zip:
            print("Replaces by empty zip: " + zipfile)
            zipfile.remove()
            zipObj = ZipFile(zipfile, 'w')
            zipObj.close()

def delete_empty_zip(zipped_dir, unzipped_dir):
    """
    Deletes empty zip files if the unzipped directory is missing

    Parameters
    ----------
    zipped_dir : str
        Directory where zip files containing theia data are stored.
    unzipped_dir : str
        Directory where unzipped data containing theia data are stored

    Returns
    -------
    None.

    """

    tile = TileInfo(unzipped_dir)
    for i in range(2):
        tile.getdict_datepaths("zipped",zipped_dir)
        tile.getdict_datepaths("unzipped",unzipped_dir)
        for date in tile.paths["zipped"]:
            if date not in tile.paths["unzipped"]:
                try:
                    if (len(ZipFile(tile.paths["zipped"][date]).namelist()) == 0):
                        print("Zip file is empty and unzipped directory not found : zip file removed " + str(tile.paths["zipped"][date]))
                        Path(tile.paths["zipped"][date]).remove()
                except BadZipfile:
                    print(f"Bad zip file, removing file: {tile.paths["zipped"][date]}")
                    Path(tile.paths["zipped"][date]).remove()

def merge_same_date(bands,out_dir):
    """
    Merges data from two theia directories if they share the same date of acquisition

    Parameters
    ----------
    bands : list of str
        List of bands to extracted (B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12, CLMR2).
    out_dir : str
        Directory where unzipped data containing theia data are stored.

    Returns
    -------
    None.

    """

    out_dir = Path(out_dir).expand()
    SenPathGen = out_dir.glob("SEN*")
    # SenPathList=glob(out_dir+"/SEN*")
    SenDateList = [] #Création dictionnaire avec date : chemin du fichier
    SenPathList = []
    for SenPath in SenPathGen:
        # SenDate = SenPath.split('_')[1].split('-')[0]
        SenDate = retrieve_date_from_string(SenPath)
        SenDateList+=[SenDate]
        SenPathList += [SenPath]
    # tile = TileInfo(out_dir)
    # tile.getdict_datepaths("SENTINEL",tile.data_directory)

    
    for date in np.unique(np.array(SenDateList)):
        if np.sum(np.array(SenDateList)==date)>1:
            print("Doublon détecté à la date : " + date)
            Doublons=np.array(SenPathList)[np.array(SenDateList)==date]
            
            #MOSAIQUE BANDES
            
            for band in bands:
                if band != "CLMR2":
                    print("Fusion bande : " + band)
                    for doublon in Doublons:
                        # PathBande=doublon+"/"+os.path.basename(doublon)+"_FRE_"+band+".tif"
                        PathBande=doublon / (doublon.name +"_FRE_"+band+".tif")
                        with rasterio.open(PathBande) as RasterBand:
                            if doublon==Doublons[0]:
                                MergedBand=RasterBand.read(1)
                                ProfileSave=RasterBand.profile
                            else:
                                AddedBand=RasterBand.read(1)
                                MergedBand[AddedBand!=-10000]=AddedBand[AddedBand!=-10000]
                    
                    for doublon in Doublons:
                        if doublon==Doublons[0]:
                            # with rasterio.open(doublon+"/"+os.path.basename(doublon)+"_FRE_"+band+".tif", 'w', **ProfileSave) as dst:
                            with rasterio.open(doublon /(doublon.name +"_FRE_"+band+".tif"), 'w', **ProfileSave) as dst:
                                    dst.write(MergedBand,indexes=1)
            
            print("Fusion masque")
            #MOSAIQUE MASQUE THEIA
            for doublon in Doublons:
                    PathBande=doublon /  "MASKS" / (doublon.name +"_CLM_R2.tif")
                    with rasterio.open(PathBande) as RasterBand:
                        if doublon==Doublons[0]:
                            MergedBand=RasterBand.read(1)
                            ProfileSave=RasterBand.profile
                        else:
                            AddedBand=RasterBand.read(1)
                            MergedBand[AddedBand!=0]=AddedBand[AddedBand!=0]
                
            for doublon in Doublons:
                if doublon==Doublons[0]:
                    with rasterio.open(doublon /  "MASKS" / (doublon.name +"_CLM_R2.tif"), 'w', **ProfileSave) as dst:
                            dst.write(MergedBand,indexes=1)
                else:
                    shutil.rmtree(str(doublon)) #Supprime les inutiles
                    print("Suppression doublons")
                

def decompose_interval(start_date, end_date):
    # Convert input strings to datetime objects
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Initialize the list to store decomposed intervals
    intervals = []

    # Check if the interval is longer than a year
    while start_date < end_date:
        next_year = start_date + timedelta(days=365)
        
        # Adjust for leap year
        if next_year.year % 4 == 0 and (next_year.year % 100 != 0 or next_year.year % 400 == 0):
            next_year += timedelta(days=1)

        # Determine the end date for the current interval
        interval_end = min(next_year, end_date)

        # Append the current interval to the list
        intervals.append((start_date, interval_end))

        # Move the start date to the beginning of the next interval
        start_date = interval_end

    return intervals