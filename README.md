# pygeogrids #

This is a package for creation and handling of Discrete Global Grids. We hope
extend the interface also to projected grids(images) in the future.

For now the main features are:

- Creation of grids
- Nearest neighbor search [pykdtree](https://github.com/storpipfugl/pykdtree)
- conversion of grid piont indices to lat, lon
- Storage of grids and loading grids from CF-compatible netCDF files
- Calculation of lookup tables between grids

## Optional Requirements

- [pykdtree](https://github.com/storpipfugl/pykdtree) or [scipy](http://www.scipy.org/) if you want to use the nearest neighbor search. pykdtree is much faster than the scipy implementation but it is at the moment not available for Windows systems.

# Documentation

[![Documentation Status](https://readthedocs.org/projects/pygeogrids/badge/?version=latest)](http://pygeogrids.readthedocs.org/)


# Build Status

[![Build Status](https://travis-ci.org/TUW-GEO/pygeogrids.svg?branch=master)](https://travis-ci.org/TUW-GEO/pygeogrids)

# Test Coverage

[![Coverage Status](https://coveralls.io/repos/TUW-GEO/pygeogrids/badge.svg?branch=master)](https://coveralls.io/r/TUW-GEO/pygeogrids?branch=master)

#Citing, DOI

If you want to cite pygeogrids then please use the DOI of the version you used.

[![DOI](https://zenodo.org/badge/12761/TUW-GEO/pygeogrids.svg)](http://dx.doi.org/10.5281/zenodo.17406)
