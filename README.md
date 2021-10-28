## gridspec
![CI badge](https://github.com/LiamBindle/gridspec/actions/workflows/continuous-integration.yml/badge.svg) ![GitHub](https://img.shields.io/github/license/LiamBindle/gridspec?color=blue) ![Python versions](https://img.shields.io/badge/python-%3E%3D3.6-brightgreen) [![DOI](https://zenodo.org/badge/347012459.svg)](https://zenodo.org/badge/latestdoi/347012459)


Gridspec is a proposed standard for representing Earth system model grids. The standard was originally proposed by
V. Balaji and Z. Liang (2007; [reference](https://extranet.gfdl.noaa.gov/~vb/gridstd/gridstd.html)). 

Gridspec files are useful for offline regridding with the Earth System Modeling Framework 
([ESMF](https://earthsystemmodeling.org/)), but there are no generalized frameworks or utilities for creating gridspec
files and data. This project aims to develop common tools for working with gridspec files and data.

## Supported grids

The grids that are currently implemented are:

- [X] gnomonic cubed-sphere (see: `gridspec-create gcs --help`)
- [X] stretched gnomonic cubed-sphere (see: `gridspec-create sgcs --help`)
- [X] regular lat-lon grid (see: `gridspec-create latlon --help`)
  - [X] pole-centered/polar-edge and dateline-centered/dateline-edge
  - [X] regional lat-lon grid 
- [ ] gaussian grid

See "Contributing" for information on submitting pull-requests and setting up a development copy. 

## Compliance

- [X] ESMF GRIDSPEC (subset of the standard)
- [ ] Full gridspec standard

## Installation

You can install `gridspec` like so:
```console
$ pip install git+https://github.com/LiamBindle/gridspec.git 
```

This installs (see `--help` for subcommands and their usage):

- `gridspec-create`: create a gridspec file for one of the supported grids (mosaic or tile)
- `gridspec-dump`: displays useful information about a gridspec file
- `gridspec-utils`: utilities for working with gridspec data (splitting stacked data files, joining tiled data files, etc.) 

## Examples

Creating a cubed-sphere grid:
```console
$ gridspec-create gcs 24
Creating gnomonic cubed-sphere grid.
  Cubed-sphere size: C24

Writing mosaic and tile files
  + c24_gridspec.nc
  + c24.tile1.nc
  + c24.tile2.nc
  + c24.tile3.nc
  + c24.tile4.nc
  + c24.tile5.nc
  + c24.tile6.nc

Created 7 files.
$ 
```

Creating a stretched cubed-sphere grid:
```console
$ gridspec-create sgcs 24 -s 2 -t 40 -100
Creating stretched gnomonic cubed-sphere grid.
  Cubed-sphere size: C12
  Stretch factor:    2.0
  Target point:      40.0°N, -100.0°E

Writing mosaic and tile files.
  + c12_s2d00_t9z0gs3y0zh7w_gridspec.nc
  + c12_s2d00_t9z0gs3y0zh7w.tile1.nc
  + c12_s2d00_t9z0gs3y0zh7w.tile2.nc
  + c12_s2d00_t9z0gs3y0zh7w.tile3.nc
  + c12_s2d00_t9z0gs3y0zh7w.tile4.nc
  + c12_s2d00_t9z0gs3y0zh7w.tile5.nc
  + c12_s2d00_t9z0gs3y0zh7w.tile6.nc

Created 7 files.
$ 
```

View the contents of a mosaic or tile file:
```console
$ gridspec-dump c24_gridspec.nc                  
Gridspec mosaic  (c24_gridspec, 6 tiles, 12 contacts)
Tile files:      "c24.tile1.nc", "c24.tile2.nc", "c24.tile3.nc", "c24.tile4.nc",
...              "c24.tile5.nc", "c24.tile6.nc"

Gridspec tiles:
  tile1       (49x49)      logical center (  0.0°N, 350.0°E)    approx area: 8.5e+07 km+2
  tile2       (49x49)      logical center (  0.0°N,  80.0°E)    approx area: 8.5e+07 km+2
  tile3       (49x49)      logical center ( 90.0°N, 350.0°E)    approx area: 8.5e+07 km+2
  tile4       (49x49)      logical center (  0.0°N, 170.0°E)    approx area: 8.5e+07 km+2
  tile5       (49x49)      logical center (  0.0°N, 260.0°E)    approx area: 8.5e+07 km+2
  tile6       (49x49)      logical center (-90.0°N,  35.0°E)    approx area: 8.5e+07 km+2
$ 
```

## Contributing
Submit pull requests to https://github.com/LiamBindle/gridspec. Please make sure to include tests for your PR.

To set up a developement copy:

1. Clone the repo
   ```console
   $ git clone https://github.com/LiamBindle/gridspec
   ```
2. Install as an editable package:
   ```console
   $ pip install -e gridspec/
   ```
 
### Tests
To run the tests, you need to install [pytest](https://docs.pytest.org/en/stable/getting-started.html). 
Once pytest is installed, you can run the tests like so (pytest test discovery is described 
[here](https://docs.pytest.org/en/stable/goodpractices.html#conventions-for-python-test-discovery)):
```console
$ pytest
```
