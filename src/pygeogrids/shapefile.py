# Copyright (c) 2022, TU Wien, Department of Geodesy and Geoinformation
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
import os
import numpy as np
from typing import Union, Optional
import pandas as pd
from pygeogrids.grids import CellGrid

try:
    from osgeo import ogr
    ogr_installed = True
except ImportError:
    ogr_installed = False

path_shp_countries = os.path.join(
    os.path.dirname(__file__), 'shapefiles', 'ne_110m_admin_0_countries.shp')

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
        drv = ogr.GetDriverByName("ESRI Shapefile")
        ds_in = drv.Open(os.path.join(gadm_shp_path, f"gadm28_adm{level}.shp"))
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
        raise ImportError("Could not import ogr from osgeo. "
                          "Please install them via `conda install geos gdal` first.")


class ShpReader:
    """
    Wrapper around gdal to read geometries from passed shapefile
    and filter them by fields for certain attributes (e.g. country names).
    NOTE: The default implementation using `fields=None` will load ALL
    available metadata from the shapefile. This can be slow!
    If you know the field that contains the values you want to filter,
    pass it as the `field`, this will also speed up the search.
    """
    def __init__(
            self,
            shp_path: str,
            fields: Optional[Union[list, str]] = None,
            driver: str = 'ESRI Shapefile'
    ):
        """
        Read shp-file and create feature table

        Parameters
        ----------
        shp_path: str
            Path to shapefile
        fields: list[str], str or None
            Shapefile fields to read from attribute table. If None is passed,
            all fields are read.
        driver: str, optional
            Driver to use for reading shapefile. Default is ESRI Shapefile.

        Attributes
        ----------
        features: pd.DataFrame
            Feature table where each row is a polygon in the shp file and
            each column represents a field. Fields contain attributes used
            to filter out the relevant polygons.
        """
        if not ogr_installed:
            raise ImportError("Could not import ogr from osgeo. "
                              "Please install them via `conda install geos gdal` first.")
        self.shp_path = shp_path
        self.driver = driver
        self._init_open_shp()

        self.fields = None if fields is None else np.atleast_1d(fields)
        all_fields = [field.name for field in self.layer.schema]

        if self.fields is None:
            self.fields = all_fields
        else:
            # check each element of fields is in all_fields
            for field in self.fields:
                if field not in all_fields:
                    raise ValueError(f"Field {field} not in shapefile")

        # The feature table contains all geometries in the shp file and
        # their attributes from shp fields as columns.
        # Attributes are used to select relevant features, e.g. countries
        # by name.
        self.features = self._init_build_feature_table()

    def __repr__(self):
        name = self.__class__.__name__
        return f"shp_path: {self.shp_path}\n" \
               f"See `{name}.features` for the full feature table.\n" \
               f"----------------------------------------------------\n" \
               f"{len(self.features.index)} features with Fields: " \
               f"{self.fields}"

    def _init_open_shp(self):
        """
        Open shapefile and get layer
        """
        self.driver = ogr.GetDriverByName(self.driver)
        self.ds = self.driver.Open(self.shp_path)
        self.layer = self.ds.GetLayer()
        self.srs = self.layer.GetSpatialRef()

    def _init_build_feature_table(self):
        """
        Extract names of features in the relevant fields and stores them
        in a pandas dataframe.
        Each row in the data frame refers to the same feature in the shapefile.
        The index is the id under which the feature is found.
        Columns can be used to find the id(s) for a given name.

        Returns
        -------
        df: pd.DataFrame
            Dataframe with feature ids and names for features in passed fields

        """
        ids = []
        features = {}

        for n in range(self.layer.GetFeatureCount()):
            feature = self.layer.GetFeature(n)
            for field in self.fields:
                if field not in features:
                    features[field] = []
                features[field].append(feature.GetField(field))
            ids.append(n)

        return pd.DataFrame(index=ids, data=features)

    def lookup_id(self, names: Union[str, list, np.ndarray]) -> np.ndarray:
        """
        Lookup ids for passed names in passed field
        """
        names = np.atleast_1d(names)
        rows = np.unique(np.where(np.isin(self.features.values, names))[0])
        return self.features.index.values[rows]

    def geom(self, id) -> 'ogr.Geometry':
        """
        Get geometry of feature with passed id
        """
        feature = self.layer.GetFeature(id)
        geom = feature.geometry().Clone()
        return geom

