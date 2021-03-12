import xarray as xr

ds = xr.open_dataset('../sample_data/GCHP.SpeciesConc.20180101_1200z.nc4')
gs = xr.open_dataset('c24_mosaic.nc')

datafile_prefix = 'testdata'

gs_children = gs['mosaic'].attrs['children']
tile_dim='nf'
for f in range(6):
    tile_ds = ds.isel(nf=f)
    tilename = gs[gs_children][f].item().decode()
    datafile_name = f'{datafile_prefix}.{tilename}.nc'
    tile_ds.to_netcdf(datafile_name)




