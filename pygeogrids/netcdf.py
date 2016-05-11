# Copyright (c) 2013,Vienna University of Technology, Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Vienna University of Technology, Department of Geodesy and Geoinformation nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''
Created on Jan 21, 2014

Module for saving grid to netCDF

@author: Christoph Paulik christoph.paulik@geo.tuwien.ac.at
'''
from netCDF4 import Dataset
import numpy as np
import os
from datetime import datetime
from collections import OrderedDict
from pygeogrids import CellGrid, BasicGrid



def save_lonlat(filename, arrlon, arrlat, geodatum, arrcell=None,
                gpis=None, subsets={}, global_attrs=None, **argv):
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
                                        'meaning': 'water, land'}}
    global_attrs : dict or OderedDict, optional
        if given will be written as global attributs into netCDF file
    **argv['ncformat']: choose either from one of these NetCDF formats
                        'NETCDF4' (default, if ncformat not specified)
                        'NETCDF4_CLASSIC' (default, if ncformat specified)
                        'NETCDF3_CLASSIC'
                        'NETCDF3_64BIT'
    **argv['nccompression']: dictionary of (default):
          {'zlib': False, 'shuffle': True, 'complevel': 4}
    """

    nc_name = filename
    
    if 'ncformat' in argv:
        frmt = argv['ncformat']
        if frmt not in ['NETCDF4','NETCDF4_CLASSIC',
                        'NETCDF3_CLASSIC', 'NETCDF3_64BIT']:
            frmt = 'NETCDF4_CLASSIC'
    else:
        frmt = 'NETCDF4'
    if 'nccompression' in argv:
        nccomp = argv['nccompression']
        if 'zlib' in nccomp:
            nczlib = True if nccomp['zlib'] else False
        else:
            nczlib = False
        if 'ncshuffle' in nccomp:    
            ncshuffle = True if nccomp['shuffle'] else False
        else:
            ncshuffle = True
        if (('complevel' in nccomp) and 
           (isinstance(nccomp['complevel'], (int, long))) and
           ((nccomp['complevel'] >= 1) or (nccomp['complevel'] <= 9))):
            nccomplevel = nccomp['complevel']
        else:
            nccomplevel = 4      
    else:
        nczlib = False
        ncshuffle = True
        nccomplevel = 4
            
    with Dataset(nc_name, 'w', format=frmt) as ncfile:

        if (global_attrs is not None and 'shape' in global_attrs and
                type(global_attrs['shape']) is not int and
                len(global_attrs['shape']) == 2):

            latsize = global_attrs['shape'][1]
            lonsize = global_attrs['shape'][0]
            ncfile.createDimension("lat", latsize)
            ncfile.createDimension("lon", lonsize)

            idxlatsrt = np.argsort(arrlat)[::-1]
            idxlat = np.argsort(arrlat[idxlatsrt].
                                reshape((latsize, lonsize)),
                                axis=0)[::-1]
            idxlon = np.argsort(arrlon[idxlatsrt].
                                reshape((latsize, lonsize))
                                [idxlat, np.arange(lonsize)], axis=1)
            
            gpisize = global_attrs['shape'][0] * global_attrs['shape'][1]
            if gpis is None:
                gpivalues = np.arange(gpisize,
                                      dtype=np.int32).reshape(latsize,
                                                              lonsize)
                gpivalues = gpivalues[::-1]
                
            else:
                gpivalues = gpis[idxlatsrt].reshape(latsize, lonsize)\
                            [idxlat, np.arange(lonsize)]\
                            [np.arange(latsize)[:, None], idxlon]

            arrlat = np.unique(arrlat)[::-1]  # sorts arrlat descending
            arrlon = np.unique(arrlon)
                 
        else:
            ncfile.createDimension("gp", arrlon.size)
            gpisize = arrlon.size
            if gpis is None:
                gpivalues = np.arange(arrlon.size, dtype=np.int32)
            else:
                gpivalues = gpis

        dim = list(ncfile.dimensions.keys())

        crs = ncfile.createVariable('crs', np.dtype('int32').char,
                                    shuffle=ncshuffle,
                                    zlib=nczlib, complevel=nccomplevel)
        setattr(crs, 'grid_mapping_name', 'latitude_longitude')
        setattr(crs, 'longitude_of_prime_meridian', 0.)
        setattr(crs, 'semi_major_axis', geodatum.geod.a)
        setattr(crs, 'inverse_flattening', 1. / geodatum.geod.f)
        setattr(crs, 'ellipsoid_name', geodatum.name)

        gpi = ncfile.createVariable('gpi', np.dtype('int32').char, dim,
                                    shuffle=ncshuffle,
                                    zlib=nczlib, complevel=nccomplevel)

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
                                         shuffle=ncshuffle,
                                         zlib=nczlib, complevel=nccomplevel)
        latitude[:] = arrlat
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
                                          shuffle=ncshuffle,
                                          zlib=nczlib, complevel=nccomplevel)
        longitude[:] = arrlon
        setattr(longitude, 'long_name', 'Longitude')
        setattr(longitude, 'units', 'degree_east')
        setattr(longitude, 'standard_name', 'longitude')
        setattr(longitude, 'valid_range', [-180.0, 180.0])

        if arrcell is not None:
            cell = ncfile.createVariable('cell', np.dtype('int16').char,
                                         dim,
                                         shuffle=ncshuffle,
                                         zlib=nczlib, complevel=nccomplevel)

            if len(dim) == 2:
                arrcell = arrcell[idxlatsrt].reshape(latsize, lonsize)\
                                 [idxlat, np.arange(lonsize)]\
                                 [np.arange(latsize)[:, None], idxlon]
                #arrcell = arrcell.reshape(latsize,
                #                          lonsize)
                
            cell[:] = arrcell
            setattr(cell, 'long_name', 'Cell')
            setattr(cell, 'units', '')
            setattr(cell, 'valid_range', [np.min(arrcell), np.max(arrcell)])

        if subsets:
            for subset_name in subsets.keys():
                flag = ncfile.createVariable(subset_name, np.dtype('int8').char,
                                             dim,
                                             shuffle=ncshuffle,
                                             zlib=nczlib, complevel=nccomplevel)

                # create flag array based on shape of data
                lf = np.zeros_like(gpivalues)
                if len(dim) == 2:
                    lf = lf.flatten()
                lf[subsets[subset_name]['points']] = 1
                if len(dim) == 2:
                    lf = lf[idxlatsrt].reshape(latsize, lonsize)\
                           [idxlat, np.arange(lonsize)]\
                           [np.arange(latsize)[:, None], idxlon]

                flag[:] = lf
                setattr(flag, 'long_name', subset_name)
                setattr(flag, 'units', '')
                setattr(flag, 'coordinates', 'lat lon')
                setattr(flag, 'flag_values', np.arange(2, dtype=np.int8))
                setattr(flag, 'flag_meanings', subsets[subset_name]['meaning'])
                setattr(flag, 'valid_range', [0, 1])

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
        
        if global_attrs is not None and (
                (type(global_attrs) is dict) or
                (isinstance(global_attrs, OrderedDict))):
            ncfile.setncatts(global_attrs)


def save_grid(filename, grid, subset_name='subset_flag',
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
    subset_name : string, optional
        long_name of the netcdf variable
        if the subset symbolises something other than a land/sea mask
    subset_meaning : string, optional
        will be written into flag_meanings metadata of variable 'subset_name'
    global_attrs : dict, optional
        if given will be written as global attributs into netCDF file
    """

    try:
        arrcell = grid.arrcell
    except AttributeError:
        arrcell = None

    if grid.gpidirect is True:
        gpis = None
    else:
        gpis = grid.gpis

    if grid.shape is not None:
        if global_attrs is None:
            global_attrs = {}
        global_attrs['shape'] = grid.shape

    subsets = {subset_name: {'points': grid.subset, 'meaning': subset_meaning}}

    save_lonlat(filename, grid.arrlon, grid.arrlat, grid.geodatum,
                arrcell=arrcell, gpis=gpis, subsets=subsets,
                global_attrs=global_attrs)


def load_grid(filename, subset_flag='subset_flag'):
    """
    load a grid from netCDF file

    Parameters
    ----------
    filename : string
        filename
    subset_flag : string, optional
        name of the subset to load.

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

        # determine if gpis are in order or custom order
        if nc_data.gpidirect == 0x1b:
            gpis = None  # gpis can be calculated through np.arange..
        else:
            gpis = nc_data.variables['gpi'][:].flatten()

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
                                     nc_data.variables['lat'][::-1])
            lons = lons.flatten('F')
            lats = lats.flatten('F')

            if subset_flag in nc_data.variables.keys():
                subset = np.where(
                    nc_data.variables[subset_flag][:].flatten() == 1)[0]

        elif len(shape) == 1:
            lons = nc_data.variables['lon'][:]
            lats = nc_data.variables['lat'][:]

            # determine if it has a subset
            if subset_flag in nc_data.variables.keys():
                subset = np.where(nc_data.variables[subset_flag][:] == 1)[0]

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