def subgrid_for_shp(grid, values=None, shp_path=path_shp_countries,
                    field=None, shp_driver='ESRI Shapefile',
                    verbose=False):
    """
    Cut grid to selected shape(s) from passed shapefile.

    Parameters
    ----------
    grid: CellGrid
        Grid that should be cut to shape(s) in passed shapefile
    values: np.ndarray or list or None, default: None
        Values in field that are used to select the shape(s) to cut the grid
        to. Usually e.g. a list of country names or continent names.
        The passed values are looked up in all loaded fields, i.e. in all
        columns of the feature table. A polygon is selected if the value
        appears in ANY of the columns (fields) of the feature table.
        If None is passed, all features are used.
    shp_path: str, optional (default: ./shapefiles/ne_10m_admin_0_countries.shp)
        Path to shapefile. By default we use the 110m resolution country
        shape file provided in this package. In theory any shapefile should
        work as long as the structure is the same (the GADM shapefiles
        should work as well).
        For the default shp file it is recommended to filter by the fields
        "NAME" (full country name) and "CONTINENT" (continent name).
        ----------------------------------------------------------------------
        The default file contains the following country names (field: 'NAME'):
        .......................................................................
        'Afghanistan', 'Albania', 'Algeria', 'Angola', 'Antarctica',
        'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan',
        'Bahamas', 'Bangladesh','Belarus', 'Belgium', 'Belize', 'Benin',
        'Bhutan', 'Bolivia', 'Bosnia and Herz.', 'Botswana', 'Brazil',
        'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia',
        'Cameroon', 'Canada', 'Central African Rep.', 'Chad', 'Chile','China',
        'Colombia', 'Congo', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus',
        'Czechia', "Côte d'Ivoire", 'Dem. Rep. Congo', 'Denmark', 'Djibouti',
        'Dominican Rep.', 'Ecuador', 'Egypt', 'El Salvador', 'Eq. Guinea',
        'Eritrea', 'Estonia', 'Ethiopia', 'Falkland Is.', 'Fiji', 'Finland',
        'Fr. S. Antarctic Lands', 'France', 'French Guiana', 'Gabon', 'Gambia',
        'Georgia', 'Germany', 'Ghana', 'Greece', 'Greenland', 'Guatemala',
        'Guinea', 'Guinea-Bissau', 'Guyana', 'Haiti', 'Honduras', 'Hungary',
        'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel',
        'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kosovo',
        'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho',
        'Liberia', 'Libya', 'Lithuania', 'Luxembourg', 'Macedonia',
        'Madagascar', 'Malawi', 'Malaysia', 'Mali', 'Mauritania', 'Mexico',
        'Moldova', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique',
        'Myanmar', 'N. Cyprus', 'Namibia', 'Nepal', 'Netherlands',
        'New Caledonia', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria',
        'North Korea', 'Norway', 'Oman', 'Pakistan', 'Palestine', 'Panama',
        'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland',
        'Portugal', 'Puerto Rico', 'Qatar', 'Romania', 'Russia',
        'Rwanda', 'S. Sudan', 'Saudi Arabia', 'Senegal',
        'Serbia', 'Sierra Leone', 'Slovakia', 'Slovenia', 'Solomon Is.',
        'Somalia', 'Somaliland', 'South Africa', 'South Korea', 'Spain',
        'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
        'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo',
        'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Uganda',
        'Ukraine', 'United Arab Emirates', 'United Kingdom',
        'United States of America', 'Uruguay', 'Uzbekistan', 'Vanuatu',
        'Venezuela', 'Vietnam', 'W. Sahara', 'Yemen', 'Zambia', 'Zimbabwe',
        'eSwatini'
        ----------------------------------------------------------------------
        and the following continent names (field: 'CONTINENT'):
        .......................................................................
        'Africa', 'Antarctica', 'Asia', 'Europe', 'North America', 'Oceania',
        'Seven seas (open ocean)', 'South America'
    field: str or list[str], optional (default: None)
        Shapefile field(s) to use for value search. Each field is a column
        in the feature table. If None is passed, all fields are used (slow).
        Limiting the fields leads to faster lookup times and is recommended
        especially for complex shapefiles.
        For the default countries shp file it is suggested to use the fields:
        "NAME" and "CONTINENT" to search for countries and continents by their
        names.
    shp_driver: str, optional (default: 'ESRI Shapefile')
        Driver to use for reading vector shapefile. Default is ESRI Shapefile.
    verbose: bool, optional (default: False)
        If True, print some information while processing. This also prints
        all available fields and the attribute table after loading the file.

    Returns
    -------
    subgrid: CellGrid
        Subgrid that is cut to the shape(s) in the shapefile
    """
    shp_reader = ShpReader(shp_path, fields=field, driver=shp_driver)

    if verbose:
        print(shp_reader)

    if verbose:
        print("--------------")
        print("Feature table:")
        print(shp_reader.features)

    if values is None:
        ids = shp_reader.features.index.values
    else:
        ids = np.unique(shp_reader.lookup_id(values))

    if len(ids) == 0:
        raise ValueError(f"No features found for {values} in "
                         f"fields {shp_reader.fields}")

    gpis = np.array([], dtype=int)
    for i, id in enumerate(ids):
        if verbose:
            print('Creating subset {} of {} ... to speed this up '
                  'improve pygeogrids.grids.get_shp_grid_points()'.format(
                   i + 1, ids.size))

        subgrid = grid.get_shp_grid_points(shp_reader.geom(id))
        if subgrid is not None:
            poly_gpis = subgrid.activegpis
            gpis = np.append(gpis, poly_gpis)
        else:
            pass

    if gpis.size == 0:
        empty_arr = np.array([])
        return CellGrid(lon=empty_arr, lat=empty_arr, cells=empty_arr)
    else:
        return grid.subgrid_from_gpis(np.unique(gpis))
