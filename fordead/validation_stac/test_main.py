#
# author : Kenji Ose
#
import time
from stac_module import get_vectorBbox, getItemCollection
from obs_to_s2_grid import obs_to_s2_grid
from extract_reflectance import extract_reflectance

if __name__ == '__main__':

    # input and output files

    # input vector file path
    obs_path = "D:/PROJETS/PRJ_FORDEAD/TEST_STAC/data/observations_tuto.shp"
    # output vector file path
    export_shp = "D:/PROJETS/PRJ_FORDEAD/TEST_STAC/data/export05.shp"
    # output csv file path
    export_csv = "D:/PROJETS/PRJ_FORDEAD/TEST_STAC/data/export05.csv"

    # get bounding box of vector layer
    obs_bbox = get_vectorBbox(obs_path)
    # start and end dates of S2 time series
    startDate = "2021-07-01"
    endDate = "2021-12-01"
    # cloud percentage (lt)
    cloudPct = 20

    # get pystac S2 item collection
    coll = getItemCollection(startDate, endDate, obs_bbox, cloudPct)

    # convert obs polygons into points (pixel centroids)
    start_time = time.time()
    obs_to_s2_grid(obs_path, coll, export_shp)
    duration = time.time() - start_time
    print(f"durée 'obs_to_s2_grid': {duration/60} min")

    # sample raster values
    start_time = time.time()
    extract_reflectance(export_shp, coll, export_csv)
    duration = time.time() - start_time
    print(f"durée 'extract_reflectance: {duration/60} min")
    
    end_time = time.time()