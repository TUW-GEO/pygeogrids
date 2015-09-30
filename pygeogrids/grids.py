# Copyright (c) 2015, Vienna University of Technology,
# Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Vienna University of Technology, Department
#      of Geodesy and Geoinformation nor the names of its contributors may
#      be used to endorse or promote products derived from this software
#      without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# created on Aug 26, 2013
# author: Christoph Paulik Christoph.Paulik@geo.tuwien.ac.at

"""
The grids module defines the grid classes.
"""

import numpy as np
import numpy.testing as nptest

try:
    from itertools import izip as zip
except ImportError:
    pass  # python3

import pygeogrids.nearest_neighbor as NN


class GridDefinitionError(Exception):
    pass


class GridIterationError(Exception):
    pass


class BasicGrid(object):

    """
    Grid that just has lat,lon coordinates and can find the
    nearest neighbour. It can also yield the gpi, lat, lon
    information in order.

    Parameters
    ----------
    lon : numpy.array
        longitudes of the points in the grid
    lat : numpy.array
        latitudes of the points in the grid
    gpis : numpy.array, optional
        if the gpi numbers are in a different order than the
        lon and lat arrays an array containing the gpi numbers
        can be given
        if no array is given here the lon lat arrays are given
        gpi numbers starting at 0
    subset : numpy.array, optional
        if the active part of the array is only a subset of
        all the points then the subset array which is a index
        into lon and lat can be given here
    setup_kdTree : boolean, optional
        if set (default) then the kdTree for nearest neighbour
        search will be built on initialization
    shape : tuple, optional
        The shape of the grid array in 2-d space.
        e.g. for a 1x1 degree global regular grid the shape would be (360,180).
        if given the grid can be reshaped into the given shape
        this indicates that it is a regular grid and fills the
        attributes self.lon2d and self.lat2d which
        define the grid only be the meridian coordinates(self.lon2d) and
        the coordinates of the circles of latitude(self.lat2d).
        The shape has to be given as (lon2d, lat2d)
        It it is not given the shape is set to the length of the input
        lon and lat arrays.

    Attributes
    ----------
    arrlon : numpy.array
        1D array of all longitudes of the grid
    arrlat : numpy.array
        1D array of all latitudes of the grid
    n_gpi : int
        number of gpis in the grid
    gpidirect : boolean
        if true the gpi number is equal to the index
        of arrlon and arrlat
    gpis : numpy.array
        gpi number for elements in arrlon and arrlat
        gpi[i] is located at arrlon[i],arrlat[i]
    subset : numpy.array
        if given then this contains the indices of a subset of
        the grid. This can be used if only a part of a grid is
        interesting for a application. e.g. land points, or only
        a specific country
    allpoints : boolean
        if False only a subset of the grid is active
    activearrlon : numpy.array
        array of longitudes that are active, is defined by
        arrlon[subset] if a subset is given otherwise equal to
        arrlon
    activearrlat : numpy.array
        array of latitudes that are active, is defined by
        arrlat[subset] if a subset is given otherwise equal to
        arrlat
    activegpis : numpy.array
        array of gpis that are active, is defined by
        gpis[subset] if a subset is given otherwise equal to
        gpis
    issplit : boolean
        if True then the array was split in n parts with
        the self.split function
    kdTree : object
        grid.nearest_neighbor.findGeoNN object for
        nearest neighbor search
    shape : tuple, optional
        if given during initialization then this is
        the shape the grid can be reshaped to
    lat2d : numpy.array, optional
        if shape is given this attribute contains all latitudes according to
        the provided 2d-shape that make up the grid
    lon2d : numpy.array, optional
        if shape is given this attribute contains all longitudes according to
        the provided 2d-shape that make up the grid
    """

    def __init__(self, lon, lat, gpis=None, subset=None, setup_kdTree=True,
                 shape=None):
        """
        init method, prepares lon and lat arrays for _transform_lonlats if
        necessary

        """
        lon = np.asanyarray(lon)
        lat = np.asanyarray(lat)
        if gpis is not None:
            gpis = np.asanyarray(gpis)
        if subset is not None:
            subset = np.asanyarray(subset)

        if lat.shape != lon.shape:
            raise GridDefinitionError(
                "lat and lon np.arrays have to have equal shapes")

        self.n_gpi = len(lon)

        self.arrlon = lon
        self.arrlat = lat

        self.shape = None

        if shape is not None and len(shape) == 2:
            if len(self.arrlat) % shape[0] != 0:
                msg = ("Given shape does not have the correct first dimension."
                       " Length of lat array is not divisible by shape[0] "
                       " without rest")
                raise GridDefinitionError(msg)

            if len(self.arrlon) % shape[1] != 0:
                msg = ("Given shape does not have the correct second "
                       "dimension. Length of lon array is not divisible by "
                       "shape[1] without rest")
                raise GridDefinitionError(msg)

            self.shape = shape
            self.lat2d = np.reshape(self.arrlat, self.shape)
            self.lon2d = np.reshape(self.arrlon, self.shape)

        else:
            self.shape = tuple([len(self.arrlon)])

        if gpis is None:
            self.gpis = np.arange(self.n_gpi)
            self.gpidirect = True
        else:
            if lat.shape != gpis.shape:
                raise GridDefinitionError("lat, lon gpi np.arrays have to "
                                          "have equal shapes")
            self.gpis = gpis
            self.gpidirect = False

        self.subset = subset

        if subset is not None:
            self.activearrlon = self.arrlon[subset]
            self.activearrlat = self.arrlat[subset]
            self.activegpis = self.gpis[subset]
            self.allpoints = False
        else:
            self.activearrlon = self.arrlon
            self.activearrlat = self.arrlat
            self.activegpis = self.gpis
            self.allpoints = True

        self.issplit = False

        self.kdTree = None
        if setup_kdTree:
            self._setup_kdtree()

    def _setup_kdtree(self):
        """
        Setup kdTree
        """
        if self.kdTree is None:
            self.kdTree = NN.findGeoNN(self.activearrlon, self.activearrlat)
            self.kdTree._build_kdtree()

    def split(self, n):
        """
        Function splits the grid into n parts this changes not function but
        grid_points() which takes the argument n and will only iterate through
        this part of the grid.

        Parameters
        ----------
        n : int
            Number of parts the grid should be split into
        """
        self.issplit = True
        self.subarrlats = np.array_split(self.activearrlat, n)
        self.subarrlons = np.array_split(self.activearrlon, n)
        self.subgpis = np.array_split(self.activegpis, n)

    def unite(self):
        """
        Unites a split array, so that it can be iterated over as a whole
        again.
        """
        self.issplit = False

    def grid_points(self, *args):
        """
        Yields all grid points in order

        Parameters
        ----------
        n : int, optional
            if the grid is split in n parts using the split function
            then this iterator will only iterate of the nth part of the
            grid

        Returns
        -------
        gpi : long
            grid point index
        lon : float
            longitude of gpi
        lat : float
            longitude of gpi
        """

        if not self.issplit and len(args) == 0:
            return self._normal_grid_points()
        elif self.issplit and len(args) == 1:
            return self._split_grid_points(args[0])

        raise GridIterationError("this function only takes an argument if "
                                 "the grid is split, and takes no argument "
                                 "if the grid is not split")

    def get_grid_points(self, *args):
        """
        Returns all active grid points.

        Parameters
        ----------
        n : int, optional
            if the grid is split in n parts using the split function
            then this function will only return the nth part of the
            grid

        Returns
        -------
        gpis : numpy.ndarray
            Grid point indices.
        arrlon : numpy.ndarray
            Longitudes.
        arrlat : numpy.ndarray
            Latitudes.
        """

        if not self.issplit and len(args) == 0:
            return (self.activegpis,
                    self.activearrlon,
                    self.activearrlat)

        elif self.issplit and len(args) == 1:
            n = args[0]
            return (self.subgpis[n],
                    self.subarrlons[n],
                    self.subarrlats[n])

    def _normal_grid_points(self):
        """
        Yields all grid points in order.

        Returns
        -------
        gpi : long
            grid point index
        lon : float
            longitude of gpi
        lat : float
            longitude of gpi
        """
        for i, (lon, lat) in enumerate(zip(self.activearrlon,
                                           self.activearrlat)):
            yield self.activegpis[i], lon, lat

    def _split_grid_points(self, n):
        """
        Yields all grid points or split grid in order.

        Parameters
        ----------
        n : int
            Number of subgrid to yield

        Returns
        -------
        gpi : long
            Grid point index.
        lon : float
            Longitude of gpi.
        lat : float
            Longitude of gpi.
        """

        for i, (lon, lat) in enumerate(zip(self.subarrlons[n],
                                           self.subarrlats[n])):
            yield self.subgpis[n][i], lon, lat

    def find_nearest_gpi(self, lon, lat, max_dist=np.Inf):
        """
        Finds nearest gpi, builds kdTree if it does not yet exist.

        Parameters
        ----------
        lon : float or iterable
            Longitude of point.
        lat : float or iterable
            Latitude of point.

        Returns
        -------
        gpi : long
            Grid point index.
        distance : float
            Distance of gpi to given lon, lat.
            At the moment not on a great circle but in spherical
            cartesian coordinates.
        """
        # check if input is iterable
        iterable = _element_iterable(lon)

        if self.kdTree is None:
            self._setup_kdtree()

        d, ind = self.kdTree.find_nearest_index(lon, lat, max_dist=max_dist)

        if not iterable:
            d = d[0]
            ind = ind[0]

        if self.gpidirect and self.allpoints:
            return ind, d

        return self.activegpis[ind], d

    def gpi2lonlat(self, gpi):
        """
        Longitude and latitude for given gpi.

        Parameters
        ----------
        gpi : int32 or iterable
            Grid point index.

        Returns
        -------
        lon : float
            Longitude of gpi.
        lat : float
            Latitude of gpi
        """
        if self.gpidirect:
            return self.arrlon[gpi], self.arrlat[gpi]
        else:
            index = np.where(self.activegpis == gpi)[0][0]
            return self.activearrlon[index], self.activearrlat[index]

    def gpi2rowcol(self, gpi):
        """
        If the grid can be reshaped into a sensible 2D shape then this
        function gives the row(latitude dimension) and
        column(longitude dimension) indices of the gpi in the 2D grid.

        Parameters
        ----------
        gpi : int32
            Grid point index.

        Returns
        -------
        row : int
            Row in 2D array.
        col : int
            Column in 2D array.
        """
        # check if iterable
        iterable = _element_iterable(gpi)

        gpi = np.atleast_1d(gpi)
        if len(self.shape) == 2:
            if self.gpidirect:
                index = gpi
            else:
                # get the indices that would sort the gpis
                gpisorted = np.argsort(self.gpis)
                # find the position where the gpis fit in the sorted array
                pos = np.searchsorted(self.gpis[gpisorted], gpi)
                index = gpisorted[pos]

            index_lat = (index / self.shape[0]).astype(np.int)
            index_lon = index % self.shape[0]
            if not iterable:
                index_lat = index_lat[0]
                index_lon = index_lon[0]
            return index_lat, index_lon

        else:
            raise(GridDefinitionError("Grid has no 2D shape"))

    def calc_lut(self, other, max_dist=np.Inf, into_subset=False):
        """
        Takes other BasicGrid or CellGrid objects and computes a lookup table
        between them. The lut will have the size of self.n_gpis and will
        for every grid point have the nearest index into other.arrlon etc.

        Parameters
        ----------
        other : grid object
            to which to calculate the lut to
        max_dist : float, optional
            maximum allowed distance in meters
        into_subset : boolean, optional
            if set the returned lut will have the index into the subset
            if the other grid is a subset of a grid.
            Example:
            if e.g. ind_l is used for the warp_grid some datasets will
            be given as arrays with len(ind_l) elements. These
            datasets can not be indexed with gpi numbers but have to
            be indexed with indices into the subset
        """

        if self.kdTree is None:
            self._setup_kdtree()

        if other.kdTree is None:
            other._setup_kdtree()

        if self.kdTree.kdtree is not None and other.kdTree.kdtree is not None:
            dist, index = other.kdTree.find_nearest_index(
                self.activearrlon, self.activearrlat, max_dist=max_dist)

            valid_index = np.where(dist != np.inf)[0]
            dist = dist[valid_index]
            index = index[valid_index]
            if not other.gpidirect or not other.allpoints:
                if not into_subset:
                    index = other.activegpis[index]

            active_lut = np.empty_like(self.activearrlat, dtype=np.int64)
            active_lut.fill(-1)
            active_lut[valid_index] = index

            if not self.allpoints:
                gpi_lut = np.empty_like(self.gpis)
                gpi_lut.fill(-1)
                gpi_lut[self.subset] = active_lut
            elif not self.gpidirect:
                gpi_lut = np.empty(np.max(self.activegpis) + 1, dtype=np.int64)
                gpi_lut.fill(-1)
                gpi_lut[self.activegpis] = active_lut
            else:
                gpi_lut = active_lut

            return gpi_lut

    def get_bbox_grid_points(self, latmin=-90, latmax=90, lonmin=-180,
                             lonmax=180, coords=False):
        """
        Returns all grid points located in a submitted geographic box,
        optinal as coordinates

        Parameters
        ----------
        latmin : float, optional
            minimum latitude
        latmax : float, optional
            maximum latitude
        lonmin : float, optional
            minimum latitude
        lonmax : float, optional
            maximum latitude
        coords : boolean, optional
            set to True if coordinates should be returned

        Returns
        -------
        gpi : numpy.ndarray
            grid point indices, if coords=False
        lat : numpy.ndarray
            longitudes of gpis, if coords=True
        lon : numpy.ndarray
            longitudes of gpis, if coords=True
        """

        index = np.where((self.activearrlat <= latmax) &
                         (self.activearrlat >= latmin) &
                         (self.activearrlon <= lonmax) &
                         (self.activearrlon >= lonmin))

        if coords is True:
            return self.activearrlat[index], self.activearrlon[index]
        else:
            return self.activegpis[index]

    def to_cell_grid(self, cellsize=5.0, cellsize_lat=None, cellsize_lon=None):
        """
        Convert grid to cellgrid with a cell partition of cellsize.

        Parameters
        ----------
        cellsize : float, optional
            Cell size in degrees
        cellsize_lon : float, optional
            Cell size in degrees on the longitude axis
        cellsize_lat : float, optional
            Cell size in degrees on the latitude axis

        Returns
        -------
        cell_grid : CellGrid object
            Cell grid object.
        """
        cells = lonlat2cell(self.arrlon, self.arrlat, cellsize=cellsize,
                            cellsize_lat=cellsize_lat,
                            cellsize_lon=cellsize_lon)

        if self.gpidirect:
            gpis = None
        else:
            gpis = self.gpis

        return CellGrid(self.arrlon, self.arrlat, cells, gpis=gpis,
                        subset=self.subset, shape=self.shape)

    def subgrid_from_gpis(self, gpis):
        """
        Generate a subgrid for given gpis.

        Parameters
        ----------
        gpis : int, numpy.ndarray
            Grid point indices.

        Returns
        -------
        grid : BasicGrid
            Subgrid.
        """
        sublons, sublats = self.gpi2lonlat(gpis)

        return BasicGrid(sublons, sublats, gpis)

    def __eq__(self, other):
        """
        Compare arrlon, arrlat, gpis, subsets and shape.

        Returns
        -------
        result : boolean
            Returns True if grids are equal.
        """
        # only test to certain significance for float variables
        try:
            nptest.assert_allclose(self.arrlon, other.arrlon)
            lonsame = True
        except AssertionError:
            lonsame = False
        try:
            nptest.assert_allclose(self.arrlat, other.arrlat)
            latsame = True
        except AssertionError:
            latsame = False
        gpisame = np.all(self.gpis == other.gpis)
        if self.subset is not None and other.subset is not None:
            subsetsame = np.all(self.subset == other.subset)
        elif self.subset is None and other.subset is None:
            subsetsame = True
        else:
            subsetsame = False

        if self.shape is None and other.shape is None:
            shapesame = True
        elif self.shape is not None and other.shape is not None:
            shapesame = self.shape == other.shape
        else:
            shapesame = False

        return np.all([lonsame, latsame, gpisame, subsetsame, shapesame])


