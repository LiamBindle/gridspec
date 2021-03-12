import xarray as xr

gs = xr.open_dataset('c24_mosaic.nc')

datafile_prefix = 'c12testdata'

gs_children = gs['mosaic'].attrs['children']
tile_dim='nf'
ds = []
for f in range(6):
    tilename = gs[gs_children][f].item().decode()
    datafile_name = f'{datafile_prefix}.{tilename}.nc'
    ds.append(xr.open_dataset(datafile_name))

ds = xr.concat(ds, dim='nf')
ds = ds.rename({'extradim1': 'lev'})
ds.coords['lev'].attrs['standard_nam'] = "model_layer"
ds.coords['lev'].attrs['units'] = "layer"
ds = ds.transpose('time', 'lev', 'nf', 'Ydim', 'Xdim')
ds.to_netcdf('c12_data.nc')
print('here')




