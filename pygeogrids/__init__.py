from .grids import BasicGrid, CellGrid, genreg_grid, lonlat2cell
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'
