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
import pyproj


class GeodeticDatum():
    """
    Class representing a geodetic datum providing transformation and
    calculation functionality

    Parameters
    ----------
    ellString : string
        String of geodetic datum (ellipsoid) as provided in pyproj

    """

    def __init__(self, ellps, **kwargs):
        kwargs['ellps'] = ellps
        self.geod = pyproj.Geod(**kwargs)
        self.geod.e = np.sqrt(self.geod.es)
        self.name = ellps

    def getParameter(self):
        """
        Method to transform lon/lat to ECEF (Earth-Centered, Earth-Fixed)
        coordinates representing a 3d Cartesian coordinate system.

        Parameters
        ----------
        lon : numpy.array, list or float
            longitudes of the points in the grid
        lat : numpy.array, list or float
            latitudes of the points in the grid

        Returns
        -------
        x, y, z : np.array
            3D cartesian coordinates
        """
        return self.geod.a, self.geod.b, self.geod.f, self.geod.e

    def toECEF(self, lon, lat):
        """
        Method to transform lon/lat to ECEF (Earth-Centered, Earth-Fixed)
        coordinates representing a 3d Cartesian coordinate system.

        Parameters
        ----------
        lon : numpy.array, list or float
            longitudes of the points in the grid
        lat : numpy.array, list or float
            geodatic latitudes of the points in the grid

        Returns
        -------
        x, y, z : np.array
            3D cartesian coordinates
        """
        if _element_iterable(lat) and lat.shape == lon.shape:
            lat = np.array(lat, dtype=np.float64)
            lon = np.array(lon, dtype=np.float64)

        N = self.EllN(lat)
        lon = np.deg2rad(lon)
        lat = np.deg2rad(lat)

        x = N * np.cos(lat) * np.cos(lon)
        y = N * np.cos(lat) * np.sin(lon)
        z = N * (1 - self.geod.es) * np.sin(lat)

        return x, y, z

    def ParallelRadi(self, lat):
        """
        Method to get the radius the parallel at a given latitude.

        Parameters
        ----------
        lat : numpy.array, list or float
            latitudes of the points in the grid

        Returns
        -------
        radius : np.array, float
            Radius of parallel
        """
        x, y, _ = self.toECEF(0., lat)
        return np.sqrt(x ** 2 + y ** 2)

    def GeocentricLat(self, lat):
        """
        Method to calculate the geocentric from the geodatic latitude.

        Parameters
        ----------
        lat : numpy.array, list or float
            Geodatic latitudes of the points in the grid

        Returns
        -------
        lat_geocentric : np.array, float
            Geocentric latitude
        """
        if _element_iterable(lat):
            lat = np.array(lat, dtype=np.float64)

        return np.rad2deg(np.arctan((1 - self.geod.e ** 2) *
                                    np.tan(np.deg2rad(lat))))

    def GeodeticLat(self, lat):
        """
        Method to calculate the geodatic from the geocentric latitude.

        Parameters
        ----------
        lat : numpy.array, list or float
            Geocentric latitudes of the points in the grid

        Returns
        -------
        lat_geodatic : np.array, float
            Geodatic latitude
        """
        if _element_iterable(lat):
            lat = np.array(lat, dtype=np.float64)
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(lat)) /
                                    (1 - self.geod.e ** 2)))

    def ReducedLat(self, lat):
        """
        Method to calculate the reduced from the geodatic latitude.

        Parameters
        ----------
        lat : numpy.array, list or float
            Geodatic latitudes of the points in the grid

        Returns
        -------
        lat_reduced : np.array, float
            Reduced latitude
        """
        if _element_iterable(lat):
            lat = np.array(lat, dtype=np.float64)
        return np.rad2deg(np.arctan(np.sqrt(1 - self.geod.e ** 2) *
                                    np.tan(np.deg2rad(lat))))

    def GeocentricDistance(self, lon, lat):
        """
        Method to calculate the geocentric distance to given points

        Parameters
        ----------
        lon : numpy.array, list or float
            Geodatic longitude of the points in the grid
        lat : numpy.array, list or float
            Geodatic latitudes of the points in the grid

        Returns
        -------
        r : np.array, float
            Geocentric radius
        """
        x, y, z = self.toECEF(lon, lat)
        return np.sqrt(x**2 + y**2 + z**2)

    def EllN(self, lat):
        """
        Method to calculate the radius of the prime vertical

        Parameters
        ----------
        lat : numpy.array, list or float
            Geodatic latitudes of the points in the grid in degrees

        Returns
        -------
        r : np.array, float
            radius of the prime vertical
        """

        if _element_iterable(lat):
            lat = np.array(lat, dtype=np.float64)
        return self.geod.a / np.sqrt(1 - (self.geod.es) *
                                     (np.sin(np.deg2rad(lat))) ** 2)

    def EllM(self, lat):
        """
        Method to calculate the radius of the curvature

        Parameters
        ----------
        lat : numpy.array, list or float
            Geodatic latitudes of the points in the grid

        Returns
        -------
        r : np.array, float
            radius of the curvature
        """
        if _element_iterable(lat):
            lat = np.array(lat, dtype=np.float64)
        return (self.geod.a * (1 - self.geod.es)) / \
               ((1 - self.geod.es) *
                (np.sin(np.deg2rad(lat)) ** 2) ** (3. / 2.))

    def GaussianRadi(self, lat):
        """
        Method to calculate the gaussian radius of the curvature

        Parameters
        ----------
        lat : numpy.array, list or float
            Geodatic latitudes of the points in the grid

        Returns
        -------
        r : np.array, float
            gaussian radius of the curvature
        """
        if _element_iterable(lat):
            lat = np.array(lat, dtype=np.float64)
        N = self.EllN(lat)
        M = self.EllM(lat)
        return np.sqrt(M * N)

    def ParallelArcDist(self, lat, lon1, lon2):
        """
        Method to calculate the distance between two points on a given parallel

        Parameters
        ----------
        lat : float
            Geodatic latitudes of the points in the grid
        lon1 : float
            Longitude of point 1 at the given parallel
        lon2 : float
            Longitude of point 2 at the given parallel

        Returns
        -------
        dist : np.array, float
            Parallel arc distance
        """
        lon1 = np.deg2rad(lon1)
        lon2 = np.deg2rad(lon2)
        return self.EllN(lat) * np.cos(np.deg2rad(lat)) * (lon2 - lon1)

    def MeridianArcDist(self, lat1, lat2):
        """
        Method to calculate the distance between two parallels (meridian arc
        distance)

        Parameters
        ----------
        lat1 : numpy.array, float
            Geodatic latitudes 1
        lat2 : numpy.array, float
            Geodatic latitudes 2

        Returns
        -------
        dist : np.array, float
            Meridian arc distance
        """
        if _element_iterable(lat1) and lat1.shape == lat2.shape:
            lat1 = np.array(lat1, dtype=np.float64)
            lat2 = np.array(lat2, dtype=np.float64)
        fazi, bazi, dist = self.geod.inv(0., lat1, 0., lat2)
        return dist


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
