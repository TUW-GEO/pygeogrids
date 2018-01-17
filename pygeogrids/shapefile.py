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
Module for extracting grid points from global administrative areas
"""

try:
    from osgeo import ogr
    ogr_installed = True
except ImportError:
    ogr_installed = False


def get_gad_grid_points(grid, gadm_shp_path, level, name=None, oid=None):
    """
    Returns all grid points located in a administrative area. For this
    function the files from
    http://biogeo.ucdavis.edu/data/gadm2.8/gadm28_levels.shp.zip
    need to be available in the folder gadm_shp_path
    Optinal as coordinates. Currently only works in WGS84.

    Parameters
    ----------
    grid: object
    gadm_shp_path: path
        Location to GADM28 shapefiles
    level: int
        Global Administrative Database Level
        0 : country
        1 : province/county/state/region/municipality/...
        2 : municipality/District/county/...
    name: str
        name of region at indicated level. For countries the english name
    oid: int
        OBJECTID of feature. This only works with the correct level shp.

    Returns
    -------
    grid : BasicGrid
            Subgrid.

    Raises
    ------
    ValueError: If name or oid are not found in shapefile of given level
    ImportError: If gdal or osgeo are not installed
    """
    if ogr_installed:
        drv = ogr.GetDriverByName('ESRI Shapefile')
        ds_in = drv.Open(gadm_shp_path + 'gadm28_adm{:}.shp'.format(level))
        lyr_in = ds_in.GetLayer(0)
        if name:
            if level == 0:
                lyr_in.SetAttributeFilter("NAME_ENGLI = '%s'" % (name))
            else:
                lyr_in.SetAttributeFilter("NAME_%s = '%s'" % (level, name))

        if oid:
            lyr_in.SetAttributeFilter("OBJECTID = '%s'" % (oid))
        if lyr_in.GetFeatureCount() > 0:
            feature = lyr_in.GetNextFeature()
            ply = feature.GetGeometryRef()
            return grid.get_shp_grid_points(ply)
        else:
            raise ValueError("Requested Object not found in shapefile.")

    else:
        raise ImportError("No supported implementation installed."
                          "Please install gdal and osgeo.")
