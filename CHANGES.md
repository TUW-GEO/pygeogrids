# v0.1 #
- Initial version pulled out of pytesmo
- added support for iterables like lists and numpy arrays to functions like
find_nearest_gpi. numpy arrays should work everywhere if you want to get
information from a grid. see issue #3 and #4
- fixed bugs occuring during storage as netCDF file see issue #8
- comparison of grids is no longer using exact float comparison, see issue #9
- added documentation and examples for working with the grid objects, see issue #1
