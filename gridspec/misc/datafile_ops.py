from pathlib import Path
from typing import List

import xarray as xr

from gridspec.base import load_mosaic


def split_datafile(datafile, tile_dim, gridspec_file, directory=None) -> List[str]:
    mosaic = load_mosaic(gridspec_file)
    ds = xr.open_dataset(datafile)

    assert ds.dims[tile_dim] == len(mosaic.tiles)

    # Determine the output directory for the split files
    datafile_path = Path(datafile)
    parent_dir = datafile_path.parent
    if directory is None:
        directory = parent_dir
    directory = Path(directory)

    # Split the files
    split_file_paths=[]
    for i, tile_name in enumerate(mosaic.tile_names):
        tile_ds = ds.isel(**{tile_dim: i})
        filename = f"{datafile_path.stem}.{tile_name}.nc"
        opath = str(directory.joinpath(filename))
        tile_ds.to_netcdf(opath)
        split_file_paths.append(opath)
    return split_file_paths


def touch_datafiles(gridspec_file, datafile_prefix, datafile_suffix='.nc', directory="./",
                    name_dim1='Ydim', name_dim2='Xdim',
                    name_lat_coord='lats', name_lon_coord='lons') -> List[str]:
    mosaic = load_mosaic(gridspec_file)
    directory = Path(directory)

    new_files=[]
    for tile in mosaic.tiles:
        lons = tile.supergrid_lons[1::2, 1::2]
        lats = tile.supergrid_lats[1::2, 1::2]

        ds = xr.Dataset()
        ds.coords[name_lon_coord] = xr.DataArray(
            lons,
            dims=(name_dim1, name_dim2),
            attrs=dict(
                standard_name="geographic_longitude",
                units="degree_east"
            )
        )
        ds.coords[name_lat_coord] = xr.DataArray(
            lats,
            dims=(name_dim1, name_dim2),
            attrs=dict(
                standard_name="geographic_latitude",
                units="degree_north"
            )
        )

        filename = f"{datafile_prefix}.{tile.name}{datafile_suffix}"
        opath = str(directory.joinpath(filename))
        ds.to_netcdf(opath)
        new_files.append(opath)
    return new_files



def join_datafiles(datafile_prefix, gridspec_file, tile_dim,
                   datafile_suffix='.nc', directory="./",
                   rename_dict=None, coord_attrs_dict=None, transpose=None) -> str:
    mosaic = load_mosaic(gridspec_file, load_tiles=False)
    directory = Path(directory)

    if rename_dict is None:
        rename_dict = {}
    if coord_attrs_dict is None:
        coord_attrs_dict = {}

    datasets = []
    for tile_name in mosaic.tile_names:
        filename = f"{datafile_prefix}.{tile_name}{datafile_suffix}"
        filepath = directory.joinpath(filename)
        datasets.append(xr.open_dataset(filepath))

    ds = xr.concat(datasets, dim=tile_dim)
    ds = ds.rename(rename_dict)

    for c, a in coord_attrs_dict.items():
        ds.coords[c].attrs.update(a)
    if transpose is not None:
        ds = ds.transpose(*transpose)

    filename = f"{datafile_prefix}{datafile_suffix}"
    filepath = str(directory.joinpath(filename))
    ds.to_netcdf(filepath)
    return filepath
