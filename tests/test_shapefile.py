import pytest
from pygeogrids.shapefile import subgrid_for_shp, ogr_installed
from pygeogrids.grids import genreg_grid

@pytest.mark.skipif(not ogr_installed, reason="OGR not installed.")
def test_subgrid_from_shapefile():
    grid = genreg_grid(1)

    # here we mix a country name with a continent name to load both
    subgrid = subgrid_for_shp(grid, ['Oceania', 'Austria'],
                              field=["NAME", "CONTINENT"])
    assert 14956 in subgrid.gpis  # Austria
    assert 43883 in subgrid.gpis  # Australia
    assert subgrid.activearrlon.min() == 11.5
    assert subgrid.activearrlon.max() == 179.5
    assert subgrid.activearrlat.min() == -46.5
    assert subgrid.activearrlat.max() == 48.5

    # here we search by abbreviation and german name
    subgrid = subgrid_for_shp(grid, ['JPN', 'Südkorea'])
    assert 19387 in subgrid.gpis  # South Korea
    assert 20112 in subgrid.gpis  # Japan

    # here we search by subregion and INCOME_GRP
    subgrid = subgrid_for_shp(grid, ['Sub-Saharan Africa',
                                     '1. High income: OECD'])
    assert 14956 in subgrid.gpis  # Austria
    assert 29384 in subgrid.gpis  # Ethiopia
