# v0.1.5

- bugfix of subgrid creation which returned wrongly shaped subarrays

# v0.1.4

- fix bug in lookuptable generation when gpis have custom ordering
- add functions for getting subgrids from cells and gpis

# v0.1.3 #

- change meaning and rename grid dimensions to lon2d, lat2d. They do now
  represent 2d arrays of latitudes and longitudes which means that they no
  longer have to be regular in order to be able to have a shape. This is useful
  for e.g. orbit data

# v0.1.2 #
- fix issue #19 by refactoring the iterable checking into own function
- made pykdtree an optional requirement see issue #18

# v0.1.1 #
- added support for saving more subsets and loading a certain one in/from a netcdf grid file
- fix #15 by setting correct shape for derived cell grids
- fix issue #14 of gpi2rowcol input types

# v0.1 #
- Initial version pulled out of pytesmo
- added support for iterables like lists and numpy arrays to functions like
find_nearest_gpi. numpy arrays should work everywhere if you want to get
information from a grid. see issue #3 and #4
- fixed bugs occuring during storage as netCDF file see issue #8
- comparison of grids is no longer using exact float comparison, see issue #9
- added documentation and examples for working with the grid objects, see issue #1

