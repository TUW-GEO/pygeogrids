'''
Created on Mar 26, 2014

@author: Christoph Paulik christoph.paulik@geo.tuwien.ac.at
'''
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
        setup grid with unequal cell size along lat and lon
        and test if the correct number of points lay in each cell
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


class TestCellGrid(unittest.TestCase):

    """
    setup simple 2D grid 2.5 degree global grid (144x72)
    which starts at the North Western corner of 90 -180
    Test for cell specific features
    """

    def setUp(self):
        self.latdim = np.arange(90, -90, -2.5)
        self.londim = np.arange(-180, 180, 2.5)
        self.lon, self.lat = np.meshgrid(self.londim, self.latdim)
        self.grid = grids.BasicGrid(
            self.lon.flatten(), self.lat.flatten(), shape=(len(self.londim), len(self.latdim)))
        self.cellgrid = self.grid.to_cell_grid()

    def test_gpi2cell(self):
        """
        test if gpi to row column lookup works correctly
        """
        gpi = 200
        cell = self.cellgrid.gpi2cell(gpi)
        assert cell == 1043

    def test_gpi2cell_iterable(self):
        """
        test if gpi to row column lookup works correctly
        """
        gpi = [200, 255]
        cell = self.cellgrid.gpi2cell(gpi)
        assert np.all(cell == [1043, 2015])

    def test_gpi2cell_custom_gpis(self):
        """
        test if gpi to row column lookup works correctly
        """
        self.custom_gpi_grid = grids.BasicGrid(self.lon.flatten(),
                                               self.lat.flatten(),
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


class Test_2Dgrid(unittest.TestCase):

    """
    setup simple 2D grid 2.5 degree global grid (144x72)
    which starts at the North Western corner of 90 -180
    and test 2D lookup
    """

    def setUp(self):
        self.latdim = np.arange(90, -90, -2.5)
        self.londim = np.arange(-180, 180, 2.5)
        self.lon, self.lat = np.meshgrid(self.londim, self.latdim)
        self.grid = grids.BasicGrid(
            self.lon.flatten(), self.lat.flatten(), shape=(len(self.londim), len(self.latdim)))

    def test_gpi2rowcol(self):
        """
        test if gpi to row column lookup works correctly
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
        test if gpi to row column lookup works correctly
        """
        gpi = [200, 255]
        row_should = [1, 1]
        column_should = [200 - 144, 255 - 144]
        row, column = self.grid.gpi2rowcol(gpi)
        assert np.all(row == row_should)
        assert np.all(column == column_should)

    def test_gpi2rowcol_custom_gpis(self):
        """
        test if gpi to row column lookup works correctly
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
        test if gpi to longitude latitude lookup works correctly
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
    test generation of regular grids
    """
    grid = grids.genreg_grid()
    assert grid.shape == (360, 180)
    lon, lat = grid.gpi2lonlat(3)
    assert lon == -176.5
    assert lat == 89.5


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
