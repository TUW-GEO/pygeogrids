pygeogrids
==========

This is a package for creation and handling of Discrete Global Grids or Point
collections. We hope extend the interface also to projected grids(images) in the
future.

For now the main features are:

-  Creation of grids
-  Nearest neighbor search
-  conversion of grid piont indices to lat, lon
-  Storage of grids and loading grids from CF-compatible netCDF files
-  Calculation of lookup tables between grids
-  Support for different Geodetic Datums using pyproj.

Installation
------------

To install the package use pip 6.0 or later. On linux systems `pykdtree
<https://github.com/storpipfugl/pykdtree>`__ will be installed whereas on
windows systems `scipy <http://www.scipy.org/>`__ ``cKDTree`` will be used.
pykdtree is faster than the scipy implementation but it is at the moment
not available for Windows systems.


Documentation
=============

|Documentation Status|

Build Status
============

|Build Status|

Test Coverage
=============

|Coverage Status|

Citing, DOI
===========

If you want to cite pygeogrids then please use the DOI of the version
you used.

|DOI|

.. |Documentation Status| image:: https://readthedocs.org/projects/pygeogrids/badge/?version=latest
   :target: http://pygeogrids.readthedocs.org/
.. |Build Status| image:: https://travis-ci.org/TUW-GEO/pygeogrids.svg?branch=master
   :target: https://travis-ci.org/TUW-GEO/pygeogrids
.. |Coverage Status| image:: https://coveralls.io/repos/TUW-GEO/pygeogrids/badge.svg?branch=master
   :target: https://coveralls.io/r/TUW-GEO/pygeogrids?branch=master
.. |DOI| image:: https://zenodo.org/badge/12761/TUW-GEO/pygeogrids.svg
   :target: http://dx.doi.org/10.5281/zenodo.17406