class CellGrid(BasicGrid):

    """
    Grid that has lat,lon coordinates as well as cell informatin. It can find
    nearest neighbour. It can also yield the gpi, lat, lon, cell information
    in cell order. This is important if the data on the grid is saved in cell
    files on disk as we can go through all grid points with optimized
    IO performance.

    Parameters
    ----------
    lon : numpy.ndarray
        Longitudes of the points in the grid.
    lat : numpy.ndarray
        Latitudes of the points in the grid.
    cells : numpy.ndarray
        Of same shape as lon and lat, containing the cell number of each gpi.
    gpis : numpy.ndarray, optional
        If the gpi numbers are in a different order than the lon and lat
        arrays an array containing the gpi numbers can be given.
    subset : numpy.array, optional
        If the active part of the array is only a subset of all the points
        then the subset array which is a index into lon, lat and cells can
        be given here.

    Attributes
    ----------
    arrcell : numpy.ndarray
        Array of cell number with same shape as arrlon, arrlat.
    activearrcell : numpy.ndarray
        Array of longitudes that are active, is defined by arrlon[subset]
        if a subset is given otherwise equal to arrlon.
    """

    def __init__(self, lon, lat, cells, gpis=None, subset=None,
                 setup_kdTree=False, **kwargs):

        super(CellGrid, self).__init__(lon, lat, gpis=gpis, subset=subset,
                                       setup_kdTree=setup_kdTree, **kwargs)

        cells = np.asanyarray(cells)

        if self.arrlon.shape != cells.shape:
            raise GridDefinitionError(
                "lat, lon and cells np.arrays have to have equal shapes")
        self.arrcell = cells

        if subset is not None:
            self.activearrcell = self.arrcell[subset]
        else:
            self.activearrcell = self.arrcell

    def gpi2cell(self, gpi):
        """
        Cell for given gpi.

        Parameters
        ----------
        gpi : int32 or iterable
            Grid point index.

        Returns
        -------
        cell : int or iterable
            Cell number of gpi.
        """
        # check if iterable
        iterable = _element_iterable(gpi)

        gpi = np.atleast_1d(gpi)
        if self.gpidirect:
            cell = self.arrcell[gpi]
        else:
            # get the indices that would sort the gpis
            gpisorted = np.argsort(self.gpis)
            # find the position where the gpis fit in the sorted array
            pos = np.searchsorted(self.gpis[gpisorted], gpi)
            index = gpisorted[pos]
            cell = self.activearrcell[index]

        if not iterable:
            cell = cell[0]

        return cell

    def get_cells(self):
        """
        Function to get all cell numbers of the grid.

        Returns
        -------
        cells : numpy.ndarray
            Unique cell numbers.
        """
        return np.unique(self.activearrcell)

    def get_grid_points(self, *args):
        """
        Returns all active grid points.

        Parameters
        ----------
        n : int, optional
            If the grid is split in n parts using the split function then this
            function will only return the nth part of the grid.

        Returns
        -------
        gpis : numpy.ndarray
            Grid point indices.
        arrlon : numpy.ndarray
            Longitudes.
        arrlat :numpy.ndarray
            Latitudes.
        cells : numpy.ndarray
            Cell numbers.
        """
        if not self.issplit and len(args) == 0:
            return (self.activegpis,
                    self.activearrlon,
                    self.activearrlat,
                    self.activearrcell)

        elif self.issplit and len(args) == 1:
            n = args[0]
            return (self.subgpis[n],
                    self.subarrlons[n],
                    self.subarrlats[n],
                    self.subcells[n])

    def grid_points_for_cell(self, cells):
        """
        Get all grid points for a given cell number.

        Parameters
        ----------
        cell : int, numpy.ndarray
            Cell numbers.

        Returns
        -------
        gpis : numpy.ndarray
            Gpis belonging to cell.
        lons : numpy.array
            Longitudes belonging to the gpis.
        lats : numpy.array
            Latitudes belonging to the gpis.
        """
        cells = np.atleast_1d(cells)

        gpis = []
        lons = []
        lats = []
        for cell in cells:
            cell_index = np.where(cell == self.activearrcell)
            gpis.append(self.activegpis[cell_index])
            lons.append(self.activearrlon[cell_index])
            lats.append(self.activearrlat[cell_index])

        gpis = np.array(gpis)
        lons = np.array(lons)
        lats = np.array(lats)

        return gpis, lons, lats

    def split(self, n):
        """
        Function splits the grid into n parts this changes not function but
        grid_points() which takes the argument n and will only iterate through
        this part of the grid.

        Parameters
        ----------
        n : int
            Number of parts the grid should be split into.
        """
        self.issplit = True
        # sort by cell number to split correctly
        sorted_index = np.argsort(self.activearrcell)
        self.subarrlats = np.array_split(self.activearrlat[sorted_index], n)
        self.subarrlons = np.array_split(self.activearrlon[sorted_index], n)
        self.subgpis = np.array_split(self.activegpis[sorted_index], n)
        self.subcells = np.array_split(self.activearrcell[sorted_index], n)

    def _normal_grid_points(self):
        """
        Yields all grid points in cell order.

        Returns
        -------
        gpi : long
            Grid point index.
        lon : float
            Longitude of gpi.
        lat : float
            Longitude of gpi.
        cell : int
            Cell number.
        """
        uniq_cells = np.unique(self.activearrcell)

        for cell in uniq_cells:
            cell_gpis = np.where(cell == self.activearrcell)[0]
            for gpi in cell_gpis:
                yield self.activegpis[gpi], self.activearrlon[gpi], \
                    self.activearrlat[gpi], cell

    def _split_grid_points(self, n):
        """
        Yields all grid points in cell order.

        Parameters
        ----------
        n : int
            Number of subgrid to yield.

        Returns
        -------
        gpi : long
            Grid point index.
        lon : float
            Longitude of gpi.
        lat : float
            Latitude of gpi.
        cell : int
            Cell number.
        """
        uniq_cells = np.unique(self.subcells[n])

        for cell in uniq_cells:
            cell_gpis = np.where(cell == self.subcells[n])[0]
            for gpi in cell_gpis:
                yield self.subgpis[n][gpi], self.subarrlons[n][gpi], \
                    self.subarrlats[n][gpi], cell

    def subgrid_from_gpis(self, gpis):
        """
        Generate a subgrid for given gpis.

        Parameters
        ----------
        gpis : int, numpy.ndarray
            Grid point indices.

        Returns
        -------
        grid : BasicGrid
            Subgrid.
        """
        sublons, sublats = self.gpi2lonlat(gpis)
        subcells = self.gpi2cell(gpis)

        return CellGrid(sublons, sublats, subcells, gpis)

    def subgrid_from_cells(self, cells):
        """
        Generate a subgrid for given cells.

        Parameters
        ----------
        cells : int, numpy.ndarray
            Cell numbers.

        Returns
        -------
        grid : CellGrid
            Subgrid.
        """
        subgpis, sublons, sublats = self.grid_points_for_cell(cells)
        subcells = self.gpi2cell(subgpis)

        return CellGrid(sublons, sublats, subcells, subgpis)

    def __eq__(self, other):
        """
        Compare cells.

        Returns
        -------
        result : boolean
            Returns true if equal.
        """
        basicsame = super(CellGrid, self).__eq__(other)
        cellsame = np.all(self.arrcell == other.arrcell)
        return np.all([basicsame, cellsame])


