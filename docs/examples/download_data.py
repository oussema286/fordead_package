# This script aims at downloading the data necessary
# for the examples

from path import Path
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve
import zipfile

data_dir = Path(__file__).parent / "fordead_data"

print("Downloading test data...")


if not data_dir.exists():
    # data_dir.mkdir_p()
    data_url = Path("https://gitlab.com/fordead/fordead_data/-/archive/main/fordead_data-main.zip")
    
    with TemporaryDirectory(dir=data_dir.parent) as tmpdir:
        # download and extraction directory (removed automatically after transfer)
        dl_dir = Path(tmpdir)

        data_tmp_dir = dl_dir / "fordead_data-main"
        zip_path, _ = urlretrieve(data_url, dl_dir / data_url.name)
        with zipfile.ZipFile(zip_path, "r") as f:
            f.extractall(dl_dir)
        
        data_tmp_dir.rename(data_dir)

print(f"Data downloaded in: {data_dir}")
