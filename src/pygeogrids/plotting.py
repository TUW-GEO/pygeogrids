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

import warnings

try:
    import matplotlib.pyplot as plt
    import matplotlib as mp
except ImportError:
    warnings.warn("Matplotlib is necessary for plotting grids. "
                  "Call `conda install matplotlib`")
try:
    import cartopy
    import cartopy.crs as ccrs
except ImportError:
    warnings.warn("Cartopy is necessary for plotting grids."
                  "Call `conda install cartopy`")

import numpy as np
import pygeogrids.grids as grids


def plot_cell_grid_partitioning(
    output, cellsize_lon=5.0, cellsize_lat=5.0, figsize=(12, 6), fontsize=2,
):
    """
    Plot an overview of a global cell partitioning.

    Parameters
    ----------
    output: str
        output file path, must end with .png
    cellsize_lon: float, optional (default: 5.0)
        Cell sampling in longitude dimension
    cellsize_lat: float, optional (default: 5.0)
        Cell sampling in latitude dimension
    figsize: tuple, optional (default: (12, 6))
        Figure size (inch)
    fontsize: float, optional (default: 2)
        Font size for labels on the map
    """

    fig, ax = plt.subplots(figsize=figsize,
                           subplot_kw={"projection": ccrs.PlateCarree()})

    ax.add_feature(cartopy.feature.LAND, color='coral')
    ax.add_feature(cartopy.feature.LAKES, color='aqua')
    ax.add_feature(cartopy.feature.OCEAN, color='aqua')

    for y in np.arange(-90, 90, cellsize_lat):
        ax.plot([-180, 180], [y, y], '--', transform=ccrs.PlateCarree(), lw=0.5,
                color='black')

    for x in np.arange(-180, 180, cellsize_lat):
        ax.plot([x, x], [-90, 90], '--', transform=ccrs.PlateCarree(), lw=0.5,
                color='black')

    label_lats = np.arange(-90 + cellsize_lat / 2.0, 90, cellsize_lat)
    label_lons = np.arange(-180 + cellsize_lon / 2.0, 180, cellsize_lon)
    lons, lats = np.meshgrid(label_lons, label_lats)

    cells = grids.lonlat2cell(
        lons.flatten(),
        lats.flatten(),
        cellsize_lon=cellsize_lon,
        cellsize_lat=cellsize_lat,
    )
    for lon, lat, cell in zip(lons.flatten(), lats.flatten(), cells):
        ax.text(
            lon,
            lat,
            "{:}".format(cell),
            fontsize=fontsize,
            va="center",
            ha="center",
            weight="bold",
        )

    fig.savefig(output, format="png", dpi=300)
    plt.close(fig)