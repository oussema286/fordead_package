from path import Path
from fordead.theia_preprocess import maja_download, maja_search, patch_merged_scenes, categorize_search
import pandas as pd
import re

def test_maja_search():

    # SENTINEL2A_20200325-103818-163_L2A_T31TGL (4-0)
    # SENTINEL2A_20200325-103818-163_L2A_T31TGL (2-2)
    tile = "T31TGL"
    start_date = "2020-03-25"
    end_date = "2020-03-26"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 1
    assert df.version[0] == "4-0"

    # SENTINEL2A_20200407-104815-292_L2A_T31TGL (4-0)
    # SENTINEL2A_20200407-104815-295_L2A_T31TGL (2-2)
    start_date = "2020-04-07"
    end_date = "2020-04-08"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 1
    assert df.version[0] == "4-0"

    # SENTINEL2B_20200409-103818-465_L2A_T31TGL (4-0)
    # SENTINEL2B_20200409-103818-464_L2A_T31TGL (2-2)
    start_date = "2020-04-09"
    end_date = "2020-04-10"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 1
    assert df.version[0] == "4-0"

    tile = "T31TGM"
    start_date = "2024-09-26"
    end_date = "2024-10-30"
    df = maja_search(tile, start_date, end_date)
    assert all(df.version == "4-0")

    # two granules (diff. id, diff. date, diff. version)
    start_date = "2024-09-20"
    end_date = "2024-09-26"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 2
    assert df.date.unique().shape[0] == 2

    # two splits of scene
    # SENTINEL2B_20240829-104755-706_L2A_T31TGM (3-1)
    # SENTINEL2B_20240829-104805-712_L2A_T31TGM (3-1)
    start_date = "2024-08-29"
    end_date = "2024-08-30"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 2
    assert df.date.unique().shape[0] == 1

    # two granules (same id, same date, diff. version)
    # the latest is kept
    # SENTINEL2B_20240918-104716-575_L2A_T31UGQ (4-0)
    # SENTINEL2B_20240918-104716-575_L2A_T31UGQ (3-1)
    tile = "T31UGQ"
    start_date = "2024-09-18"
    end_date = "2024-09-19"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 1

    # test cloud cover limit
    # SENTINEL2A_20240920-103808-282_L2A_T31TGM (3-1)
    tile = "T31TGM"
    start_date = "2024-09-20"
    end_date = "2024-09-26"
    df = maja_search(tile, start_date, end_date, lim_perc_cloud=50)
    assert df.shape[0] == 1

    # test for search with empty results
    start_date = "2024-09-23"
    end_date = "2024-09-24"
    df = maja_search(tile, start_date, end_date)
    assert df.empty





