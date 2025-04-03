import pytest

from fordead.stac.stac_module import getItemCollection, get_harmonized_theia_collection, get_harmonized_planetary_collection, get_harmonized_theiastac_collection, PLANETARY, THEIASTAC
from fordead.stac.theia_collection import MyTheiaImage
import rioxarray as rxr

@pytest.fixture(scope="module")
def obs_bbox():
    return [6.5425, 47.9044, 6.5548, 47.9091]

@pytest.fixture(scope="module")
def start_date():
    # return "2021-09-01"
    return "2015-01-01"

@pytest.fixture(scope="module")
def end_date():
    return "2022-05-01"
    # return "2018-01-01"

@pytest.fixture(scope="module")
def cloud_cover():
    return 45

@pytest.mark.parametrize("source", ["planetary", "theiastac"])
def test_getItemCollection(source, start_date, end_date, obs_bbox, cloud_cover):
    if source == "planetary":
        source = PLANETARY
    elif source == "theiastac":
        source = THEIASTAC

    col = getItemCollection(
        start_date, 
        end_date, 
        obs_bbox, 
        cloud_nb = cloud_cover, 
        source = source
    )
    gdf = col.to_geodataframe()
    assert (gdf.datetime >= start_date).all() and (gdf.datetime <= end_date).all()
    assert (col.to_geodataframe()["eo:cloud_cover"] < cloud_cover).all()
    assert set(gdf["s2:mgrs_tile"].drop_duplicates().tolist()) == set(["32ULU", "31UGP"])

def test_get_harmonized_collection(input_dir, start_date, end_date, obs_bbox, cloud_cover):
    sentinel_dir = input_dir / "sentinel_data" / "validation_tutorial" / "sentinel_data"
    col = get_harmonized_theia_collection(sentinel_dir, None, start_date, end_date, cloud_cover/100, tile="T31UGP")
    da = col.to_xarray()
    r = rxr.open_rasterio(col[0].assets["B2"].href)
    # check that ItemCollection.to_xarray is well configured by default
    assert (r.x.values == da.x.values).all()
    assert (r.y.values == da.y.values).all()

    col = get_harmonized_planetary_collection(start_date, end_date, obs_bbox, cloud_cover/100, tile=None, sign=False)
    assert "Mask" in col[0].assets
    assert col[0].assets["B2"].extra_fields["raster:bands"][0]["offset"] == 0
    assert col[-1].assets["B2"].extra_fields["raster:bands"][0]["offset"] == -1000
    gdf = col.to_geodataframe()
    assert set(gdf["tilename"].drop_duplicates().tolist()) == set(["T32ULU", "T31UGP"])

    col = get_harmonized_theiastac_collection(start_date, end_date, obs_bbox, cloud_cover/100, tile=None, sign=False)
    assert "Mask" in col[0].assets
    gdf = col.to_geodataframe()
    assert set(gdf["tilename"].drop_duplicates().tolist()) == set(["T32ULU", "T31UGP"])

# test if CLM_R1 and CLM_R2 present
# only choose CLM_R2
def test_two_clms(input_dir):
    
    s2_dir = input_dir / "sentinel_data" / "validation_tutorial" / "sentinel_data"

    s2_scene  = s2_dir.glob("*/SENTINEL*")[0]

    s2_mask = (s2_scene / "MASKS").glob("*CLM_R2.tif")[0]
    import re
    from path import Path
    s2_mask_r1 = Path(re.sub("CLM_R2\.tif$", "CLM_R1.tif", s2_mask))
    if not s2_mask_r1.exists():
        s2_mask.copy(s2_mask_r1)

    item = MyTheiaImage(s2_scene).create_item()

    assert item.assets["CLM"].href.endswith("CLM_R2.tif")
    s2_mask_r1.remove()

    




# def test_extract_reflectance(start_date, end_date, obs, cloud_cover):
#     extract_raster_values

