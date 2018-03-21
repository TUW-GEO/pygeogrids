==========
pygeogrids
==========

.. image:: https://travis-ci.org/TUW-GEO/pygeogrids.svg?branch=master
   :target: https://travis-ci.org/TUW-GEO/pygeogrids

.. image:: https://coveralls.io/repos/TUW-GEO/pygeogrids/badge.svg?branch=master
   :target: https://coveralls.io/r/TUW-GEO/pygeogrids?branch=master

.. image:: https://badge.fury.io/py/pygeogrids.svg
    :target: https://badge.fury.io/py/pygeogrids

.. image:: https://zenodo.org/badge/12761/TUW-GEO/pygeogrids.svg
   :target: https://doi.org/10.5281/zenodo.596401

.. image:: https://readthedocs.org/projects/pygeogrids/badge/?version=latest
   :target: http://pygeogrids.readthedocs.org/


This is a package for creation and handling of Discrete Global Grids or Point
collections. We hope extend the interface also to projected grids(images) in the
future.

Citation
========

If you want to cite pygeogrids then please use the DOI of the version
you used.

.. image:: https://zenodo.org/badge/12761/TUW-GEO/pygeogrids.svg
   :target: https://doi.org/10.5281/zenodo.596401

Installation
============

This package should be installable through pip:

.. code::

    pip install pygeogrids

To install the package use pip 6.0 or later. On linux systems `pykdtree
<https://github.com/storpipfugl/pykdtree>`__ will be installed whereas on
windows systems `scipy <http://www.scipy.org/>`__ ``cKDTree`` will be used.
pykdtree is faster than the scipy implementation but it is at the moment
not available for Windows systems.

Features
========

For now the main features are:

-  Creation of grids
-  Nearest neighbor search
-  conversion of grid piont indices to lat, lon
-  Storage of grids and loading grids from CF-compatible netCDF files
-  Calculation of lookup tables between grids
-  Support for different Geodetic Datums using pyproj.

Contribute
==========

We are happy if you want to contribute. Please raise an issue explaining what
is missing or if you find a bug. We will also gladly accept pull requests
against our master branch for new features or bug fixes.

Development setup
-----------------

For Development we recommend a ``conda`` environment. You can create one
including test dependencies and debugger by running
``conda env create -f environment.yml``. This will create a new ``pygeogrids``
environment which you can activate by using ``source activate pygeogrids``.

Guidelines
----------

If you want to contribute please follow these steps:

- Fork the pygeogrids repository to your account
- Clone the repository
- make a new feature branch from the pygeogrids master branch
- Add your feature
- Please include tests for your contributions in one of the test directories.
  We use py.test so a simple function called test_my_feature is enough
- submit a pull request to our master branch