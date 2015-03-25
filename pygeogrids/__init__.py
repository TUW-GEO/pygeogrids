from ._version import get_versions
from .grids import BasicGrid, CellGrid, genreg_grid, lonlat2cell

__version__ = get_versions()['version']
del get_versions
