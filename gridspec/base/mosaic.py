from abc import ABC, abstractmethod
from typing import List
import os.path

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

    def to_netcdf(self):
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
        ds.to_netcdf(f'{self.name}.nc')

    def load_netcdf(self, filepath):
        ds = xr.open_dataset(filepath)
        self.name = ds['mosaic'].item().decode()
        self.name_children = ds['mosaic'].attrs['children']
        self.name_contacts = ds['mosaic'].attrs['contact_regions']
        self.tile_files_root = ds['gridlocation'].item().decode()
        self.tile_names = [byte_arr.decode() for byte_arr in ds[self.name_children]]
        self.contacts = [byte_arr.decode() for byte_arr in ds[self.name_contacts]]
        self.name_contact_index = ds[self.name_contacts].attrs['contact_index']
        self.contact_indices = [byte_arr.decode() for byte_arr in ds[self.name_contact_index]]


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
        self.attrs = first_da_matching_standard_name(ds, "grid_tile_spec").attrs
        self.supergrid_lats = first_da_matching_standard_name(ds, "geographic_latitude")
        self.supergrid_lons = first_da_matching_standard_name(ds, "geographic_longitude")


class GridspecFactory(ABC):
    @abstractmethod
    def tiles(self) -> List[TileFile]:
        pass

    @abstractmethod
    def mosaic(self) -> MosaicFile:
        pass

    def save(self):
        for tile, tile_filename in zip(self.tiles(), self.mosaic().tile_filenames):
            ds = tile.to_ds()
            opath = os.path.join(self.mosaic().tile_files_root, tile_filename)
            ds.to_netcdf(opath)
        self.mosaic().to_netcdf()


class LoadGridspec(GridspecFactory):
    def __init__(self, gridspec_path):
        self._mosaic = MosaicFile()
        self._mosaic.load_netcdf(gridspec_path)
        self._tiles = [TileFile(name=name) for name in self.mosaic().tile_names]
        tile_files_root = self.mosaic().tile_files_root
        for i, filename in enumerate(self.mosaic().tile_filenames):
            ds = xr.open_dataset(os.path.join(tile_files_root, filename))
            self._tiles[i].from_ds(ds)

    def mosaic(self) -> MosaicFile:
        return self._mosaic

    def tiles(self) -> List[TileFile]:
        return self._tiles

