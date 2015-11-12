# Copyright (c) 2015,Vienna University of Technology,
#                    Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the <organization> nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


"""
Created on Nov 12, 2015

@author: Christoph Reimer christoph.reimer@geo.tuwien.ac.at
"""


import numpy as np


class GeodaticDatum(object):
    def __init__(self, ell):
        if ell == 'WGS84':
            self.a = 6378137.
            self.b = 6356752.3142
        elif ell == 'GRS80':
            self.a = 6378137.
            self.b = 6356752.3141
        elif ell == 'GEM6':
            self.a = 6378144.
            self.b = 6356759.
        elif ell == 'GEM10B':
            self.a = 6378138.
            self.b = 6356753.2949
        elif ell == 'Bessel':
            self.a = 6377397.155
            self.b = 6356078.96282
        elif ell == 'Sphere':
            self.a = 6371000.
            self.b = 6371000.
        else:
            raise ValueError('Ellipsoid not supported.')

        self.f = (self.a - self.b) / self.a
        self.e = np.sqrt(self.a ** 2 - self.b ** 2) / self.a

    def getParameter(self):
        return self.a, self.b, self.f, self.e

    def CartesianCooridnates(self, lon, lat):
        """
        Method to transform lon/lat to 3d Cartesian coordinates.

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

        lon = np.radians(np.array(lon), dtype=np.float64)
        lat = np.radians(np.array(lat), dtype=np.float64)

        x = (self.a ** 2 * np.cos(lat) * np.cos(lon)) / \
            np.sqrt(self.a ** 2 * np.cos(lat) ** 2 +
                    self.b ** 2 * np.sin(lat) ** 2)
        y = (self.a ** 2 * np.cos(lat) * np.sin(lon)) / \
            np.sqrt(self.a ** 2 * np.cos(lat) ** 2 +
                    self.b ** 2 * np.sin(lat) ** 2)
        z = (self.b ** 2 * np.sin(lat)) / \
            np.sqrt(self.a ** 2 * np.cos(lat) ** 2 +
                    self.b ** 2 * np.sin(lat) ** 2)
        return (x, y, z)

    def ParallelRadi(self, lat):
        x, y, _ = self.getCartesianCooridnates(0., lat)
        return np.sqrt(x ** 2 + y ** 2)

    def GeocentricLat(self, lat):
        return np.rad2deg(np.arctan((1 - self.e ** 2) *
                                    np.tan(np.deg2rad(lat))))

    def GeodeticLat(self, lat):
        return np.rad2deg(np.arctan(np.tan(np.deg2rad(lat)) /
                                    (1 - self.e ** 2)))

    def ReducedLat(self, lat):
        return np.rad2deg(np.arctan(np.sqrt(1 - self.e ** 2) *
                                    np.tan(np.deg2rad(lat))))

    def GeocentricRadi(self, lat):
        lat = np.deg2rad(lat)
        p = self.getParallelRadi(lat)
        geoLat = self.getGeocentricLat(lat)
        return p / np.cos(np.deg2rad(geoLat))

    def EllN(self, lat):
        return self.a / np.sqrt(1 - (self.e ** 2) *
                                (np.sin(np.deg2rad(lat))) ** 2)

    def EllM(self, lat):
        return (self.a * (1 - self.e ** 2)) / \
               ((1 - (self.e ** 2) *
                 (np.sin(np.deg2rad(lat))) ** 2) ** (3. / 2.))

    def GaussianRadi(self, lat):
        N = self.getEllN(lat)
        M = self.getEllM(lat)
        return np.sqrt(M * N)

    def ParallelArcDist(self, lat, lon1, lon2):
        lat = np.deg2rad(lat)
        lon1 = np.deg2rad(lon1)
        lon2 = np.deg2rad(lon2)
        return self.getEllN(lat) * np.cos(lat) * (lon2 - lon1)

    def MeridianArcDist(self, lat1, lat2):
        latMid = (lat2 + lat1) / 2
        # r_gaus = self.getGaussianRadi(latMid)
        return np.deg2rad(lat2 - lat1) * self.getEllM(latMid)