# author(s) : Kenji Ose

import geopandas as gp
from shapely.geometry import Polygon, Point
from pyproj import Proj, transform
import pystac_client
import pystac
import planetary_computer

def get_vectorBbox(vector_path):
    """
    get layer bounding box

    - vector_path: <string> vectorfile path

    return: <list> of bbox coordinates in lat/lon 
            [lon_min, lat_min, lon_max, lat_max]
    """
    obs = gp.read_file(vector_path)
    obs = obs.to_crs("EPSG:4326")
    bbox = list(obs.total_bounds)
    return bbox

def getItemCollection(startdate, enddate, bbox, cloud_nb = 0):
    """
    get item collection from Microsoft Planetary Computer

    - startdate: <string> start date yyyy-mm-dd
    - enddate: <string> end date yyyy-mm-dd
    - bbox: <list> bounding box [lon_min, lat_min, lon_max, lat_max]
    - cloud_nb: <int> cloud percentage [default: 0]

    return pystac itemcollection object
    """
    catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
    )
    time_range = f"{startdate}/{enddate}" #"2021-07-01/2021-12-01"
    bbox = bbox
    cloud_nb = cloud_nb

    # recherche avec filtre de type 'query'
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime=time_range,
        query={"eo:cloud_cover": {"lt": cloud_nb}},
        sortby="datetime"
    )

    itemsColl = search.get_item_collections()
    return itemsColl

# Conversion de tous les items découverts par la recherche, 
# on crée un objet ItemcCollection pour avoir la liste des items. 

def get_s2_epsgXY(item_collection):
    """
    get S2 tile name, epsg and geometry (in lat/long)
    
    - item_collection: pystac item_collection object

    return: list with the following elements : 
            tile_name <string>, epsg_code <string>, geometry <list>
    """
    out_list = []
    for item in item_collection:
        tile = item.properties['s2:mgrs_tile']
        epsg = item.properties["proj:epsg"]
        if not any(tile in i for i in out_list):
            tileinfo = [tile, epsg, item.geometry['coordinates'][0]]
            out_list.append(tileinfo)
        
        return out_list

def coord2epsg(tilesinfo, in_epsg = '4326'):
    """
    convert S2 tile geometry from input csr (default epsg:4326) to output crs
    
    - tilesinfo : <list> output of get_s2_epsgXY () function
    - in_epsg : <string> epsg code [default : 4326]

    return: list with the following elements : 
            tile_name <string>, epsg_code <string>, geometry <list>
    """
    out_list = []
    inProj = Proj(init=f'epsg:{in_epsg}')
    for tile in tilesinfo:
        outProj = Proj(init=f'epsg:{tile[1]}')
        in_coord = tile[2]
        out_coord = []
        for coord in in_coord:
            outX, outY = transform(inProj, outProj, coord[0], coord[1])
            out_coord.append([round(outX), round(outY)])
        tileinfo = [tile[0], tile[1], out_coord]
        out_list.append(tileinfo)
    return out_list

def tile_filter(item_collection, tile_name):
    """
    Filter S2 item_collection according to Tile ID

    - item_collection: <pystac object> input S2 item_collection
    - tile_name: <string> S2 tile ID 

    return: <pystac object> filtered item_collection
    """
    filt_item = []
    for item in item_collection:
        if item.properties["s2:mgrs_tile"] == tile_name:
            filt_item.append(item)
    new_coll = pystac.item_collection.ItemCollection(filt_item)
    return new_coll

def get_items_tiles(item_collection):
    """
    Link S2 tile with corresponding EPSG

    - item_collection: <pystac object> S2 item collection

    return: <list> of list with following elements [tile name, epsg code]
    """
    out_list = []
    for item in item_collection:
        tile = item.properties['s2:mgrs_tile']
        epsg = item.properties["proj:epsg"]
        info = [tile, epsg]
        if info not in out_list:
            out_list.append(info)
    return out_list

if __name__ == '__main__':
    obs_path = "D:/PROJETS/PRJ_FORDEAD/TEST_STAC/data/observations_tuto.shp"
    obs_bbox = get_vectorBbox(obs_path)
    print(obs_bbox)

    coll = getItemCollection("2021-07-01", "2021-12-01", obs_bbox, 20)
    print(coll.items)