def test_categorize_search():

    def temp_local(
            id="test_id",
            date="2016-01-01",
            version="1-0",
            unzip_file="test_file",
            merged=False):
        args = locals().copy()
        return pd.DataFrame([args])
    
    def temp_remote(
            id = "test_id",
            date = "2016-01-01",
            version = "1-0",
            cloud_cover = "10",
            product = "test_product",
            ):
        args = locals().copy()
        return pd.DataFrame([args])

    ##################
    # one file on date
    ##################

    # same date, same id, same version
    local = temp_local()
    remote = temp_remote()
    df = categorize_search(remote, local)
    assert df.status.unique().tolist() == ["up_to_date"]

    # same date, same id, different version
    remote.version=["2-0"]
    df = categorize_search(remote, local)
    assert df.status.unique().tolist() == ["upgrade"]

    # local-remote: same date, diff. id, diff. version
    remote.version=["2-0"]
    remote.id = ["test_id_2"]
    df = categorize_search(remote, local)
    assert df.status.tolist() == ["remove", "download"]

    ###################
    # two files on date
    ###################

    local = pd.concat([
        temp_local("test_id_1", merged=True),
        temp_local("test_id_2", merged=True),])
    remote = pd.concat([
        temp_remote("test_id_1"),
        temp_remote("test_id_2"),])

    # local-remote: same date, same id, same version
    df = categorize_search(remote, local)
    assert df.status.unique().tolist() == ["up_to_date"]

    # local-remote: same date, same id, different version
    remote.version=["2-0", "1-0"]
    df = categorize_search(remote, local)
    assert df.status.unique().tolist() == ["upgrade"]

    # local-remote: same date, different id, different version
    remote = pd.concat([
        temp_remote("test_id_1"),
        temp_remote("test_id_3"),])
    
    df = categorize_search(remote, local)
    ref = pd.DataFrame(dict(
        id=["test_id_1", "test_id_2", "test_id_3"],
        status = ["download", "remove", "download"]
        ))
    assert all(df[["id", "status"]] ==  ref)

    # case of interupted merged:
    # two locals with same id but two versions
    # one remote with same id as local and one version
    local = pd.concat([
        temp_local("test_id_1", version="0-0"),
        temp_local("test_id_1", version="1-0"),])

    remote = temp_remote(id="test_id_1", version="1-0")
    df = categorize_search(remote, local)
    ref = pd.DataFrame(dict(
        id=["test_id_1", "test_id_1"],
        version_local=["1-0", "0-0"],
        version_remote=["1-0", "1-0"],
        status = ["upgrade", "remove"]
        ))
    assert all(df[["id", "version_local", "version_remote", "status"]] ==  ref)

    # case of merged product but old version not available anymore
    local = pd.concat([
        temp_local("test_id_0", version="0-0", unzip_file=pd.NA, merged=True),
        temp_local("test_id_1", version="1-0", unzip_file="test_file", merged=True),])
    remote = temp_remote(id="test_id_1", version="1-0")
    df = categorize_search(remote, local)
    assert all(df.status == ["remove", "upgrade"])

    local = pd.concat([
        temp_local("test_id_0", version="0-0", unzip_file=pd.NA, merged=True),
        temp_local("test_id_1", version="1-0", unzip_file="test_file", merged=True),])
    remote = pd.concat([
        temp_remote(id="test_id_1", version="1-0"),
        temp_remote(id="test_id_0", version="0-0"),])
    df = categorize_search(remote, local)
    assert all(df.status == (["up_to_date"]*2))

