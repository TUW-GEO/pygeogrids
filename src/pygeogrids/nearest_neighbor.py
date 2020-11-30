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

import numpy as np

try:
    import pykdtree.kdtree as pykd
    pykdtree_installed = True
except ImportError:
    pykdtree_installed = False

try:
    import scipy.spatial as sc_spat
    scipy_installed = True
except ImportError:
    scipy_installed = False


class findGeoNN(object):

    """
    class that takes lat,lon coordinates, transformes them to cartesian (X,Y,Z)
    coordinates and provides a interface to scipy.spatial.kdTree
    as well as pykdtree if installed

    Parameters
    ----------
    lon : numpy.array or list
        longitudes of the points in the grid
    lat : numpy.array or list
        latitudes of the points in the grid
    geodatum : object
        pygeogrids.geodatic_datum.GeodeticDatum object associated with
        lons/lats coordinates
    grid : boolean, optional
        if True then lon and lat are assumed to be the coordinates of a grid
        and will be used in numpy.meshgrid to get coordinates for all
        grid points
    kd_tree_name : string, optional
        name of kdTree implementation to use, either
        'pykdtree' to use pykdtree or
        'scipy' to use scipy.spatial.kdTree
        Fallback is always scipy if any other string is given
        or if pykdtree is not installed. standard is pykdtree since it is faster

    Attributes
    ----------
    geodatum : object
        pygeogrids.geodatic_datum.GeodeticDatum object used for
        x,y,z  coordinates calculations
    coords : numpy.array
        3D array of cartesian x,y,z coordinates
    kd_tree_name: string
        name of kdTree implementation to use, either
        'pykdtree' to use pykdtree or
        'scipy' to use scipy.spatial.kdTree
        Fallback is always scipy if any other string is given
        or if pykdtree is not installed
    kdtree: object
        kdTree object that is built only once and saved in this attribute

    Methods
    -------
    find_nearest_index(lon,lat)
        finds the nearest neighbor of the given lon,lat coordinates in the lon,lat
        arrays given during initialization and returns the index of the nearest neighbour
        in those arrays.

    """

    def __init__(self, lon, lat, geodatum, grid=False,
                 kd_tree_name='pykdtree'):
        """
        init method, prepares lon and lat arrays for _transform_lonlats if
        necessary

        """
        if grid:
            lon_grid, lat_grid = np.meshgrid(lon, lat)
            lat_init = lat_grid.flatten()
            lon_init = lon_grid.flatten()
            self.lat_size = len(lat)
            self.lon_size = len(lon)
        else:
            if lat.shape != lon.shape:
                raise Exception(
                    "lat and lon np.arrays have to have equal shapes")
            lat_init = lat
            lon_init = lon
        # Earth radius
        self.geodatum = geodatum
        self.kd_tree_name = kd_tree_name
        self.coords = self._transform_lonlats(lon_init, lat_init)
        self.kdtree = None
        self.grid = grid

    def _transform_lonlats(self, lon, lat):
        """
        calculates cartesian 3D coordinates from given lon,lat

        Parameters
        ----------
        lon : numpy.array, list or float
            longitudes of the points in the grid
        lat : numpy.array, list or float
            latitudes of the points in the grid

        Returns
        -------
        coords : np.array
            3D cartesian coordinates
        """
        lon = np.array(lon)
        lat = np.array(lat)
        coords = np.zeros((lon.size, 3), dtype=np.float64)
        (coords[:, 0],
         coords[:, 1],
         coords[:, 2]) = self.geodatum.toECEF(lon, lat)

        return coords

    def _build_kdtree(self):
        """
        Build the kdtree and saves it in the self.kdtree attribute
        """
        if self.kd_tree_name == 'pykdtree' and pykdtree_installed:
            self.kdtree = pykd.KDTree(self.coords)
        elif scipy_installed:
            self.kdtree = sc_spat.cKDTree(self.coords)
        else:
            raise Exception("No supported kdtree implementation installed.\
                             Please install pykdtree or scipy.")

    def find_nearest_index(self, lon, lat, max_dist=np.Inf, k=1):
        """
        finds nearest index, builds kdTree if it does not yet exist

        Parameters
        ----------
        lon : float, list or numpy.array
            longitude of point
        lat : float, list or numpy.array
            latitude of point
        max_dist : float, optional
            Maximum distance to consider for search (default: np.Inf).
        k : int, optional
            The number of nearest neighbors to return (default: 1).

        Returns
        -------
        d : float, numpy.array
            distances of query coordinates to the nearest grid point,
            distance is given in cartesian coordinates and is not the
            great circle distance at the moment. This should be OK for
            most applications that look for the nearest neighbor which
            should not be hundreds of kilometers away.
            If no point was found within the maximum distance to consider, an
            empty array is returned.
        ind : int, numpy.array
            If ``self.grid`` is ``False`` indices of nearest neighbor.
            If no point was found within the maximum distance to consider, an
            empty array is returned.
        index_lon : numpy.array, optional
            If ``self.grid`` is ``True`` then return index into lon array of
            grid definition.
            If no point was found within the maximum distance to consider, an
            empty array is returned.
        index_lat : numpy.array, optional
            If ``self.grid`` is ``True`` then return index into lat array of
            grid definition.
            If no point was found within the maximum distance to consider, an
            empty array is returned.
        """
        if self.kdtree is None:
            self._build_kdtree()

        query_coords = self._transform_lonlats(lon, lat)

        d, ind = self.kdtree.query(
            query_coords, distance_upper_bound=max_dist, k=k)

        # if no point was found, d == inf
        if not np.all(np.isfinite(d)):
            d, ind = np.array([]), np.array([])

        if not self.grid:
            return d, ind
        else:
            # calculate index position in grid definition arrays assuming
            # row-major flattening of arrays after numpy.meshgrid
            index_lat = ind / self.lon_size
            index_lon = ind % self.lon_size
            return d, index_lon.astype(np.int32), index_lat.astype(np.int32)
