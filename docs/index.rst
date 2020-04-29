==========
pygeogrids
==========

This is the documentation of **pygeogrids**.

pygeogrids is a package for creation and handling of Discrete Global Grids.

It can be used to define a grid on the globe using numpy arrays of longitude and
latitude.  These grids can also have unique grid point numbers. The grids must
not be valid globally but can e.g. only cover the Continents.

When a grid is defined it can be used to quickly find the nearest neigbor of a a
given lat, lon coordinate on the grid. For that the lon, lat coordinates are
converted to Cartesian coordinates. This approach is of limited use for high
resolution data which might rely on a specific geodetic datum.

The class :class:`pygeogrids.grids.CellGrid` extends this basic grid with the
ability to store a additional cell number for each grid point. This can be used
to tile a grid in e.g. 5x5° cells. We often store remote sensing data in cells
to partition a dataset into manageable parts. This link with the grid class
enables us to easily find the link between a grid point and the cell file in
which the relevant data is stored.

Please see the examples in this documentation as well as the `pytesmo
<https://github.com/TUW-GEO/pytesmo>`_ code for real world usage examples.


Contents
========

.. toctree::
   :maxdepth: 2

   License <license>
   Authors <authors>
   Changelog <changelog>
   Module Reference <api/modules>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. _toctree: http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html
.. _reStructuredText: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _references: http://www.sphinx-doc.org/en/stable/markup/inline.html
.. _Python domain syntax: http://sphinx-doc.org/domains.html#the-python-domain
.. _Sphinx: http://www.sphinx-doc.org/
.. _Python: http://docs.python.org/
.. _Numpy: http://docs.scipy.org/doc/numpy
.. _SciPy: http://docs.scipy.org/doc/scipy/reference/
.. _matplotlib: https://matplotlib.org/contents.html#
.. _Pandas: http://pandas.pydata.org/pandas-docs/stable
.. _Scikit-Learn: http://scikit-learn.org/stable
.. _autodoc: http://www.sphinx-doc.org/en/stable/ext/autodoc.html
.. _Google style: https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings
.. _NumPy style: https://numpydoc.readthedocs.io/en/latest/format.html
.. _classical style: http://www.sphinx-doc.org/en/stable/domains.html#info-field-lists
