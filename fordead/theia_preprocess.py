# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 13:53:50 2021

@author: Raphael Dutrieux
@author: Florian de Boissieu
"""
from path import Path
from zipfile import ZipFile, BadZipfile
import zipfile
import tempfile
import numpy as np
import rasterio
import time
import re
import sys
from datetime import datetime, timedelta
from eodag import EODataAccessGateway


from fordead.import_data import retrieve_date_from_string, TileInfo


def theia_download(tile, start_date, end_date, write_dir, lim_perc_cloud,
                   login_theia=None, password_theia=None, level='LEVEL2A',
                   unzip_dir = None, retry=10, wait=300, search_timeout=10):
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
    retry : int, optional
        Number of retries if download fails
    wait : int, optional
        Wait time between retries in seconds
    search_timeout : int, optional
        Timeout in seconds for search of theia products. Default is 10.
        It updates the htttp request timeout for the search.

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

    done = False
    trials = 0
    while not done:
        dag = EODataAccessGateway()
        # dag._prune_providers_list()

        if login_theia is not None and password_theia is not None:
            dag.providers_config["theia"].auth.credentials.update(
                {
                    "ident": login_theia,
                    "pass": password_theia
                }
            )
        if search_timeout is not None:
            dag.providers_config["theia"].search.timeout = search_timeout

        # search products
        search_args = dict(
            productType=product_type,
            start=start_date,
            end=end_date,
            location=re.sub(r'^([0-9].*)', r'T\1', tile),
            cloudCover=lim_perc_cloud,
            provider="theia"
        )

        try:
            search_results = dag.search_all(**search_args)
        except Exception as e:
            print("search failed : ", e)
            if trials==retry:
                raise RuntimeError("\nRetry limit reached.\n")
            else:
                trials+=1
                print(f"\nRetries in {wait} seconds {trials}/{retry} ...\n")
                time.sleep(wait)
                continue

        # Several failure can happen: remote onnection closed, authentication error, empty download.
        # We will loop until we get all products or until we reach the number of retries.

        # distribute search results among the different categories
        unzipped = []
        merged = []
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
                try:
                    zip_len = len(ZipFile(zip_file).namelist())
                    if zip_len==0:
                        merged.append(zip_file)
                    else:
                        # products downloaded but not unzipped
                        to_unzip.append(zip_file)
                except BadZipfile:
                    print(f"Bad zip file, removing file: {f}")
                    Path(zip_file).remove()
                    to_download.append(r)    
            else:
                to_download.append(r)
        
        
        if len(unzipped):
            unzipped_str = '\n'.join(unzipped)
            print(f"Products already unzipped:\n{unzipped_str}\n")
        if len(merged):
            merged_str = '\n'.join(merged)
            print(f"Products considered as merged:\n{merged_str}\n")
        if to_unzip:
            to_unzip_str = '\n'.join(to_unzip)
            print(f"Products already downloaded but not unzipped:\n{to_unzip_str}\n")
        print(f'{len(search_results)-len(to_download)} files already downloaded or unzipped, {len(to_download)} files left to download.')
        if len(to_download):
            print(f"Downloading products: {to_download}")

        # start downloading
        downloaded = []
        if len(to_download) == 0:
            done = True
        else:
            try:
                downloaded = dag.download_all(to_download,
                            outputs_prefix=write_dir,
                            extract=False)
            except Exception as e:
                    print(f"Download failed with error: {e}")

            # check all downloaded files exists and correct zip
            for f in downloaded:
                try:
                    ZipFile(f).namelist()
                except BadZipfile:
                    print(f"Bad zip file, removing file: {f}")
                    Path(f).remove()
                    downloaded.remove(f)
            
            # check all files were downloaded
            if len(to_download) == len(downloaded):
                done=True
                print(f"\nDownload done after {trials} retries!\n")
            elif trials==retry:
                raise RuntimeError("\nRetry limit reached.\n")
            else:
                trials+=1
                print(f"\nRetries in {wait} seconds {trials}/{retry} ...\n")
                time.sleep(wait)
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
            if date not in tile.paths["unzipped"]: # this excludes duplicates of the same date but different scene ID, it is wanted...
                try:
                    if (len(ZipFile(tile.paths["zipped"][date]).namelist()) == 0):
                        print("Zip file is empty and unzipped directory not found : zip file removed " + str(tile.paths["zipped"][date]))
                        Path(tile.paths["zipped"][date]).remove()
                except BadZipfile:
                    print("Bad zip file, removing file: {}".format(tile.paths["zipped"][date]))
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
            Doublons = [Path(f) for f in Doublons]
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
                    doublon.rmtree() #Supprime les inutiles
                    print("Suppression doublons")
