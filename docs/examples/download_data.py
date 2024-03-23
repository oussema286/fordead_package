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
        try:
            with zipfile.ZipFile(zip_path, "r") as f:
                f.extractall(dl_dir)
            data_tmp_dir.rename(data_dir)
        except FileNotFoundError as e:
            print("Extraction failed, path may be too long for Windows...")
            print("Trying again extraction in a shorter temporary directory: " + Path(TemporaryDirectory().name))
            with TemporaryDirectory() as tmpdir2:
                dl_dir2 = Path(tmpdir2)
                with zipfile.ZipFile(zip_path, "r") as f:
                    f.extractall(dl_dir2)
                data_tmp_dir = dl_dir2 / "fordead_data-main"
                data_tmp_dir.rename(dl_dir2/data_dir.name).move(data_dir.parent)

print(f"Downloaded data is in: {data_dir}")
