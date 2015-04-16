
Examples
========

.. code:: python

    import pygeogrids.grids as grids
    import numpy as np

Let's create a simple regular 10x10 degree grid with grid points at the
center of each 10x10 degree cell.

First by hand to understand what is going on underneath

.. code:: python

    # create the longitudes
    lons = np.arange(-180 + 5, 180, 10)
    print(lons)
    lats = np.arange(90 - 5, -90, -10)
    print(lats)


.. parsed-literal::

    [-175 -165 -155 -145 -135 -125 -115 -105  -95  -85  -75  -65  -55  -45  -35
      -25  -15   -5    5   15   25   35   45   55   65   75   85   95  105  115
      125  135  145  155  165  175]
    [ 85  75  65  55  45  35  25  15   5  -5 -15 -25 -35 -45 -55 -65 -75 -85]


These are just the dimensions or we can also call them the "sides" of
the array that defines all the gridpoints.

.. code:: python

    # create all the grid points by using the numpy.meshgrid function
    longrid, latgrid = np.meshgrid(lons, lats)

now we can create a BasicGrid. We can also define the shape of the grid.
The first part of the shape must be in longitude direction.

.. code:: python

    manualgrid = grids.BasicGrid(longrid.flatten(), latgrid.flatten(), shape=(36, 18))
    
    # Each point of the grid automatically got a grid point number
    gpis, gridlons, gridlats = manualgrid.get_grid_points()
    print(gpis[:10], gridlons[:10], gridlats[:10])


.. parsed-literal::

    (array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), array([-175, -165, -155, -145, -135, -125, -115, -105,  -95,  -85]), array([85, 85, 85, 85, 85, 85, 85, 85, 85, 85]))


The grid point indices or numbers are useful when creating lookup tables
between grids.

We can now use the manualgrid instance to find the nearest gpi to any
longitude and latitude

.. code:: python

    ngpi, distance = manualgrid.find_nearest_gpi(15.84, 28.76)
    print(ngpi, distance)
    # convert the gpi to longitude and latitude
    print(manualgrid.gpi2lonlat(ngpi))


.. parsed-literal::

    (235, array([ 426227.83684784]))
    (15, 25)


The same grid can also be created by a method for creating regular grids

.. code:: python

    autogrid = grids.genreg_grid(10, 10)
    autogrid == manualgrid




.. parsed-literal::

    True



If your grid has a 2D shape like the ones we just created then you can
also get the row and the column of a grid point. This can be useful if
you know that you have data stored on a specific grid and you want to
read the data from a grid point.

.. code:: python

    row, col = autogrid.gpi2rowcol(ngpi)
    print(row, col)


.. parsed-literal::

    (6, 19)


Iteration over gridpoints
-------------------------

.. code:: python

    for i, (gpi, lon, lat) in enumerate(autogrid.grid_points()):
        print(gpi, lon, lat)
        if i==10: # this is just to keep the example output short
            break


.. parsed-literal::

    (0, -175.0, 85.0)
    (1, -165.0, 85.0)
    (2, -155.0, 85.0)
    (3, -145.0, 85.0)
    (4, -135.0, 85.0)
    (5, -125.0, 85.0)
    (6, -115.0, 85.0)
    (7, -105.0, 85.0)
    (8, -95.0, 85.0)
    (9, -85.0, 85.0)
    (10, -75.0, 85.0)


Calculation of lookup tables
----------------------------

If you have a two grids and you know that you want to get the nearest
neighbors for all of its grid points in the second grid you can
calculate a lookup table once and reuse it later.

.. code:: python

    # lets generate a second grid with 10 random points on the Earth surface.
    
    randlat = np.random.random(10) * 180 - 90
    randlon = np.random.random(10) * 360 - 180
    print(randlat)
    print(randlon)
    # This grid has no meaningful 2D shape so none is given
    randgrid = grids.BasicGrid(randlon, randlat)


.. parsed-literal::

    [ -1.54836122e+01  -1.35887580e+00  -4.78383560e-02   4.78709682e+00
       1.11369002e+01   3.12077283e+01  -8.71094503e+01   2.20725149e+00
       6.64563916e+01   7.87705109e+01]
    [ 121.05539154  111.61193334 -131.22315478  -46.73641204   15.1126928
     -165.14751769 -115.24386825  -56.14158745    9.9695647   143.61467711]


Now lets calculate a lookup table to the regular 10x10° grid we created
earlier

.. code:: python

    lut = randgrid.calc_lut(autogrid)
    print(lut)


.. parsed-literal::

    [390 353 328 301 271 181 618 300  90  68]


The lookup table contains the grid point indices of the other grid,
autogrid in this case.

.. code:: python

    lut_lons, lut_lats = autogrid.gpi2lonlat(lut)
    print(lut_lats)
    print(lut_lons)


.. parsed-literal::

    [-15.  -5.  -5.   5.  15.  35. -85.   5.  65.  75.]
    [ 125.  115. -135.  -45.   15. -165. -115.  -55.    5.  145.]


Storing and loading grids
-------------------------

Grids can be stored to disk as CF compliant netCDF files

.. code:: python

    import pygeogrids.netcdf as nc
    nc.save_grid('example.nc', randgrid)

.. code:: python

    loadedgrid = nc.load_grid('example.nc')

.. code:: python

    loadedgrid == randgrid




.. parsed-literal::

    True


