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


import unittest
import numpy as np
import numpy.testing as nptest
from netCDF4 import Dataset

from pygeogrids.geodetic_datum import GeodeticDatum
import pygeogrids.netcdf as grid_nc
import pygeogrids as grids
import tempfile


class Test(unittest.TestCase):

    def setUp(self):
        lat, lon = np.arange(180) - 90, np.arange(360) - 180
        self.lats, self.lons = np.meshgrid(lat, lon)
        self.lats, self.lons = self.lats.flatten(), self.lons.flatten()
        self.cells = grids.lonlat2cell(self.lons, self.lats)
        self.subset = np.sort(np.random.choice(np.arange(self.lats.size),
                                               size=500, replace=False))
        self.basic = grids.BasicGrid(self.lons, self.lats, subset=self.subset,
                                     shape=(180, 360))

        self.basic_shape_gpis = grids.BasicGrid(self.lons, self.lats,
                                                gpis=np.arange(self.lats.size),
                                                subset=self.subset,
                                                shape=(180, 360))
        self.basic_generated = grids.genreg_grid(1, 1)
        self.basic_irregular = grids.BasicGrid(np.random.random(360 * 180) * 360 - 180,
                                               np.random.random(
                                                   360 * 180) * 180 - 90,
                                               subset=self.subset)
        self.cellgrid = grids.CellGrid(self.lons, self.lats, self.cells,
                                       subset=self.subset)

        self.cellgrid_shape = grids.CellGrid(self.lons, self.lats, self.cells,
                                             subset=self.subset,
                                             shape=(180, 360))

        self.testfile = tempfile.NamedTemporaryFile().name

    def tearDown(self):
        pass

    def test_save_lonlat_nc(self):
        grid_nc.save_lonlat(self.testfile,
                            self.lons, self.lats,
                            GeodeticDatum('WGS84'),
                            self.cells,
                            subsets={'subset_flag': {'points': self.subset,
                                                     'value': 1.,
                                                     'meaning': 'test_flag'}},
                            global_attrs={'test': 'test_attribute'})

        with Dataset(self.testfile) as nc_data:
            nptest.assert_array_equal(self.lats, nc_data.variables['lat'][:])
            nptest.assert_array_equal(self.lons, nc_data.variables['lon'][:])
            nptest.assert_array_equal(self.cells, nc_data.variables['cell'][:])
            nptest.assert_array_equal(
                self.subset, np.where(nc_data.variables['subset_flag'][:] == 1)[0])
            assert nc_data.test == 'test_attribute'

    def test_save_basicgrid_generated(self):
        grid_nc.save_grid(self.testfile,
                          self.basic,
                          global_attrs={'test': 'test_attribute'})

        with Dataset(self.testfile) as nc_data:
            nptest.assert_array_equal(np.unique(self.lats)[::-1],
                                      nc_data.variables['lat'][:])
            nptest.assert_array_equal(np.unique(self.lons),
                                      nc_data.variables['lon'][:])

            # subsets have to identify the same gpis in the original grid and
            # the stored one.
            stored_subset = np.where(nc_data.variables['subset_flag'][
                                     :].flatten() == 1)[0]
            nptest.assert_array_equal(sorted(self.basic.gpis[self.subset]),
                                      sorted(nc_data.variables['gpi'][:].flatten()[stored_subset]))
            assert nc_data.test == 'test_attribute'
            assert nc_data.shape[0] == 180
            assert nc_data.shape[1] == 360

    def test_save_basicgrid_irregular_nc(self):
        grid_nc.save_grid(self.testfile,
                          self.basic_irregular,
                          global_attrs={'test': 'test_attribute'})

        with Dataset(self.testfile) as nc_data:
            nptest.assert_array_equal(
                self.basic_irregular.arrlat, nc_data.variables['lat'][:])
            nptest.assert_array_equal(
                self.basic_irregular.arrlon, nc_data.variables['lon'][:])
            nptest.assert_array_equal(self.subset,
                                      np.where(nc_data.variables['subset_flag'][:] == 1)[0])
            assert nc_data.test == 'test_attribute'
            assert nc_data.shape == 64800

    def test_save_cellgrid_nc(self):
        grid_nc.save_grid(self.testfile,
                          self.cellgrid,
                          global_attrs={'test': 'test_attribute'})

        with Dataset(self.testfile) as nc_data:
            nptest.assert_array_equal(self.lats, nc_data.variables['lat'][:])
            nptest.assert_array_equal(self.lons, nc_data.variables['lon'][:])
            nptest.assert_array_equal(self.cells, nc_data.variables['cell'][:])
            nptest.assert_array_equal(
                self.subset, np.where(nc_data.variables['subset_flag'][:] == 1)[0])
            assert nc_data.test == 'test_attribute'

    def test_save_load_basicgrid(self):
        grid_nc.save_grid(self.testfile,
                          self.basic)

        loaded_grid = grid_nc.load_grid(self.testfile)
        assert self.basic == loaded_grid

    def test_save_load_basicgrid_shape_gpis(self):
        grid_nc.save_grid(self.testfile,
                          self.basic_shape_gpis)

        loaded_grid = grid_nc.load_grid(self.testfile)
        assert self.basic_shape_gpis == loaded_grid

    def test_save_load_basicgrid_irregular(self):
        grid_nc.save_grid(self.testfile,
                          self.basic_irregular)

        loaded_grid = grid_nc.load_grid(self.testfile)
        assert self.basic_irregular == loaded_grid

    def test_save_load_cellgrid(self):
        grid_nc.save_grid(self.testfile,
                          self.cellgrid)

        loaded_grid = grid_nc.load_grid(self.testfile)
        assert self.cellgrid == loaded_grid

    def test_save_load_cellgrid_shape(self):
        grid_nc.save_grid(self.testfile,
                          self.cellgrid_shape)

        loaded_grid = grid_nc.load_grid(self.testfile)
        assert self.cellgrid_shape == loaded_grid