def test_download(output_dir):
    zip_dir = (output_dir / "download" / "zip").rmtree_p().makedirs_p()
    unzip_dir = (output_dir / "download" / "unzip").rmtree_p().makedirs_p()

    # # download issue for JBD, mail 2025-04-21
    # tile = "T30TXN"
    # start_date = "2019-01-16"
    # end_date = "2019-01-17"
    # bands=["B2", "B11", "CLMR2", "CLMR1"]
    # cloud_min = 100
    # cloud_max = 100

    # download issue: product with no asset
    # tile = "T31TGN"
    # start_date = "2025-01-13"
    # end_date = "2025-01-14"
    # bands=["B2", "B3", "CLMR2", "CLMR1"]
    # cloud_min = 100
    # cloud_max = 100

    # # duplicates with same datetime but different versions
    # # issue #46
    # tile = "T31UGQ"
    # start_date = "2024-09-18"
    # end_date = "2024-09-19"
    # bands=["B2", "B3", "CLMR2", "CLMR1"]
    # cloud_min = 100
    # cloud_max = 100

    # # duplicates not with same ID
    # tile = "T32ULU"
    # start_date = "2016-12-14"
    # end_date = "2016-12-15"
    # bands=["B2", "B3", "CLMR2", "CLMR1"]
    # cloud_min = 100
    # cloud_max = 100
    # "20160326-103406-538"
    
    # # duplicate with different ID and old version not downloadable anymore
    # tile = "T31TGM"
    # start_date = "2016-03-26"
    # end_date = "2016-03-27"
    # bands=["B2", "B3", "CLMR2", "CLMR1"]
    # cloud_min = 100
    # cloud_max = 100

    # # 31TGM 2017-06-19 is "tri"plicate with cloud_cover [3, 4] (2 x v1-4 + v4-0)
    # tile = "T31TGM"
    # start_date = "2017-06-19"
    # end_date = "2017-06-20"
    # bands=["B2", "B3", "CLMR2", "CLMR1"]
    # cloud_min = 100
    # cloud_max = 100

    # # 31TGM 2018-08-11 is duplicate with cloud_cover [41,52] --> became only one tile with cloud_cover 43
    # # 31TGK 2020-05-22 is duplicate with cloud_cover [11,30] --> became two tiles with [11, 8] --> became one tile
    # # 31TGM 2024-08-29 is scene split with cc [0, 6] for v3-1
    tile = "T31TGM"
    start_date = "2024-08-29"
    end_date = "2024-08-30"
    bands = ["B2", "B3", "CLMR2", "CLMR1"]
    cloud_min = 5
    cloud_max = 100

    # # T31TGK 2023-01-12 is small
    # tile="T31TGK",
    # start_date="2023-01-12",
    # end_date="2023-01-13",

    # should only download one
    downloaded, unzip_files = maja_download(
        tile=tile,
        start_date=start_date,
        end_date=end_date,
        zip_dir=zip_dir,
        unzip_dir=unzip_dir,
        lim_perc_cloud=cloud_min,
        level="LEVEL2A",
        bands=bands,
        dry_run=False,
        keep_zip=True,
        search_timeout=1,
    )

    assert len(unzip_files) == 1

    # simulate old version

    new_scene = unzip_files[0]
    fake_old_scene = Path(re.sub("V[0-9]-[0-9]$", "V0-0", new_scene))
    fake_old_scene.mkdir()
    
    downloaded, unzip_files = maja_download(
        tile=tile,
        start_date=start_date,
        end_date=end_date,
        zip_dir=zip_dir,
        unzip_dir=unzip_dir,
        lim_perc_cloud=cloud_min,
        level="LEVEL2A",
        bands=bands,
        dry_run=False,
        keep_zip=True,
        search_timeout=1,
        rm=True
    )

    assert new_scene.exists()
    assert not fake_old_scene.exists()

    # case upgrade
    new_scene.move(fake_old_scene)
    downloaded, unzip_files = maja_download(
        tile=tile,
        start_date=start_date,
        end_date=end_date,
        zip_dir=zip_dir,
        unzip_dir=unzip_dir,
        lim_perc_cloud=cloud_min,
        level="LEVEL2A",
        bands=bands,
        dry_run=False,
        keep_zip=True,
        search_timeout=1,
        rm=True,
        upgrade=True,

    )
    assert new_scene.exists()
    assert not fake_old_scene.exists()

    # it should download duplicates (again)
    downloaded, unzip_files = maja_download(
        tile=tile,
        start_date=start_date,
        end_date=end_date,
        zip_dir=zip_dir,
        unzip_dir=unzip_dir,
        lim_perc_cloud=cloud_max,
        level="LEVEL2A",
        bands=bands,
        keep_zip=True,
        dry_run=False,
    )

    assert len(downloaded) == 2
    assert len(unzip_files) == 2
    assert sum([f.exists() for f in unzip_files]) == 1
    # check if one of the files is considered as merged
    # df = get_local_maja_files(unzip_dir)
    # assert len(df.merged_id.drop_duplicates()) == 1
    for f in unzip_files:
        if f.exists():
            assert (f / "MASKS").is_dir()
            assert len((f / "MASKS").glob("*CLM_R*.tif")) == 2

    # nothing should be downloaded
    zip_files, unzip_files = maja_download(
        tile=tile,
        start_date=start_date,
        end_date=end_date,
        zip_dir=zip_dir,
        unzip_dir=unzip_dir,
        lim_perc_cloud=cloud_max,
        level="LEVEL2A",
        bands=bands,
        dry_run=False,
    )

    assert len(zip_files) == 0
    assert len(unzip_files) == 0

    # nothing should be downloaded
    zip_files, unzip_files = maja_download(
        tile=tile,
        start_date=start_date,
        end_date=end_date,
        zip_dir=zip_dir,
        unzip_dir=unzip_dir,
        lim_perc_cloud=cloud_min,
        level="LEVEL2A",
        bands=bands,
        dry_run=False,
    )

    assert len(zip_files) == 0
    assert len(unzip_files) == 0


def test_patch_merged_scenes():
    unzip_base_dir = Path("/media/boissieu/sshfs_fordead/Data/SENTINEL")
    zip_base_dir = Path("/media/boissieu/sshfs_fordead/Data/SENTINEL/Zipped")
    for unzip_dir in unzip_base_dir.glob("T*"):
        zip_dir = zip_base_dir / unzip_dir.name
        patch_merged_scenes(zip_dir, unzip_dir, dry_run=True)
