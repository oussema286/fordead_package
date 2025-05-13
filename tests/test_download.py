from path import Path
from fordead.theia_preprocess import maja_download, maja_search, patch_merged_scenes, categorize_search
import pandas as pd


def test_maja_search():
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
    start_date = "2024-08-29"
    end_date = "2024-08-30"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 2
    assert df.date.unique().shape[0] == 1

    # two granules (same id, same date, diff. version)
    # the latest is kept
    tile = "T31UGQ"
    start_date = "2024-09-18"
    end_date = "2024-09-19"
    df = maja_search(tile, start_date, end_date)
    assert df.shape[0] == 1

    # test cloud cover limit
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
    temp_local = pd.DataFrame(
        dict(
            id = ["test_id"],
            date = ["2016-01-01"],
            version = ["1-0"],
            unzip_file = ["test_file"],
            merged = [False],
        )
    )
    
    temp_remote = pd.DataFrame(
        dict(
            id = ["test_id"],
            date = ["2016-01-01"],
            version = ["1-0"],
            cloud_cover = ["10"],
            product = ["test_product"],
        )
    )

    ##################
    # one file on date
    ##################

    # same date, same id, same version
    local = temp_local.copy() 
    remote = temp_remote.copy()
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
    assert df.status.tolist() == ["not-in-search", "download"]

    ###################
    # two files on date
    ###################
    local = pd.concat([temp_local.copy(), temp_local.copy()])
    local.id=["test_id_1", "test_id_2"]
    local.merged=[True, True]
    remote = pd.concat([temp_remote.copy(), temp_remote.copy()])
    remote.id=["test_id_1", "test_id_2"]

    # local-remote: same date, same id, same version
    df = categorize_search(remote, local)
    assert df.status.unique().tolist() == ["up_to_date"]

    # local-remote: same date, same id, different version
    remote.version=["2-0", "1-0"]
    df = categorize_search(remote, local)
    assert df.status.unique().tolist() == ["upgrade"]

    # local-remote: same date, different id, different version
    remote = pd.concat([temp_remote.copy(), temp_remote.copy()])
    remote.id=["test_id_1", "test_id_3"]
    df = categorize_search(remote, local)
    ref = pd.DataFrame(dict(
        id=["test_id_1", "test_id_2", "test_id_3"],
        status = ["download", "not-in-search", "download"]
        ))
    assert all(df[["id", "status"]] ==  ref)

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

    assert len(downloaded) == 1

    # # simulate old version
    # for f in unzip_files:
    #     if f.exists():
    #         new_file = re.sub("V[0-9]-[0-9]$", "V1-1", f)
    #         f.move(new_file)

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