def test_store_load_regular_2D_grid_custom_gpis():
    """
    Test the storing/loading of a 2D grid when the gpis are in a custom
    ordering.
    """
    londim = np.arange(-180.0, 180.0, 60)
    latdim = np.arange(-90.0, 90.0, 30)
    lons, lats = np.meshgrid(londim, latdim)
    gpis = np.arange(lons.flatten().size).reshape(lons.shape)
    grid = grids.BasicGrid(lons.flatten(), lats.flatten(),
                           gpis.flatten(), shape=lons.shape)
    testfile = tempfile.NamedTemporaryFile().name
    grid_nc.save_grid(testfile, grid)
    grid_loaded = grid_nc.load_grid(testfile)
    assert grid == grid_loaded


def test_store_load_regular_2D_grid():
    """
    Test the storing/loading of a 2D grid when the gpis are in a custom
    ordering.
    """
    londim = np.arange(-180.0, 180.0, 60)
    latdim = np.arange(90.0, -90.0, -30)
    lons, lats = np.meshgrid(londim, latdim)
    gpis = np.arange(lons.flatten().size).reshape(lons.shape)
    grid = grids.BasicGrid(lons.flatten(), lats.flatten(),
                           gpis.flatten(), shape=lons.shape)
    testfile = tempfile.NamedTemporaryFile().name
    grid_nc.save_grid(testfile, grid)
    grid_loaded = grid_nc.load_grid(testfile)
    assert grid == grid_loaded


def test_sort_lon_lat_for_netcdf_transposed():
    """
    Test the sorting of an array for netcdf storage
    """
    londim = np.arange(-180.0, 180.0, 60)
    latdim = np.arange(90.0, -90.0, -30)
    lats, lons = np.meshgrid(latdim, londim)
    gpis = np.arange(lons.flatten().size).reshape(lons.shape)
    rand_idx = np.random.permutation(gpis.flatten().size)
    lons_rand = lons.flatten()[rand_idx].reshape(lons.shape)
    lats_rand = lats.flatten()[rand_idx].reshape(lats.shape)
    gpis_rand = gpis.flatten()[rand_idx].reshape(gpis.shape)
    lons_sorted, lats_sorted, gpis_sorted = grid_nc.sort_for_netcdf(
        lons_rand, lats_rand, gpis_rand)
    nptest.assert_almost_equal(lons_sorted, lons.T)
    nptest.assert_almost_equal(lats_sorted, lats.T)
    nptest.assert_almost_equal(gpis_sorted, gpis.T)


def test_sort_lon_lat_for_netcdf():
    """
    Test the sorting of an array for netcdf storage
    """
    londim = np.arange(-180.0, 180.0, 60)
    latdim = np.arange(90.0, -90.0, -30)
    lons, lats = np.meshgrid(londim, latdim)
    gpis = np.arange(lons.flatten().size).reshape(lons.shape)
    rand_idx = np.random.permutation(gpis.flatten().size)
    lons_rand = lons.flatten()[rand_idx].reshape(lons.shape)
    lats_rand = lats.flatten()[rand_idx].reshape(lats.shape)
    gpis_rand = gpis.flatten()[rand_idx].reshape(gpis.shape)
    lons_sorted, lats_sorted, gpis_sorted = grid_nc.sort_for_netcdf(
        lons_rand, lats_rand, gpis_rand)
    nptest.assert_almost_equal(lons_sorted, lons)
    nptest.assert_almost_equal(lats_sorted, lats)
    nptest.assert_almost_equal(gpis_sorted, gpis)


if __name__ == "__main__":
    unittest.main()

