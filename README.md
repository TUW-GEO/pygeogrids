# pygeogrids #

This is a package for creation and handling of Discrete Global Grids. We hope
extend the interface also to projected grids(images) in the future.

For now the main features are:

- Creation of grids
- Nearest neighbor search [pykdtree](https://github.com/storpipfugl/pykdtree)
- conversion of grid piont indices to lat, lon
- Storage of grids and loading grids from CF-compatible netCDF files
- Calculation of lookup tables between grids

# Build Status

![https://travis-ci.org/TUW-GEO/pygeogrids](https://travis-ci.org/TUW-GEO/pygeogrid.svg?branch=master)
