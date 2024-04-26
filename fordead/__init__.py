# from ._version import __version__
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("fordead")
except PackageNotFoundError:
    # package is not installed
    pass