def lonlat2cell(lon, lat, cellsize=5., cellsize_lon=None, cellsize_lat=None):
    """
    Partition lon, lat points into cells.

    Parameters
    ----------
    lat: float64, or numpy.ndarray
        Latitude.
    lon: float64, or numpy.ndarray
        Longitude.
    cellsize: float
        Cell size in degrees.
    cellsize_lon : float, optional
        Cell size in degrees on the longitude axis.
    cellsize_lat : float, optional
        Cell size in degrees on the latitude axis.

    Returns
    -------
    cell: int32, or numpy.ndarray
        Cell numbers.
    """
    if cellsize_lon is None:
        cellsize_lon = cellsize
    if cellsize_lat is None:
        cellsize_lat = cellsize
    y = np.clip(np.floor((np.double(lat) +
                          (np.double(90.0) + 1e-9)) / cellsize_lat), 0, 180)
    x = np.clip(np.floor((np.double(lon) + (np.double(180.0) + 1e-9))
                         / cellsize_lon), 0, 360)
    return np.int32(x * (np.double(180.0) / cellsize_lat) + y)


def gridfromdims(londim, latdim):
    """
    Defines new grid object from latitude and longitude dimensions. Latitude
    and longitude dimensions are 1D arrays that give the latitude and
    longitude values of a 2D latitude-longitude array.

    Parameters
    ----------
    londim : numpy.ndarray
        longitude dimension
    latdim : numpy.ndarray
        latitude dimension

    Returns
    -------
    grid : BasicGrid
        New grid object.
    """
    lons, lats = np.meshgrid(londim, latdim)
    return BasicGrid(lons.flatten(), lats.flatten(),
                     shape=(len(londim), len(latdim)))


