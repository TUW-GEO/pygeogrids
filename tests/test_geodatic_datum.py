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
import numpy.testing as nptest
import numpy as np
from pygeogrids.geodetic_datum import GeodeticDatum


class test_GeodaticDatum(unittest.TestCase):

    def setUp(self):
        self.datum = GeodeticDatum('WGS84')

    def test_toECEF(self):
        x, y, z = self.datum.toECEF(0, 90)
        nptest.assert_almost_equal(np.array([0, 0, self.datum.geod.b]),
                                   np.array([x, y, z]),
                                   decimal=5)

        x, y, z = self.datum.toECEF(0, 0)
        nptest.assert_almost_equal(np.array([self.datum.geod.a, 0, 0]),
                                   np.array([x, y, z]),
                                   decimal=5)

    def test_ParallelRadi(self):
        r = self.datum.ParallelRadi(0.)
        nptest.assert_almost_equal(r, self.datum.geod.a, decimal=5)

        r = self.datum.ParallelRadi(90.)
        nptest.assert_almost_equal(r, 0., decimal=5)

    def test_GeocentricDistance(self):
        r = self.datum.GeocentricDistance(0., 0.)
        nptest.assert_almost_equal(r, self.datum.geod.a, decimal=5)

        r = self.datum.GeocentricDistance(0., 90.)
        nptest.assert_almost_equal(r, self.datum.geod.b, decimal=5)

    def test_ParallelArcDist(self):
        dist = self.datum.ParallelArcDist(0., 0., 360.)
        nptest.assert_almost_equal(dist, self.datum.geod.a * 2 * np.pi)

        lat, lon1, lon2 = 45., -5., 5.
        __, __, great_circle_dist = self.datum.geod.inv(lon1, lat, lon2, lat)
        parallel_dist = self.datum.ParallelArcDist(lat, lon1, lon2)

        assert great_circle_dist < parallel_dist, \
            (great_circle_dist, parallel_dist)


if __name__ == "__main__":
    unittest.main()
