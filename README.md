# pygeogrids #

This is a package for creation and handling of Discrete Global Grids. We hope
extend the interface also to projected grids(images) in the future.

For now the main features are:

- Creation of grids
- Nearest neighbor search [pykdtree](https://github.com/storpipfugl/pykdtree)
- conversion of grid piont indices to lat, lon
- Storage of grids and loading grids from CF-compatible netCDF files
- Calculation of lookup tables between grids

# Documentation

[![Documentation Status](https://readthedocs.org/projects/pygeogrids/badge/?version=latest)](http://pygeogrids.readthedocs.org/)


# Build Status

[![Build Status](https://travis-ci.org/TUW-GEO/pygeogrids.svg?branch=master)](https://travis-ci.org/TUW-GEO/pygeogrids)

# Test Coverage

[![Coverage Status](https://coveralls.io/repos/TUW-GEO/pygeogrids/badge.svg?branch=master)](https://coveralls.io/r/TUW-GEO/pygeogrids?branch=master)
