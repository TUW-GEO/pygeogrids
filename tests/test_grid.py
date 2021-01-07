# Copyright (c) 2018, TU Wien, Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of TU Wien, Department of Geodesy and Geoinformation
#      nor the names of its contributors may be used to endorse or promote
#      products derived from this software without specific prior written
#      permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL TU WIEN, DEPARTMENT OF GEODESY AND
# GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Testing grid functionality.
"""

import unittest
import numpy.testing as nptest
import numpy as np
from osgeo import ogr
import pytest
import warnings

from pygeogrids.grids import lonlat2cell, BasicGrid
import pygeogrids as grids


class Test_lonlat2cell(unittest.TestCase):

    def setUp(self):
        lat = np.arange(-90, 90, 2.5)
        lon = np.arange(-180, 180, 2.5)
        self.lons, self.lats = np.meshgrid(lon, lat)

    def testlonlat2cell_hist(self):
        """
        Setup grid with unequal cell size along lat and lon and test if the
        correct number of points lay in each cell.
        """
        cells = lonlat2cell(
            self.lons, self.lats, cellsize_lon=15, cellsize_lat=30)
        hist, bin_edges = np.histogram(
            cells.flatten(), bins=len(np.unique(cells)))
        nptest.assert_allclose(hist, np.zeros_like(hist) + 72)

    def testlonlat2cell_edge(self):
        """
        Use points on the 180 degree longitude and see if they fall into
        the correct cell
        """
        lats = [69.8242, 69.122, 68.42]
        lons = [180, 180, 180]
        cells = lonlat2cell(lons, lats)
        assert list(cells) == [31, 31, 31]


class TestFindNearestNeighbor(unittest.TestCase):

    def setUp(self):
        self.grid = grids.genreg_grid(1, 1)

    def test_nearest_neighbor(self):
        gpi, dist = self.grid.find_nearest_gpi(14.3, 18.5)
        assert gpi == 25754
        assert len([dist]) == 1
        lon, lat = self.grid.gpi2lonlat(gpi)
        assert lon == 14.5
        assert lat == 18.5

    def test_nearest_neighbor_list(self):
        gpi, dist = self.grid.find_nearest_gpi([145.1, 90.2], [45.8, -16.3])
        assert len(gpi) == 2
        assert len(dist) == 2
        assert gpi[0] == 16165
        assert gpi[1] == 38430
        lon, lat = self.grid.gpi2lonlat(gpi)
        assert lon[0] == 145.5
        assert lon[1] == 90.5
        assert lat[0] == 45.5
        assert lat[1] == -16.5

    def test_nearest_neighbor_ndarray(self):
        gpi, dist = self.grid.find_nearest_gpi(
            np.array([145.1, 90.2]), np.array([45.8, -16.3]))
        assert len(gpi) == 2
        assert len(dist) == 2
        assert gpi[0] == 16165
        assert gpi[1] == 38430
        lon, lat = self.grid.gpi2lonlat(gpi)
        assert lon[0] == 145.5
        assert lon[1] == 90.5
        assert lat[0] == 45.5
        assert lat[1] == -16.5

    def test_nearest_neighbor_numpy_single(self):
        gpi, dist = self.grid.find_nearest_gpi(
            np.array([145.1, 90.2])[0], np.array([45.8, -16.3])[0])
        assert gpi == 16165
        lon, lat = self.grid.gpi2lonlat(gpi)
        assert lon == 145.5
        assert lat == 45.5

    def test_k_nearest_neighbor(self):
        gpi, dist = self.grid.find_k_nearest_gpi(14.3, 18.5, k=2)
        assert gpi[0, 0] == 25754
        assert gpi[0, 1] == 25753
        assert dist.shape == (1, 2)
        lon, lat = self.grid.gpi2lonlat(gpi[0, 0])
        assert lon == 14.5
        assert lat == 18.5
        lon, lat = self.grid.gpi2lonlat(gpi[0, 1])
        assert lon == 13.5
        assert lat == 18.5

    def test_k_nearest_neighbor_list(self):
        gpi, dist = self.grid.find_k_nearest_gpi(
            [145.1, 90.2], [45.8, -16.3], k=2)
        assert gpi.shape == (2, 2)
        assert dist.shape == (2, 2)
        assert gpi[0, 0] == 16165
        assert gpi[0, 1] == 16164
        assert gpi[1, 0] == 38430
        assert gpi[1, 1] == 38429

    def test_nearest_neighbor_max_dist(self):
        # test with maxdist higher than nearest point
        gpi, dist = self.grid.find_nearest_gpi(14.3, 18.5, max_dist=100e3)
        assert gpi == 25754
        assert len([dist]) == 1
        lon, lat = self.grid.gpi2lonlat(gpi)
        assert lon == 14.5
        assert lat == 18.5

        # test with maxdist lower than nearest point
        gpi, dist = self.grid.find_nearest_gpi(14.3, 18.5, max_dist=10e3)
        assert len(gpi) == 0
        assert len(dist) == 0

        # test with custom gpi, see issue #68
        grid = grids.BasicGrid(lon=[16,17], lat=[45,46], gpis=[100,200])
        gpi, dist = grid.find_nearest_gpi(0,0, max_dist=1000)
        assert len(gpi) == 0
        assert len(dist) == 0
                                                

class TestCellGridNotGpiDirect(unittest.TestCase):

    """
    Setup simple 2D grid 2.5 degree global grid (144x72) which starts at the
    North Western corner of 90 -180 Test for cell specific features.
    """

    def setUp(self):
        self.latdim = np.arange(90, -90, -2.5)
        self.londim = np.arange(-180, 180, 2.5)
        self.lon, self.lat = np.meshgrid(self.londim, self.latdim)
        self.grid = grids.BasicGrid(self.lon.flatten(), self.lat.flatten(),
                                    gpis=np.arange(self.lon.flatten().size),
                                    shape=(len(self.latdim),
                                           len(self.londim)))
        self.reverse_gpi_grid = grids.BasicGrid(
            self.lon.flatten(), self.lat.flatten(),
            gpis=np.arange(self.lon.flatten().size)[::-1],
            shape=(len(self.latdim),
                   len(self.londim)))
        self.cellgrid = self.grid.to_cell_grid()

    def test_gpi2cell(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        gpi = 200
        cell = self.cellgrid.gpi2cell(gpi)
        assert cell == 1043

    def test_gpi2cell_iterable(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        gpi = [200, 255]
        cell = self.cellgrid.gpi2cell(gpi)
        assert np.all(cell == [1043, 2015])

    def test_gpi2cell_numpy(self):
        """
        test if gpi to cell lookup works correctly
        """
        gpi = np.array([200, 255])
        cell = self.cellgrid.gpi2cell(gpi)
        assert np.all(cell == [1043, 2015])

    def test_gpi2cell_numpy_single(self):
        """
        test if gpi to row column lookup works correctly
        """
        gpi = np.array([200, 255])[0]
        cell = self.cellgrid.gpi2cell(gpi)
        assert cell == 1043

    def test_calc_lut(self):
        """
        Test calcuation of lookuptable into reverse gpi grid.
        This must result in a lookuptable that reverses the gpis.
        """
        lut = self.grid.calc_lut(self.reverse_gpi_grid)
        nptest.assert_allclose(lut[::-1], self.grid.gpis)

    def test_gpi2cell_custom_gpis(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        self.custom_gpi_grid = \
            grids.BasicGrid(self.lon.flatten(), self.lat.flatten(),
                            shape=(len(self.latdim),
                                   len(self.londim)),
                            gpis=np.arange(len(self.lat.flatten()))[::-1])
        self.custom_gpi_cell_grid = self.custom_gpi_grid.to_cell_grid()
        gpi = [200, 255]
        cell = self.custom_gpi_cell_grid.gpi2cell(gpi)
        assert np.all(cell == [1549, 577])
        gpi = 200
        cell = self.custom_gpi_cell_grid.gpi2cell(gpi)
        assert cell == 1549

    def test_subgrid_from_cells(self):
        """
        Test subgrid selection.
        """
        cells = [1549, 577]
        subgrid = self.cellgrid.subgrid_from_cells(cells)
        assert type(subgrid) == type(self.cellgrid)

        for cell in cells:
            gpis, lons, lats = subgrid.grid_points_for_cell(cell)
            cell_index = np.where(cell == self.cellgrid.activearrcell)
            orig_gpis = self.cellgrid.activegpis[cell_index]
            orig_lons = self.cellgrid.activearrlon[cell_index]
            orig_lats = self.cellgrid.activearrlat[cell_index]
            nptest.assert_array_equal(gpis, orig_gpis)
            nptest.assert_array_equal(lons, orig_lons)
            nptest.assert_array_equal(lats, orig_lats)

    def test_subgrid_from_gpis(self):
        """
        Test subgrid selection.
        """
        gpis = [200, 255]
        subgrid = self.cellgrid.subgrid_from_gpis(gpis)
        assert type(subgrid) == type(self.cellgrid)
        lons_should, lats_should = self.cellgrid.gpi2lonlat(gpis)
        cells_should = self.cellgrid.gpi2cell(gpis)
        subgrid_should = grids.CellGrid(
            lons_should, lats_should, cells_should, gpis=gpis)
        assert subgrid == subgrid_should


class TestLutCalculation(unittest.TestCase):

    def setUp(self):
        """
        Setup two grids with similar gpis but with different subset/gpi ordering.
        The lookup tables should still give the correct results.
        The gpi's of the two grids are identical.
        """
        self.lats = np.array([1, 2, 3, 4])
        self.lons = np.array([1, 2, 3, 4])
        self.gpis = [0, 1, 2, 3]
        self.subset = [3, 2]
        self.lats2 = np.array([3, 4, 2, 1])
        self.lons2 = np.array([3, 4, 2, 1])
        self.gpis2 = [2, 3, 1, 0]
        self.subset2 = [0, 1]
        self.grid1 = grids.BasicGrid(self.lons, self.lats, gpis=self.gpis,
                                     subset=self.subset)
        self.grid2 = grids.BasicGrid(self.lons2, self.lats2, gpis=self.gpis2,
                                     subset=self.subset2)

    def test_calc_lut(self):
        lut = self.grid1.calc_lut(self.grid2)
        nptest.assert_array_equal(lut, [-1, -1, 2, 3])
        nptest.assert_array_equal(
            lut[self.grid2.activegpis], self.grid2.activegpis)
        lut2 = self.grid2.calc_lut(self.grid1)
        nptest.assert_array_equal(lut2, [-1, -1, 2, 3])
        nptest.assert_array_equal(
            lut2[self.grid1.activegpis], self.grid1.activegpis)


class TestCellGridNotGpiDirectSubset(unittest.TestCase):

    """Setup simple 2D grid 2.5 degree global grid (144x72) which starts at the
    North Western corner of 90 -180 Test for cell specific features. This grid
    also has a subset with only the first half of points active.
    """

    def setUp(self):
        self.latdim = np.arange(90, -90, -2.5)
        self.londim = np.arange(-180, 180, 2.5)
        self.lon, self.lat = np.meshgrid(self.londim, self.latdim)
        self.grid = grids.BasicGrid(self.lon.flatten(), self.lat.flatten(),
                                    gpis=np.arange(self.lon.flatten().size),
                                    shape=(len(self.londim),
                                           len(self.latdim)),
                                    subset=np.arange(self.lon.flatten().size / 2,
                                                     dtype=np.int))
        self.cellgrid = self.grid.to_cell_grid()

    def test_gpi2cell(self):
        """
        Test if gpi to cell lookup works correctly.
        """
        gpi = 5185
        cell = self.cellgrid.gpi2cell(gpi)
        assert cell == 18

    def test_gpi2cell_iterable(self):
        """
        Test if gpi to cell lookup works correctly.
        """
        gpi = [200, 5185]
        cell = self.cellgrid.gpi2cell(gpi)
        assert np.all(cell == [1043, 18])

    def test_gpi2cell_numpy_single(self):
        """
        test if gpi to cell lookup works correctly
        """
        gpi = np.array([5185, 255])[0]
        cell = self.cellgrid.gpi2cell(gpi)
        assert cell == 18

    def test_gpi2lonlat(self):
        """
        Test if gpi to lon lat lookup works correctly.
        """
        gpi = 5185
        lon, lat = self.cellgrid.gpi2lonlat(gpi)
        assert lon == -177.5
        assert lat == 0.0

    def test_gpi2lonlat_iterable(self):
        """
        Test if gpi to lon lat lookup works correctly.
        """
        gpi = [200, 5185]
        lon, lat = self.cellgrid.gpi2lonlat(gpi)
        assert np.all(lon == [-40.0, -177.5])
        assert np.all(lat == [87.5, 0.0])

    def test_gpi2lonlat_numpy_single(self):
        """
        test if gpi to lon lat lookup works correctly
        """
        gpi = np.array([5185, 255])[0]
        lon, lat = self.cellgrid.gpi2lonlat(gpi)
        assert lon == -177.5
        assert lat == 0.0


class TestCellGrid(unittest.TestCase):

    """
    Setup simple 2D grid 2.5 degree global grid (144x72) which starts at the
    North Western corner of 90 -180 Test for cell specific features.
    """

    def setUp(self):
        self.latdim = np.arange(90, -90, -2.5)
        self.londim = np.arange(-180, 180, 2.5)
        self.lon, self.lat = np.meshgrid(self.londim, self.latdim)
        self.grid = grids.BasicGrid(self.lon.flatten(), self.lat.flatten(),
                                    shape=(len(self.latdim),
                                           len(self.londim)))
        self.cellgrid = self.grid.to_cell_grid()

    def test_gpi2cell(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        gpi = 200
        cell = self.cellgrid.gpi2cell(gpi)
        assert cell == 1043

    def test_gpi2cell_iterable(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        gpi = [200, 255]
        cell = self.cellgrid.gpi2cell(gpi)
        assert np.all(cell == [1043, 2015])

    def test_gpi2cell_numpy_single(self):
        """
        test if gpi to row column lookup works correctly
        """
        gpi = np.array([200, 255])[0]
        cell = self.cellgrid.gpi2cell(gpi)
        assert cell == 1043

    def test_gpi2cell_custom_gpis(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        self.custom_gpi_grid = \
            grids.BasicGrid(self.lon.flatten(), self.lat.flatten(),
                            shape=(len(self.londim),
                                   len(self.latdim)),
                            gpis=np.arange(len(self.lat.flatten()))[::-1])
        self.custom_gpi_cell_grid = self.custom_gpi_grid.to_cell_grid()
        gpi = [200, 255]
        cell = self.custom_gpi_cell_grid.gpi2cell(gpi)
        assert np.all(cell == [1549, 577])
        gpi = 200
        cell = self.custom_gpi_cell_grid.gpi2cell(gpi)
        assert cell == 1549

    def test_subgrid_from_cells(self):
        """
        Test subgrid selection.
        """
        cells = [1549, 577]
        subgrid = self.cellgrid.subgrid_from_cells(cells)
        assert type(subgrid) == type(self.cellgrid)

        for cell in cells:
            gpis, lons, lats = subgrid.grid_points_for_cell(cell)
            cell_index = np.where(cell == self.cellgrid.activearrcell)
            orig_gpis = self.cellgrid.activegpis[cell_index]
            orig_lons = self.cellgrid.activearrlon[cell_index]
            orig_lats = self.cellgrid.activearrlat[cell_index]
            nptest.assert_array_equal(gpis, orig_gpis)
            nptest.assert_array_equal(lons, orig_lons)
            nptest.assert_array_equal(lats, orig_lats)

    def test_subgrid_from_gpis(self):
        """
        Test subgrid selection.
        """
        gpis = [200, 255]
        subgrid = self.cellgrid.subgrid_from_gpis(gpis)
        assert type(subgrid) == type(self.cellgrid)
        lons_should, lats_should = self.cellgrid.gpi2lonlat(gpis)
        cells_should = self.cellgrid.gpi2cell(gpis)
        subgrid_should = grids.CellGrid(
            lons_should, lats_should, cells_should, gpis=gpis)
        assert subgrid == subgrid_should

    def test_get_bbox_grid_points(self):
        gpis = self.cellgrid.get_bbox_grid_points(latmin=-10,
                                                  latmax=-5,
                                                  lonmin=-10,
                                                  lonmax=-5)
        nptest.assert_allclose(gpis,
                               np.array([5684, 5685, 5828, 5829,
                                         5540, 5541, 5686, 5830, 5542]))
        # gpis should come back sorted by cells
        nptest.assert_allclose(self.cellgrid.gpi2cell(gpis),
                               np.array([1240, 1240, 1240, 1240,
                                         1241, 1241, 1276, 1276, 1277]))
        lats, lons = self.cellgrid.get_bbox_grid_points(latmin=-10,
                                                        latmax=-5,
                                                        lonmin=-10,
                                                        lonmax=-5,
                                                        coords=True)
        lats_should = np.array([-7.5, -7.5, -10., -10.,
                                -5., -5., -7.5, -10., -5.])
        lons_should = np.array([-10.,  -7.5, -10.,  -7.5,
                                -10.,  -7.5,  -5.,  -5.,  -5.])
        nptest.assert_allclose(lats,
                               lats_should)
        nptest.assert_allclose(lons,
                               lons_should)
        gpis, lats, lons = self.cellgrid.get_bbox_grid_points(latmin=-10,
                                                              latmax=-5,
                                                              lonmin=-10,
                                                              lonmax=-5,
                                                              both=True)
        lats_should = np.array([-7.5, -7.5, -10., -10.,
                                -5., -5., -7.5, -10., -5.])
        lons_should = np.array([-10.,  -7.5, -10.,  -7.5,
                                -10.,  -7.5,  -5.,  -5.,  -5.])
        nptest.assert_allclose(lats,
                               lats_should)
        nptest.assert_allclose(lons,
                               lons_should)
        nptest.assert_allclose(gpis,
                               np.array([5684, 5685, 5828, 5829,
                                         5540, 5541, 5686, 5830, 5542]))
        # gpis should come back sorted by cells
        nptest.assert_allclose(self.cellgrid.gpi2cell(gpis),
                               np.array([1240, 1240, 1240, 1240,
                                         1241, 1241, 1276, 1276, 1277]))


def test_setup_grid_with_lists():

    grid = grids.BasicGrid([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])

    nptest.assert_allclose(grid.arrlon, np.array([1, 2, 3, 4, 5]))
    nptest.assert_allclose(grid.arrlat, np.array([1, 2, 3, 4, 5]))


def test_setup_cellgrid_with_lists():

    grid = grids.CellGrid([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], [1, 1, 1, 1, 1])

    nptest.assert_allclose(grid.arrlon, np.array([1, 2, 3, 4, 5]))
    nptest.assert_allclose(grid.arrlat, np.array([1, 2, 3, 4, 5]))
    nptest.assert_allclose(grid.arrcell, np.array([1, 1, 1, 1, 1]))


class Test_2Dgrid(unittest.TestCase):

    """
    Setup simple 2D grid 2.5 degree global grid (144x72) which starts at the
    North Western corner of 90 -180 and test 2D lookup.
    """

    def setUp(self):
        self.latdim = np.arange(90, -90, -2.5)
        self.londim = np.arange(-180, 180, 2.5)
        self.lon, self.lat = np.meshgrid(self.londim, self.latdim)
        self.grid = grids.BasicGrid(self.lon.flatten(), self.lat.flatten(),
                                    shape=(len(self.latdim),
                                           len(self.londim)))

    def test_gpi2rowcol(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        gpi = 200
        row_should = 1
        column_should = 200 - 144
        row, column = self.grid.gpi2rowcol(gpi)
        assert row == row_should
        assert column == column_should

    def test_gpi2rowcol_np_int(self):
        """
        test if gpi to row column lookup works correctly
        """
        gpi = np.array([200])[0]
        row_should = 1
        column_should = 200 - 144
        row, column = self.grid.gpi2rowcol(gpi)
        assert row == row_should
        assert column == column_should

    def test_gpi2rowcol_iterable(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        gpi = [143, 200, 255]
        row_should = [0, 1, 1]
        column_should = [143, 200 - 144, 255 - 144]
        row, column = self.grid.gpi2rowcol(gpi)
        assert np.all(row == row_should)
        assert np.all(column == column_should)

    def test_gpi2rowcol_custom_gpis(self):
        """
        Test if gpi to row column lookup works correctly.
        """
        self.custom_gpi_grid = grids.BasicGrid(self.lon.flatten(),
                                               self.lat.flatten(),
                                               shape=(len(self.latdim),
                                                      len(self.londim)),
                                               gpis=np.arange(len(self.lat.flatten()))[::-1])
        gpi = [200, 255]
        row_should = [70, 70]
        column_should = [87, 32]
        row, column = self.custom_gpi_grid.gpi2rowcol(gpi)
        assert np.all(row == row_should)
        assert np.all(column == column_should)

    def test_gpi2lonlat(self):
        """
        Test if gpi to longitude latitude lookup works correctly.
        """
        gpi = 200
        lat_should = 87.5
        lon_should = -180 + (200 - 144) * 2.5
        lon, lat = self.grid.gpi2lonlat(gpi)
        assert lon == lon_should
        assert lat == lat_should

    def test_lonlat2d(self):
        """
        Test if lonlat 2d grids are the same as the grids used for making the grid.
        """
        assert np.all(self.lon == self.grid.lon2d)
        assert np.all(self.lat == self.grid.lat2d)

    def test_tocellgrid(self):
        """
        test if to_cell_grid method works correctly
        """
        cell_grid = self.grid.to_cell_grid()
        result = grids.BasicGrid.__eq__(self.grid, cell_grid)
        assert result


def test_genreggrid():
    """
    Test generation of regular grids.
    """
    grid = grids.genreg_grid()
    assert grid.shape == (180, 360)
    lon, lat = grid.gpi2lonlat(3)
    assert lon == -176.5
    assert lat == 89.5
    lon, lat = grid.gpi2lonlat(360)
    assert lon == -179.5
    assert lat == 88.5


def test_reorder_to_cellsize():
    """
    Test reordering to different cellsize
    """
    lons = np.array([-177, -177, -176, -176])
    lats = np.array([51, 57, 51, 57])
    gpis = np.array([1, 2, 3, 4])
    cells = np.array([14, 14, 14, 14])
    orig_grid = grids.CellGrid(lons, lats, cells, gpis=gpis)
    reordered_grid = grids.reorder_to_cellsize(orig_grid, 5.0, 5.0)
    nptest.assert_almost_equal(reordered_grid.gpis,
                               np.array([1, 3, 2, 4]))
    nptest.assert_almost_equal(reordered_grid.arrlon,
                               np.array([-177, -176, -177, -176]))
    nptest.assert_almost_equal(reordered_grid.arrlat,
                               np.array([51, 51, 57, 57]))
    nptest.assert_almost_equal(reordered_grid.arrcell,
                               np.array([14, 14, 14, 14]))


class Test_ShpGrid(unittest.TestCase):

    def setUp(self):
        """
        Setup grid and shp_file to check if grid points fall in shp.
        """
        lat = np.arange(-90, 90, 1)
        lon = np.arange(-180, 180, 1)
        self.lons, self.lats = np.meshgrid(lon, lat)
        self.grid = grids.BasicGrid(self.lons.flatten(), self.lats.flatten())

        ring = ogr.Geometry(ogr.wkbLinearRing)
        ring.AddPoint(14, 45)
        ring.AddPoint(14, 47)
        ring.AddPoint(16, 47)
        ring.AddPoint(16, 45)
        ring.AddPoint(14, 45)

        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        self.shp = poly

    def test_shpgrid(self):
        '''
        Check if gridpoints fall in polygon.
        '''
        subgrid = self.grid.get_shp_grid_points(self.shp)
        assert subgrid.activearrlon == 15
        assert subgrid.activearrlat == 46


@pytest.mark.filterwarnings("error")
def test_BasicGrid_transform_lon():
    """
    Tests whether transforming longitudes works as expected.
    """

    lat = np.asarray([10, -10, 5, 42])
    lon_pos = np.asarray([0, 90, 180, 270])
    lon_centered = np.asarray([0, 90, 180, -90])

    # case 1: warning and transformation
    with pytest.warns(UserWarning):
        grid = BasicGrid(lon_pos, lat)
        assert np.all(grid.arrlon == lon_centered)

    # case 2: no warning and transform
    grid = BasicGrid(lon_pos, lat, transform_lon=True)
    assert np.all(grid.arrlon == lon_centered)

    # case 3: no warning and no transform
    grid = BasicGrid(lon_pos, lat, transform_lon=False)
    assert np.all(grid.arrlon == lon_pos)



if __name__ == "__main__":
    unittest.main()
