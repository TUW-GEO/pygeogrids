
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

    [ 17.29906911 -35.38535729 -71.93633461 -45.50119896  21.44038298
     -51.8807349  -53.74357805  86.06241248  80.23097461 -70.56187193]
    [ 117.908495     55.71301743 -107.521213   -167.90819856   70.20423657
     -153.14746009  -12.72514138  -44.59386791   25.45141516    3.75179355]


Now lets calculate a lookup table to the regular 10x10° grid we created
earlier

.. code:: python

    lut = randgrid.calc_lut(autogrid)
    print(lut)


.. parsed-literal::

    [281 455 583 469 241 506 520  13  20 594]


The lookup table contains the grid point indices of the other grid,
autogrid in this case.

.. code:: python

    lut_lons, lut_lats = autogrid.gpi2lonlat(lut)
    print(lut_lats)
    print(lut_lons)


.. parsed-literal::

    [ 15. -35. -75. -45.  25. -55. -55.  85.  85. -75.]
    [ 115.   55. -105. -165.   75. -155.  -15.  -45.   25.    5.]


Storing and loading grids
-------------------------

Grids can be stored to disk as CF compliant netCDF files

.. code:: python

    import pygeogrids.netcdf as nc
    nc.save_grid('example.nc', randgrid)

.. code:: python

    loadedgrid = nc.load_grid('example.nc')

