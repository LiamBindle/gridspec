from pathlib import Path

import xarray as xr

from gridspec.base.mosaic import LoadGridspec


def split_datafile(datafile, tile_dim, gridspec_file, directory=None):
    gridspec = LoadGridspec(gridspec_file)
    ds = xr.open_dataset(datafile)

    assert ds.dims[tile_dim] == len(gridspec.tiles())

    # Determine the output directory for the split files
    datafile_path = Path(datafile)
    parent_dir = datafile_path.parent
    if directory is None:
        directory = parent_dir
    directory = Path(directory)

    # Split the files
    for i, tile_name in enumerate(gridspec.mosaic().tile_names):
        tile_ds = ds.isel(**{tile_dim: i})
        filename = f"{datafile_path.stem}.{tile_name}.nc"
        tile_ds.to_netcdf(directory.joinpath(filename))


def touch_datafiles(gridspec_file, datafile_prefix, datafile_suffix='.nc', directory="./",
                    name_dim0='Ydim', name_dim1='Xdim',
                    name_lat_coord='lats', name_lon_coord='lons'):
    gridspec = LoadGridspec(gridspec_file)
    directory = Path(directory)

    for tile in gridspec.tiles():
        lons = tile.supergrid_lons[1::2, 1::2]
        lats = tile.supergrid_lats[1::2, 1::2]

        ds = xr.Dataset()
        ds.coords[name_lon_coord] = xr.DataArray(
            lons,
            dims=(name_dim0, name_dim1),
            attrs=dict(
                standard_name="geographic_longitude",
                units="degree_east"
            )
        )
        ds.coords[name_lat_coord] = xr.DataArray(
            lats,
            dims=(name_dim0, name_dim1),
            attrs=dict(
                standard_name="geographic_latitude",
                units="degree_north"
            )
        )

        filename = f"{datafile_prefix}.{tile.name}{datafile_suffix}"
        ds.to_netcdf(directory.joinpath(filename))


def join_datafiles(datafile_prefix, gridspec_file, tile_dim,
                   datafile_suffix='.nc', directory="./",
                   rename_dict=None, coord_attrs_dict=None, transpose=None):
    gridspec = LoadGridspec(gridspec_file)
    directory = Path(directory)

    if rename_dict is None:
        rename_dict = {}
    if coord_attrs_dict is None:
        coord_attrs_dict = {}

    datasets = []
    for tile in gridspec.tiles():
        filename = f"{datafile_prefix}.{tile.name}{datafile_suffix}"
        filepath = directory.joinpath(filename)
        datasets.append(xr.open_dataset(filepath))

    ds = xr.concat(datasets, dim=tile_dim)
    ds = ds.rename(rename_dict)

    for c, a in coord_attrs_dict.items():
        ds.coords[c].attrs.update(a)
    if transpose is not None:
        ds = ds.transpose(*transpose)

    filename = f"{datafile_prefix}{datafile_suffix}"
    filepath = directory.joinpath(filename)
    ds.to_netcdf(filepath)
