from abc import ABC, abstractmethod
from typing import List, Tuple
import os.path
from pathlib import Path

import numpy as np
import xarray as xr

from gridspec.base.utils import string_da, string_array_da, first_da_matching_standard_name


class MosaicFile:
    name_children = "gridtiles"
    name_contacts = "contacts"
    name_contact_index = "contact_index"
    name_ntiles_dim = "ntiles"
    name_ncontact_dim = "ncontact"

    def __init__(self, name=None, tile_names=None, tile_filenames=None, contacts=None, contact_indices=None, tile_files_root="./"):
        self.name = name
        self.tile_files_root = tile_files_root
        self.tile_names = tile_names
        self.tile_filenames = tile_filenames
        self.contacts = contacts
        self.contact_indices = contact_indices

    def tile_file_paths(self):
        """
        Returns a list of the paths to the tile files.
        """
        return [os.path.join(self.tile_files_root, fname) for fname in self.tile_filenames]

    def to_netcdf(self, directory=None) -> str:
        if directory is None:
            directory = Path.cwd()
        elif isinstance(directory, str):
            directory = Path(directory)

        ds = xr.Dataset()
        ds['mosaic'] = string_da(
            self.name,
            standard_name="grid_mosaic_spec",
            children=self.name_children,
            contact_regions=self.name_contacts,
            grid_descriptor="",
        )
        ds['gridlocation'] = string_da(
            self.tile_files_root,
            standard_name="grid_file_location",
        )
        ds['gridfiles'] = string_array_da(
            self.tile_filenames,
            dim=self.name_ntiles_dim
        )
        ds[self.name_children] = string_array_da(
            self.tile_names,
            dim=self.name_ntiles_dim,
        )
        ds[self.name_contacts] = string_array_da(
            self.contacts,
            dim=self.name_ncontact_dim,
            standard_name="grid_contact_spec",
            contact_type="boundary",
            alignment="true",
            contact_index=self.name_contact_index,
            orientation="orient",
        )
        ds[self.name_contact_index] = string_array_da(
            self.contact_indices,
            dim=self.name_ncontact_dim,
            standard_name="starting_ending_point_index_of_contact"
        )
        opath = str(directory.joinpath(f'{self.name}.nc'))
        ds.to_netcdf(opath)
        return opath

    def load_netcdf(self, filepath):
        ds = xr.open_dataset(filepath)
        self.name = ds['mosaic'].item().decode()
        self.name_children = ds['mosaic'].attrs['children']
        self.name_contacts = ds['mosaic'].attrs['contact_regions']
        self.tile_files_root = ds['gridlocation'].item().decode()
        self.tile_names = [byte_arr.decode() for byte_arr in ds[self.name_children].values]
        self.tile_filenames = [byte_arr.decode() for byte_arr in ds["gridfiles"].values]
        self.contacts = [byte_arr.decode() for byte_arr in ds[self.name_contacts].values]
        self.name_contact_index = ds[self.name_contacts].attrs['contact_index']
        self.contact_indices = [byte_arr.decode() for byte_arr in ds[self.name_contact_index].values]

    def __eq__(self, other):
        names_are_equal = (
            self.name == other.name and
            self.name_children == other.name_children and
            self.name_contacts == other.name_contacts and
            self.name_contact_index == other.name_contact_index and
            self.name_ntiles_dim == other.name_ntiles_dim and
            self.name_ncontact_dim == other.name_ncontact_dim
        )
        values_are_equal = (
            self.tile_files_root == other.tile_files_root and
            self.tile_names == other.tile_names and
            self.tile_filenames == other.tile_filenames and
            self.contacts == other.contacts and
            self.contact_indices == other.contact_indices
        )
        return names_are_equal and values_are_equal


class TileFile:
    name_ydim = 'yc'
    name_xdim = 'xc'

    def __init__(self, name=None, supergrid_lats=None, supergrid_lons=None, attrs=None):
        self.name = name
        self.supergrid_lats = supergrid_lats
        self.supergrid_lons = supergrid_lons
        self.attrs = attrs
        if self.attrs is None:
            self.attrs = {}
        self.attrs["standard_name"] = "grid_tile_spec"

    def to_ds(self):
        ds = xr.Dataset()
        ds['tile'] = string_da(
            self.name,
            **self.attrs
            # geometry="spherical",
            # north_pole="0.0 90.0",
            # projection="cube_gnomonic",
            # discretization="logically_rectangular",
            # conformal="FALSE"
        )
        ds['x'] = xr.DataArray(
            self.supergrid_lons, dims=[self.name_ydim, self.name_xdim],
            attrs=dict(standard_name="geographic_longitude", units="degree_east")
        )
        ds['y'] = xr.DataArray(
            self.supergrid_lats, dims=[self.name_ydim, self.name_xdim],
            attrs=dict(standard_name="geographic_latitude", units="degree_north")
        )
        return ds

    def from_ds(self, ds):
        self.attrs = list(ds.filter_by_attrs(standard_name="grid_tile_spec").variables.values())[0].attrs
        self.supergrid_lats = first_da_matching_standard_name(ds, "geographic_latitude")
        self.supergrid_lons = first_da_matching_standard_name(ds, "geographic_longitude")

    def __eq__(self, other):
        names_are_equal = (
            self.name == other.name and
            self.name_ydim == other.name_ydim and
            self.name_xdim == other.name_xdim
        )
        attrs_are_equal = (self.attrs == other.attrs)
        values_are_equal = (
            np.allclose(self.supergrid_lats, other.supergrid_lats) and
            np.allclose(self.supergrid_lons, other.supergrid_lons)
        )
        return names_are_equal and attrs_are_equal and values_are_equal


class GridspecFactory(ABC):
    @abstractmethod
    def tiles(self) -> List[TileFile]:
        pass

    def tile_file_paths(self, mosaic_dir=None) -> List[str]:
        if mosaic_dir is None:
            mosaic_dir = Path.cwd()
        elif isinstance(mosaic_dir, str):
            mosaic_dir = Path(mosaic_dir)

        paths = []
        for tilepath_relto_mosaic in self.mosaic().tile_file_paths():
            if not Path(tilepath_relto_mosaic).is_absolute():
                paths.append(str(mosaic_dir.joinpath(tilepath_relto_mosaic)))
            else:
                paths.append(tilepath_relto_mosaic)
        return paths

    @abstractmethod
    def mosaic(self) -> MosaicFile:
        pass

    def save(self, directory=None) -> str:
        if directory is None:
            directory = Path.cwd()
        elif isinstance(directory, str):
            directory = Path(directory)
        for tile, tile_path in zip(self.tiles(), self.tile_file_paths(directory)):
            ds = tile.to_ds()
            ds.to_netcdf(tile_path)
        mosaic_path = self.mosaic().to_netcdf(directory)
        return mosaic_path


class LoadGridspec(GridspecFactory):
    def __init__(self, gridspec_path):
        self._mosaic = MosaicFile()
        self._mosaic.load_netcdf(gridspec_path)
        self._tiles = [TileFile(name=name) for name in self.mosaic().tile_names]
        for i, filepath in enumerate(self.mosaic().tile_file_paths()):
            if not Path(filepath).is_absolute():
                ipath = str(Path(gridspec_path).parent.joinpath(filepath))
            else:
                ipath = filepath
            ds = xr.open_dataset(ipath)
            self._tiles[i].from_ds(ds)

    def mosaic(self) -> MosaicFile:
        return self._mosaic

    def tiles(self) -> List[TileFile]:
        return self._tiles

