## gridspec
Gridspec is a proposed standard for representing Earth system model grids. The standard was originally proposed by
V. Balaji and Z. Liang (2007; [reference](https://extranet.gfdl.noaa.gov/~vb/gridstd/gridstd.html)).

## Motivation
Gridspec is particularly useful for regridding cubed-sphere data offline with tools like `ESMF_Regrid` and 
`ESMF_RegridWeightGen`. Two barriers to effective use of gridspec files for offline regridding are: 
to using gridspec effectively are:
- No generalized frameworks or tools exist for creating gridspec files. Creating gridspec mosaic and tile files is 
  time-consuming and error-prone.
- No generalized utilities for converting CF compliant datafiles to/from gridspec compliant datafiles exist. 
  Implementing custom utilities for stacking/unstacking tiled datafiles is tedious.
  
This project aims to develop and support common tools for working with gridspec files. 

## Implementation compliance

- [X] ESMF_GRIDSPEC
- [ ] full gridspec standard

## Supported grids

- gnomonic cubed-sphere
- stretched gnomonic cubed-sphere

## Examples
todo

## Installation
todo

## Contribute
todo

## Tests
todo

## Credits
todo
