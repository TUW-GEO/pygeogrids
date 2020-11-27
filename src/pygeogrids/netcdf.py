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
Module for saving grid to netCDF.
"""

from netCDF4 import Dataset
import numpy as np
import os
from datetime import datetime
from pygeogrids import CellGrid, BasicGrid


def save_lonlat(filename, arrlon, arrlat, geodatum, arrcell=None,
                gpis=None, subsets={}, global_attrs=None,
                format='NETCDF4',
                zlib=False,
                complevel=4,
                shuffle=True):
    """
    saves grid information to netCDF file

    Parameters
    ----------
    filename : string
        name of file
    arrlon : numpy.array
        array of longitudes
    arrlat : numpy.array
        array of latitudes
    geodatum : object
        pygeogrids.geodetic_datum.GeodeticDatum object associated with lon/lat
    arrcell : numpy.array, optional
        array of cell numbers
    gpis : numpy.array, optional
        gpi numbers if not index of arrlon, arrlat
    subsets : dict of dicts, optional
        keys : long_name of the netcdf variables
        values : dict with the following keys: points, meaning
        e.g. subsets = {'subset_flag': {'points': numpy.array,
                                        'value': int,
                                        'meaning': 'water, land'}}
    global_attrs : dict, optional
        if given will be written as global attributs into netCDF file
    format: string, optional
        choose either from one of these NetCDF formats
                        'NETCDF4'
                        'NETCDF4_CLASSIC'
                        'NETCDF3_CLASSIC'
                        'NETCDF3_64BIT_OFFSET'
    zlib: boolean, optional
        see netCDF documentation
    shuffle: boolean, optional
        see netCDF documentation
    complevel: int, opational
        see netCDF documentation
    """

    with Dataset(filename, 'w', format=format) as ncfile:

        if (global_attrs is not None and 'shape' in global_attrs and
                type(global_attrs['shape']) is not int and
                len(global_attrs['shape']) == 2):

            latsize = global_attrs['shape'][0]
            lonsize = global_attrs['shape'][1]
            ncfile.createDimension("lat", latsize)
            ncfile.createDimension("lon", lonsize)
            gpisize = global_attrs['shape'][0] * global_attrs['shape'][1]
            if gpis is None:
                gpivalues = np.arange(gpisize,
                                      dtype=np.int32).reshape(latsize,
                                                              lonsize)
            else:
                gpivalues = gpis.reshape(latsize, lonsize)

            lons = arrlon.reshape(latsize, lonsize)
            lats = arrlat.reshape(latsize, lonsize)
            # sort arrlon, arrlat and gpis
            arrlon_sorted, arrlat_sorted, gpivalues = sort_for_netcdf(
                lons, lats, gpivalues)

            # sorts arrlat descending
            arrlat_store = np.unique(arrlat_sorted)[::-1]
            arrlon_store = np.unique(arrlon_sorted)

        else:
            ncfile.createDimension("gp", arrlon.size)
            gpisize = arrlon.size
            if gpis is None:
                gpivalues = np.arange(arrlon.size, dtype=np.int32)
            else:
                gpivalues = gpis
            arrlon_store = arrlon
            arrlat_store = arrlat

        dim = list(ncfile.dimensions.keys())

        crs = ncfile.createVariable('crs', np.dtype('int32').char,
                                    shuffle=shuffle,
                                    zlib=zlib, complevel=complevel)
        setattr(crs, 'grid_mapping_name', 'latitude_longitude')
        setattr(crs, 'longitude_of_prime_meridian', 0.)
        setattr(crs, 'semi_major_axis', geodatum.geod.a)
        setattr(crs, 'inverse_flattening', 1. / geodatum.geod.f)
        setattr(crs, 'ellipsoid_name', geodatum.name)

        gpi = ncfile.createVariable('gpi', np.dtype('int32').char, dim,
                                    shuffle=shuffle,
                                    zlib=zlib, complevel=complevel)

        if gpis is None:
            gpi[:] = gpivalues
            setattr(gpi, 'long_name', 'Grid point index')
            setattr(gpi, 'units', '')
            setattr(gpi, 'valid_range', [0, gpisize])
            gpidirect = 0x1b
        else:
            gpi[:] = gpivalues
            setattr(gpi, 'long_name', 'Grid point index')
            setattr(gpi, 'units', '')
            setattr(gpi, 'valid_range', [np.min(gpivalues), np.max(gpivalues)])
            gpidirect = 0x0b

        latitude = ncfile.createVariable('lat', np.dtype('float64').char,
                                         dim[0],
                                         shuffle=shuffle,
                                         zlib=zlib, complevel=complevel)
        latitude[:] = arrlat_store
        setattr(latitude, 'long_name', 'Latitude')
        setattr(latitude, 'units', 'degree_north')
        setattr(latitude, 'standard_name', 'latitude')
        setattr(latitude, 'valid_range', [-90.0, 90.0])

        if len(dim) == 2:
            londim = dim[1]
        else:
            londim = dim[0]
        longitude = ncfile.createVariable('lon', np.dtype('float64').char,
                                          londim,
                                          shuffle=shuffle,
                                          zlib=zlib, complevel=complevel)
        longitude[:] = arrlon_store
        setattr(longitude, 'long_name', 'Longitude')
        setattr(longitude, 'units', 'degree_east')
        setattr(longitude, 'standard_name', 'longitude')
        setattr(longitude, 'valid_range', [-180.0, 180.0])

        if arrcell is not None:
            cell = ncfile.createVariable('cell', np.dtype('int16').char,
                                         dim,
                                         shuffle=shuffle,
                                         zlib=zlib, complevel=complevel)

            if len(dim) == 2:
                arrcell = arrcell.reshape(latsize,
                                          lonsize)
                _, _, arrcell = sort_for_netcdf(lons, lats, arrcell)
            cell[:] = arrcell
            setattr(cell, 'long_name', 'Cell')
            setattr(cell, 'units', '')
            setattr(cell, 'valid_range', [np.min(arrcell), np.max(arrcell)])

        if subsets:
            for subset_name in subsets.keys():
                flag = ncfile.createVariable(subset_name, np.dtype('int8').char,
                                             dim,
                                             shuffle=shuffle,
                                             zlib=zlib, complevel=complevel)

                # create flag array based on shape of data
                lf = np.zeros_like(gpivalues)
                if len(dim) == 2:
                    lf = lf.flatten()
                value = subsets[subset_name]['value']
                lf[subsets[subset_name]['points']] = value
                if len(dim) == 2:
                    lf = lf.reshape(latsize, lonsize)
                    _, _, lf = sort_for_netcdf(lons, lats, lf)

                flag[:] = lf
                setattr(flag, 'long_name', subset_name)
                setattr(flag, 'units', '')
                setattr(flag, 'coordinates', 'lat lon')
                setattr(flag, 'flag_values', np.arange(2, dtype=np.int8))
                setattr(flag, 'flag_meanings', subsets[subset_name]['meaning'])
                setattr(flag, 'valid_range', [0, value])

        s = "%Y-%m-%d %H:%M:%S"
        date_created = datetime.now().strftime(s)

        attr = {'Conventions': 'CF-1.6',
                'id': os.path.split(filename)[1],  # file name
                'date_created': date_created,
                'geospatial_lat_min': np.round(np.min(arrlat), 4),
                'geospatial_lat_max': np.round(np.max(arrlat), 4),
                'geospatial_lon_min': np.round(np.min(arrlon), 4),
                'geospatial_lon_max': np.round(np.max(arrlon), 4),
                'gpidirect': gpidirect
                }

        ncfile.setncatts(attr)

        if global_attrs is not None:
            ncfile.setncatts(global_attrs)


def sort_for_netcdf(lons, lats, values):
    """
    Sort an 2D array for storage in a netCDF file.
    This mans that the latitudes are stored from
    90 to -90 and the longitudes from -180 to 180.
    Input arrays have to have shape latdim, londim
    which would mean for a global 10 degree grid (18, 36).

    Parameters
    ----------
    lons: numpy.ndarray
        2D numpy array of longitudes
    lats: numpy.ndarray
        2D numpy array of latitudes
    values: numpy.ndarray
        2D numpy array of values to sort

    Returns
    -------
    lons: numpy.ndarray
        2D numpy array of longitudes, sorted
    lats: numpy.ndarray
        2D numpy array of latitudes, sorted
    values: numpy.ndarray
        2D numpy array of values to sort, sorted
    """

    arrlat = lats.flatten()
    arrlon = lons.flatten()
    arrval = values.flatten()
    idxlatsrt = np.argsort(arrlat)[::-1]
    idxlat = np.argsort(arrlat[idxlatsrt].
                        reshape(lats.shape),
                        axis=0)[::-1]
    idxlon = np.argsort(arrlon[idxlatsrt].
                        reshape(lons.shape)
                        [idxlat, np.arange(lons.shape[1])], axis=1)

    values = arrval[idxlatsrt].reshape(
        *lons.shape)[idxlat, np.arange(lons.shape[1])][np.arange(lons.shape[0])[:, None], idxlon]
    lons = arrlon[idxlatsrt].reshape(
        *lons.shape)[idxlat, np.arange(lons.shape[1])][np.arange(lons.shape[0])[:, None], idxlon]
    lats = arrlat[idxlatsrt].reshape(
        *lons.shape)[idxlat, np.arange(lons.shape[1])][np.arange(lons.shape[0])[:, None], idxlon]
    return lons, lats, values


def save_grid(filename, grid, subset_name='subset_flag', subset_value=1.,
              subset_meaning='water land', global_attrs=None):
    """
    save a BasicGrid or CellGrid to netCDF
    it is assumed that a subset should be used as land_points

    Parameters
    ----------
    filename : string
        name of file
    grid : BasicGrid or CellGrid object
        grid whose definition to save to netCDF
    subset_name : string, optional (default: 'subset_flag')
        long_name of the netcdf variable
        if the subset symbolises something other than a land/sea mask
    subset_value: float, optional (default: 1.)
        Value that that the subgrid is written down as in the file.
    subset_meaning : string, optional (default: 'water land')
        will be written into flag_meanings metadata of variable 'subset_name'
    global_attrs : dict, optional
        if given will be written as global attributes into netCDF file
    """
    try:
        arrcell = grid.arrcell
    except AttributeError:
        arrcell = None

    gpis = grid.gpis

    if grid.shape is not None:
        if global_attrs is None:
            global_attrs = {}
        global_attrs['shape'] = grid.shape

    if grid.subset is not None:
        subsets = {subset_name: {
            'points': grid.subset, 'meaning': subset_meaning, 'value': subset_value}}
    else:
        subsets = None

    save_lonlat(filename, grid.arrlon, grid.arrlat, grid.geodatum,
                arrcell=arrcell, gpis=gpis, subsets=subsets, zlib=True,
                global_attrs=global_attrs)


def load_grid(filename, subset_flag='subset_flag', subset_value=1,
              location_var_name='gpi'):
    """
    load a grid from netCDF file

    Parameters
    ----------
    filename : string
        filename
    subset_flag : string, optional (default: 'subset_flag')
        name of the subset to load.
    subset_value : int or list, optional (default: 1)
        Value(s) of the subset variable that points are loaded for.
    location_var_name: string, optional (default: 'gpi')
        variable name under which the grid point locations
        are stored

    Returns
    -------
    grid : BasicGrid or CellGrid instance
        grid instance initialized with the loaded data
    """

    with Dataset(filename, 'r') as nc_data:
        # determine if it is a cell grid or a basic grid
        arrcell = None
        if 'cell' in nc_data.variables.keys():
            arrcell = nc_data.variables['cell'][:].flatten()

        gpis = nc_data.variables[location_var_name][:].flatten()

        shape = None
        if hasattr(nc_data, 'shape'):
            try:
                shape = tuple(nc_data.shape)
            except TypeError as e:
                try:
                    length = len(nc_data.shape)
                except TypeError:
                    length = nc_data.shape.size
                if length == 1:
                    shape = tuple([nc_data.shape])
                else:
                    raise e

        subset = None
        # some old grid do not have a shape attribute
        # this meant that they had shape of len 1
        if shape is None:
            shape = tuple([len(nc_data.variables['lon'][:])])

        # check if grid has regular shape
        if len(shape) == 2:
            lons, lats = np.meshgrid(nc_data.variables['lon'][:],
                                     nc_data.variables['lat'][:])
            lons = lons.flatten()
            lats = lats.flatten()

            if subset_flag in nc_data.variables.keys():
                subset = np.where(
                    np.isin(nc_data.variables[subset_flag][:].flatten(), subset_value))[0]

        elif len(shape) == 1:
            lons = nc_data.variables['lon'][:]
            lats = nc_data.variables['lat'][:]

            # determine if it has a subset
            if subset_flag in nc_data.variables.keys():
                subset = np.where(
                    np.isin(nc_data.variables[subset_flag][:].flatten(), subset_value))[0]

        if 'crs' in nc_data.variables:
            geodatumName = nc_data.variables['crs'].getncattr('ellipsoid_name')
        else:
            # ellipsoid information is missing, use WGS84 by default
            geodatumName = 'WGS84'

        if arrcell is None:
            # BasicGrid
            return BasicGrid(lons,
                             lats,
                             gpis=gpis,
                             geodatum=geodatumName,
                             subset=subset,
                             shape=shape)
        else:
            # CellGrid
            return CellGrid(lons,
                            lats,
                            arrcell,
                            gpis=gpis,
                            geodatum=geodatumName,
                            subset=subset,
                            shape=shape)
