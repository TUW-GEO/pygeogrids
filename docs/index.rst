==========
pygeogrids
==========


pygeogrids is a package for creation and handling of Discrete Global Grids.

It can be used to define a grid on the globe using numpy arrays of longitude and
latitude.  These grids can also have unique grid point numbers. The grids must
not be valid globally but can e.g. only cover the Continents.

When a grid is defined it can be used to quickly find the nearest neigbor of a a
given lat, lon coordinate on the grid. For that the lon, lat coordinates are
converted to Cartesian coordinates. This approach is of limited use for high
resolution data which might rely on a specific geodetic datum.

The class :class:`pygeogrids.grids.CellGrid` extends this basic grid with the
ability to store a additional cell number for each grid point. This can be used
to tile a grid in e.g. 5x5° cells. We often store remote sensing data in cells
to partition a dataset into manageable parts. This link with the grid class
enables us to easily find the link between a grid point and the cell file in
which the relevant data is stored.

Please see the examples in this documentation as well as the `pytesmo
<https://github.com/TUW-GEO/pytesmo>`_ code for real world usage examples.

 

Contents
========

.. toctree::
   :maxdepth: 2
               
   Creating and working with grid objects.rst
   changes.rst
   License <license>
   api/modules.rst