def genreg_grid(grd_spc_lat=1, grd_spc_lon=1, minlat=-90.0, maxlat=90.0,
                minlon=-180.0, maxlon=180.0):
    """
    Define a global regular lon lat grid which starts in the North Western
    Corner of minlon, maxlat. The grid points are defined to be in the middle
    of a grid cell. e.g. the first point on a 1x1 degree grid with
    minlon -180.0 and maxlat 90.0 will be at -179.5 longitude, 89.5 latitude.

    Parameters
    ----------
    grd_spc_lat: float, optional
        Grid spacing in latitude direction.
    grd_spc_lon: float, optional
        Grid spacing in longitude direction.
    minlat : float, optional
        Minimum latitude of the grid.
    maxlat : float, optional
        Maximum latitude of the grid.
    minlon : float, optional
        Minimum longitude of the grid.
    maxlon : float, optional
        Maximum longitude of the grid.
    """
    lon_dim = np.arange(minlon + grd_spc_lon / 2.0, maxlon, grd_spc_lon)
    lat_dim = np.arange(maxlat - grd_spc_lat / 2.0, minlat, -grd_spc_lat)

    return gridfromdims(lon_dim, lat_dim)


def _element_iterable(el):
    """
    Test if a element is iterable

    Parameters
    ----------
    el: object


    Returns
    -------
    iterable: boolean
       if True then then el is iterable
       if Fales then not
    """
    try:
        el[0]
        iterable = True
    except (TypeError, IndexError):
        iterable = False

    return iterable
