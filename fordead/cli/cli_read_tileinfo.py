import click
from fordead.ImportData import TileInfo

@click.group()
def cli():
    """Main entrypoint."""

@cli.command(name='read_tileinfo')
@click.option("-o", "--data_directory", type = str, help = "Path of the output directory containing the saved TileInfo object")
def cli_read_tileinfo(data_directory,test):
    """
    Prints parameters, all dates used and last anomaly date computed to the console
    \f
    Parameters
    ----------
    data_directory : str
        Path of the output directory containing the saved TileInfo object
    Returns
    -------
    """
    tile = TileInfo(data_directory)
    tile = tile.import_info()
    tile.print_info()

if __name__ == '__main__':
    cli_read_tileinfo()
    