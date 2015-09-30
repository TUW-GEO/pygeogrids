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

# created on Mar 26, 2014
# author: Christoph Paulik Christoph.Paulik@geo.tuwien.ac.at

"""
Testing grid functionality.
"""

import unittest
import numpy.testing as nptest
import numpy as np

from pygeogrids.grids import lonlat2cell
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
                                    shape=(len(self.londim),
                                           len(self.latdim)))
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
            orig_gpis, orig_lons, orig_lats = \
                self.cellgrid.grid_points_for_cell(cell)
            nptest.assert_equal(gpis, orig_gpis)
            nptest.assert_equal(lons, orig_lons)
            nptest.assert_equal(lats, orig_lats)

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
                                    shape=(len(self.londim),
                                           len(self.latdim)))

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
                                               shape=(len(self.londim),
                                                      len(self.latdim)),
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
    assert grid.shape == (360, 180)
    lon, lat = grid.gpi2lonlat(3)
    assert lon == -176.5
    assert lat == 89.5


if __name__ == "__main__":
    unittest.main()
