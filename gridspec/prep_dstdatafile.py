import xarray as xr
import numpy as np

gs = xr.open_dataset('c12_mosaic.nc')

datafile_prefix = 'c12testdata'

gs_children = gs['mosaic'].attrs['children']
tile_dim='nf'
ydim_name='Ydim'
xdim_name='Xdim'
for f in range(6):
    tilename = gs[gs_children][f].item().decode()
    grid = xr.open_dataset(gs['gridfiles'][f].item().decode())

    x = grid.filter_by_attrs(standard_name='geographic_longitude').to_array()[0][1::2,1::2]
    y = grid.filter_by_attrs(standard_name='geographic_latitude').to_array()[0][1::2,1::2]

    ds = xr.Dataset()
    ds.coords['lons'] = x
    ds.coords['lons'].attrs['standard_name'] = 'geographic_longitude'
    ds.coords['lons'].attrs['units'] = 'degree_east'
    ds.coords['lats'] = y
    ds.coords['lats'].attrs['standard_name'] = 'geographic_latitude'
    ds.coords['lats'].attrs['units'] = 'degree_north'
    ds = ds.rename({k: v for k, v in zip(x.dims, (ydim_name, xdim_name))})

    datafile_name = f'{datafile_prefix}.{tilename}.nc'
    ds.to_netcdf(datafile_name)
