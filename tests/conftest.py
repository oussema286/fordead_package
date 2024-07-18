import pystac
import pytest
from path import Path
import geopandas as gpd

here = Path(__file__).parent
download_script = here / ".." / "docs" / "examples" / "download_data.py"
print("Downloading the test data...")
exec(open(download_script).read())


@pytest.fixture(scope="session")
def input_dir():
    x = here / "fordead_data"
    yield x

@pytest.fixture(scope="session")
def output_dir():
    x = (here / "outputs").mkdir_p()
    yield x