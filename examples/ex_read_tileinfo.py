import argparse
from fordead.ImportData import TileInfo

def parse_command_line():
    # execute only if run as a script
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-o", "--data_directory", dest = "data_directory",type = str, help = "Path of the output directory")
    dictArgs={}
    for key, value in parser.parse_args()._get_kwargs():
    	dictArgs[key]=value
    return dictArgs


def read_tileinfo(data_directory):
    """
    Prints parameters, all dates used and last anomaly date computed to the console

    Parameters
    ----------
    data_directory : str
        Path of the output directory containing the saved TileInfo object

    Returns
    -------
    None

    """
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.print_info()    


if __name__ == '__main__':
    dictArgs=parse_command_line()
    read_tileinfo(**dictArgs)
