=========
Changelog
=========

Version x.x.x
=============

-

Version 0.3.2
=============

- FIX: Nearest neighbour search for grids with non-default GPIs
- Replace Travis CI with Github Actions workflows.

Version 0.3.1
=============

- Add k parameter to nearest neighbor search (number of nearest neighbors to return)


Version 0.3.0
=============

- Refracture package to pyscaffold 3 standard

Version 0.2.6
=============

- Allow subsetting from non-binary masks
- Fix ParallelArcDist function (two calls of deg2rad(lat))
- Update readme
- Update to PyScaffold 2.5.9

Version 0.2.5
=============

- Fix speed bug of gpi2cell
- Update copyright header

Version 0.2.4
=============

- Add option to subset a grid with a shape file (OGRGeometry) in
  get_shp_grid_points.
- Add shapefile module for reading shapefiles from
  http://biogeo.ucdavis.edu/data/gadm2.8/gadm28_levels.shp.zip by Global
  Administrative Level
- Ensure that `get_bbox_grid_points` returns points while taking cell order into
  account.

Version 0.2.3
=============

- Fix bug in calc_lut in case of differently ordered subset of a grid.
- Add function to reorder grid based on different cell size. (See grids.reorder_to_cellsize)

Version 0.2.2
=============

- Add option to load grids with non standard variable name for gpis.

Version 0.2.1
=============

- Fix bug in gpi2lonlat with subset, see #42
- Add simple script for plotting a global cell partitioning.

Version 0.2.0
=============

- fix bug in storing/loading grids with shape attribute set.
- change equality check of grids to be more flexible. Now only a match of the
  tuples gpi, lon, lat, cell is checked. The order does no longer matter.
- Shape definition changed to correspond to what one would expect. Now a 1x1
  regular global grid has the shape (180, 360) corresponding to the 180 rows and
  360 columns that the array has. This was necessary since the genreg_grid
  function produced grids with wrong lon2d, lat2d arrays because the shape was
  not correct

Version 0.1.9
=============

-  bugfix in lonlat2cell. Improvements in dependency installation and
   documentation.

Version 0.1.7
=============

-  bugfix in gpi2lonlat. Now supports array as input.

Version 0.1.6
=============

-  add geodatic datum functionality to grid objects

Version 0.1.5
=============

-  bugfix of subgrid creation which returned wrongly shaped subarrays

Version 0.1.4
=============

-  fix bug in lookuptable generation when gpis have custom ordering
-  add functions for getting subgrids from cells and gpis

Version 0.1.3
=============

-  change meaning and rename grid dimensions to lon2d, lat2d. They do
   now represent 2d arrays of latitudes and longitudes which means that
   they no longer have to be regular in order to be able to have a
   shape. This is useful for e.g. orbit data

Version 0.1.2
=============

-  fix issue #19 by refactoring the iterable checking into own function
-  made pykdtree an optional requirement see issue #18

Version 0.1.1
=============

-  added support for saving more subsets and loading a certain one
   in/from a netcdf grid file
-  fix #15 by setting correct shape for derived cell grids
-  fix issue #14 of gpi2rowcol input types

Version 0.1
===========

-  Initial version pulled out of pytesmo
-  added support for iterables like lists and numpy arrays to functions
   like find\_nearest\_gpi. numpy arrays should work everywhere if you
   want to get information from a grid. see issue #3 and #4
-  fixed bugs occuring during storage as netCDF file see issue #8
-  comparison of grids is no longer using exact float comparison, see
   issue #9
-  added documentation and examples for working with the grid objects,
   see issue #1
