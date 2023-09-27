# %%
from path import Path
from fordead.stac.theia_collection import build_theia_collection, ItemCollection
import tempfile
from urllib.request import urlretrieve
import zipfile
from pandas import to_datetime
import xarray as xr

tmpdir = Path(tempfile.TemporaryDirectory(prefix="fordead_").name).mkdir()

data_url = Path("https://gitlab.com/fordead/fordead_data/-/archive/main/fordead_data-main.zip")

with tempfile.TemporaryDirectory() as tmpdir2:
    dl_dir = Path(tmpdir2)
    zip_path, _ = urlretrieve(data_url, dl_dir / data_url.name)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(tmpdir)

data_dir = tmpdir.glob('fordead_data-main')[0] 
input_dir = data_dir / "sentinel_data/dieback_detection_tutorial/study_area"

# make a temporary directory wher the catalog will be written
coll_path = tmpdir / "catalog.json"

# %%
# build a static collection with local files
coll = build_theia_collection(input_dir)
coll

# %%
# save collection
coll.save_object(coll_path)
assert coll_path.exists()

# %%
# load collection
coll2 = ItemCollection.from_file(coll_path)
assert set([item.id for item in coll2.items])==set([item.id for item in coll.items])

# %%
# filter items
start = to_datetime("2016-01-01")
end = to_datetime("2017-01-01")
subcoll = coll.filter(datetime="2016-01-01/2017-01-01")
assert set([item.datetime.timestamp() for item in subcoll])== \
    set([item.datetime.timestamp() for item in coll if \
         item.datetime>=start and item.datetime<=end])
subcoll
# %%
# filter items and lazy export to xarray
# three ways, about the same time, the first one being slightly faster: to try on big collection
subxr = coll.filter(asset_names=['B8', 'B8A'], datetime="2016-01-01/2017-01-01").to_xarray()
subxr2 = coll.filter(datetime="2016-01-01/2017-01-01").to_xarray().sel(band=['B8', 'B8A'])
assert subxr.equals(subxr2)
subxr

# %%
# In this last case band dimension was converted to variables, 
# which could be done with subxr.to_dataset(dim="band", promote_attrs=True)
subxr3 = xr.open_dataset(coll.filter(asset_names=['B8', 'B8A'], datetime="2016-01-01/2017-01-01"))
subxr3

# %%
# plot the first days
# notice the interpolation (nearest) on the fly of B8A from 20m to 10m compared to B8 (10m)
subxr[:2, :, :, :].plot(row='time', col='band') # 2 dates, 3 bands

# %%
# convert collection to geodataframe
# **warning**: geometry CRS is WGS84 (EPSG:4326)
subcoll_gdf = subcoll.to_geodataframe()
coll_crs = subcoll_gdf.loc[0,'proj:epsg']
subcoll_gdf.to_crs(coll_crs, inplace=True)
subcoll_gdf

# %%
# extract a small zone
extract_zone = subcoll_gdf.buffer(-1000).total_bounds
smallxr = subxr.rio.clip_box(*extract_zone)
smallxr[:2,:,:,:].plot(row='time', col='band')

# %%
# remove temp directory **recursively**
tmpdir.rmtree()

# Et voilà!






