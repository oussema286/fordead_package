from fordead.stac.stac_module import get_harmonized_planetary_collection


def test_get_harmonized_planetary_collection():
    start_date = "2024-07-20"
    end_date = "2024-08-30"
    obs_bbox = [6.5425, 47.9044, 6.5548, 47.9091]
    lim_perc_cloud = 30

    coll = get_harmonized_planetary_collection(start_date, end_date, obs_bbox, lim_perc_cloud, tile=None, sign=False)
    gdf = coll.to_geodataframe()