from abc import ABC, abstractmethod
from typing import List, Tuple
import os.path
from pathlib import Path
import textwrap

import numpy as np
import xarray as xr

from gridspec.misc.geometry import spherical_excess_area


def string_da(value, **attrs):
    """ Returns a xr.DataArray for a character array """
    da = xr.DataArray(data=value).astype('S255')
    da.attrs.update(attrs)
    return da


def string_array_da(values, dim, **attrs):
    """ Returns a xr.DataArray for an array of character arrays """
    da = xr.DataArray(data=[*values], dims=dim).astype('S255')
    da.attrs.update(attrs)
    return da


def get_da_name(ds, standard_name, only_one=True):
    name = list(ds.filter_by_attrs(standard_name=standard_name).variables)
    if not only_one:
        return name
    else:
        if len(name) != 1:
            raise ValueError(f"Multiple variables match standard_name={standard_name}")
        return name[0]

def first_da_matching_standard_name(ds, standard_name, only_one=True):
    """ Returns the xr.DataArray with a standard name """
    v = list(ds.filter_by_attrs(standard_name=standard_name).variables.values())
    if not only_one:
        return v
    else:
        return v[0]


def cwd_if_no_output_dir(directory) -> Path:
    if directory is None:
        return Path.cwd()
    return Path(directory)


class GridspecTile:
    name_dim1 = 'yc'
    name_dim2 = 'xc'
    name_lons = 'lons'
    name_lats = 'lats'
    name_dummy = 'tile'

    def __init__(self, name=None, supergrid_lats=None, supergrid_lons=None, attrs=None):
        self.name = name
        self.supergrid_lats = supergrid_lats
        self.supergrid_lons = supergrid_lons
        self.attrs = attrs
        if self.attrs is None:
            self.attrs = {}
        self.attrs["standard_name"] = "grid_tile_spec"

    def dump(self) -> xr.Dataset:
        ds = xr.Dataset()
        ds[self.name_dummy] = string_da(
            self.name,
            **self.attrs
        )
        if self.is_regular():
            lon_dims = [self.name_lons]
            lat_dims = [self.name_lats]
        else:
            lon_dims = [self.name_dim1, self.name_dim2]
            lat_dims = [self.name_dim1, self.name_dim2]

        ds[self.name_lons] = xr.DataArray(
            self.supergrid_lons, dims=[*lon_dims],
            attrs=dict(standard_name="geographic_longitude", units="degree_east")
        )
        ds[self.name_lats] = xr.DataArray(
            self.supergrid_lats, dims=[*lat_dims],
            attrs=dict(standard_name="geographic_latitude", units="degree_north")
        )
        return ds

    def load(self, ds) -> bool:
        if len(get_da_name(ds, standard_name="grid_tile_spec", only_one=False)) != 1:
            return False
        self.name_dummy = get_da_name(ds, standard_name="grid_tile_spec")
        self.name = ds[self.name_dummy].item().decode()
        self.attrs = ds[self.name_dummy].attrs
        self.name_lats = get_da_name(ds, standard_name="geographic_latitude")
        self.supergrid_lats = ds[self.name_lats].values
        self.name_lons = get_da_name(ds, standard_name="geographic_longitude")
        self.supergrid_lons = ds[self.name_lons].values
        if self.is_regular():
            self.name_dim1 = ds[self.name_lats].dims[0]
            self.name_dim2 = ds[self.name_lons].dims[0]
        else:
            self.name_dim1 = ds[self.name_lons].dims[0]
            self.name_dim2 = ds[self.name_lons].dims[1]
        return True

    def open_netcdf(self, filepath) -> bool:
        ds = xr.open_dataset(filepath)
        return self.load(ds)

    def to_netcdf(self, filepath):
        self.dump().to_netcdf(filepath)

    def __eq__(self, other):
        names_are_equal = (
            self.name == other.name and
            self.name_dim1 == other.name_dim1 and
            self.name_dim2 == other.name_dim2 and
            self.name_lats == other.name_lats and
            self.name_lons == other.name_lons and
            self.name_dummy == other.name_dummy
        )
        attrs_are_equal = (self.attrs == other.attrs)
        values_are_equal = (
            np.allclose(self.supergrid_lats, other.supergrid_lats) and
            np.allclose(self.supergrid_lons, other.supergrid_lons)
        )
        return names_are_equal and attrs_are_equal and values_are_equal

    def get_corners(self) -> List[Tuple[float,float]]:
        if self.is_regular():
            pt1 = (self.supergrid_lats[0], self.supergrid_lons[0])
            pt2 = (self.supergrid_lats[-1], self.supergrid_lons[0])
            pt3 = (self.supergrid_lats[-1], self.supergrid_lons[-1])
            pt4 = (self.supergrid_lats[0], self.supergrid_lons[-1])
        else:
            pt1 = (self.supergrid_lats[0, 0], self.supergrid_lons[0, 0])
            pt2 = (self.supergrid_lats[0, -1], self.supergrid_lons[0, -1])
            pt3 = (self.supergrid_lats[-1, -1], self.supergrid_lons[-1, -1])
            pt4 = (self.supergrid_lats[-1, 0], self.supergrid_lons[-1, 0])
        return [pt1, pt2, pt3, pt4]

    def approx_area_km2(self):
        corners = np.deg2rad(self.get_corners())
        area = spherical_excess_area(*corners[0], *corners[1], *corners[2], *corners[3]) / 1e6
        return area

    def logical_center_latlon(self):
        if self.is_regular():
            lat = self.supergrid_lats[self.supergrid_lats.shape[0] // 2]
            lon = self.supergrid_lons[self.supergrid_lons.shape[0] // 2]
        else:
            center_idx0 = self.supergrid_lats.shape[0] // 2
            center_idx1 = self.supergrid_lats.shape[1] // 2
            lat = self.supergrid_lats[center_idx0, center_idx1]
            lon = self.supergrid_lons[center_idx0, center_idx1]
        return lat, lon

    def get_shape(self):
        shape0 = self.supergrid_lats.shape[0]
        shape1 = self.supergrid_lons.shape[0] if self.is_regular() else self.supergrid_lats.shape[1]
        return shape0, shape1

    def __str__(self):
        lat, lon = self.logical_center_latlon()
        center_lat = f"{round(lat, 1)}°N"
        center_lon = f"{round(lon, 1)}°E"
        center = f"({center_lat:>7s},{center_lon:>8s})"
        text = "  {name:10s}  ({shape0}x{shape1})      logical center {center:20s}  approx area: {area:.1e} km+2"
        shape0, shape1 = self.get_shape()
        text = text.format(
            name=self.name,
            shape0=shape0,
            shape1=shape1,
            center=center,
            area=self.approx_area_km2()
        )
        return text

    def is_regular(self) -> bool:
        return len(self.supergrid_lats.shape) == 1

    def is_curvilinear(self) -> bool:
        return not self.is_regular()


class CFSingleTile(GridspecTile):
    name_dim1 = 'i'
    name_dim2 = 'j'
    name_bnds = 'bounds'
    name_lons = 'lon'
    name_lats = 'lat'
    name_dummy = 'tile'
    name_lat_bnds = 'lat_bnds'
    name_lon_bnds = 'lon_bnds'

    def __init__(self, *args, **kwargs):
        self.center_lats = kwargs.pop('center_lats', None)
        self.center_lons = kwargs.pop('center_lons', None)
        self.lat_bnds = kwargs.pop('lat_bnds', None)
        self.lon_bnds = kwargs.pop('lon_bnds', None)
        super().__init__(*args, **kwargs)

    def dump(self) -> xr.Dataset:
        ds = xr.Dataset()

        if self.is_regular():
            lons_dims=[self.name_lons]
            lats_dims=[self.name_lats]
        else:
            lons_dims=[self.name_dim1, self.name_dim2]
            lats_dims=[self.name_dim1, self.name_dim2]

        ds[self.name_lon_bnds] = xr.DataArray(self.lon_bnds, dims=[*lons_dims, self.name_bnds])
        ds[self.name_lat_bnds] = xr.DataArray(self.lat_bnds, dims=[*lats_dims, self.name_bnds])

        ds[self.name_lons] = xr.DataArray(
            self.center_lons, dims=[*lons_dims],
            attrs=dict(
                standard_name="geographic_longitude",
                units="degree_east",
                bounds=self.name_lon_bnds,
            )
        )
        ds[self.name_lats] = xr.DataArray(
            self.center_lats, dims=[*lats_dims],
            attrs=dict(
                standard_name="geographic_latitude",
                units="degree_north",
                bounds=self.name_lat_bnds,
            )
        )
        return ds

    def to_netcdf(self, directory):
        directory = cwd_if_no_output_dir(directory)
        ds = self.dump()
        opath = str(directory.joinpath(f'{self.name}.nc'))
        ds.to_netcdf(opath)
        return opath

    def init_from_supergrid(self):
        if self.is_regular():
            self.center_lats = self.supergrid_lats[1::2]
            self.center_lons = self.supergrid_lons[1::2]
            lat_bnds = self.supergrid_lats[0::2]
            self.lat_bnds = np.transpose([lat_bnds[:-1], lat_bnds[1:]])
            lon_bnds = self.supergrid_lons[0::2]
            self.lon_bnds = np.transpose([lon_bnds[:-1], lon_bnds[1:]])
        else:
            raise NotImplementedError("Not implemented yet")


class GridspecMosaic:
    name_children = "gridtiles"
    name_contacts = "contacts"
    name_contact_index = "contact_index"
    name_ntiles_dim = "ntiles"
    name_ncontact_dim = "ncontact"
    name_dummy = "mosaic"

    def __init__(self, name=None, tiles=None, tile_names=None, tile_filenames=None, contacts=None, contact_indices=None,
                 tile_files_root="./"):
        self.name = name
        self._tiles = tiles
        if tile_names is not None:
            self.tile_names = tile_names
        elif tiles is not None:
            self.tile_names = [tile.name for tile in tiles]
        self.tile_files_root = tile_files_root
        self.tile_filenames = tile_filenames
        self.contacts = contacts
        self.contact_indices = contact_indices
        self.this_files_path = None

    def tile_paths(self, mosaic_dir=None):
        paths = []
        if mosaic_dir is not None:
            tile_paths = self.tile_paths()
            for path in tile_paths:
                if Path(path).is_absolute():
                    paths.append(str(path))
                else:
                    paths.append(Path(mosaic_dir).joinpath(path))
        else:
            for fname in self.tile_filenames:
                paths.append(Path(self.tile_files_root).joinpath(fname))
        return paths

    def dump(self) -> xr.Dataset:
        ds = xr.Dataset()
        ds[self.name_dummy] = string_da(
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
        return ds

    def to_netcdf(self, directory=None, write_tiles=True):
        directory = cwd_if_no_output_dir(directory)
        ds = self.dump()
        opath = str(directory.joinpath(f'{self.name}.nc'))
        ds.to_netcdf(opath)

        if write_tiles:
            tile_paths = []
            for tile_path, tile in zip(self.tile_paths(mosaic_dir=directory), self.tiles):
                tile.to_netcdf(tile_path)
                tile_paths.append(tile_path)
            return opath, tile_paths
        else:
            return opath

    def load(self, ds) -> bool:
        if len(get_da_name(ds, standard_name="grid_mosaic_spec", only_one=False)) != 1:
            return False
        self.name_dummy = get_da_name(ds, standard_name="grid_mosaic_spec")
        self.name = ds[self.name_dummy].item().decode()
        self.name_children = ds[self.name_dummy].attrs['children']
        self.name_contacts = ds[self.name_dummy].attrs['contact_regions']
        self.tile_files_root = ds['gridlocation'].item().decode()
        self.tile_names = [byte_arr.decode() for byte_arr in ds[self.name_children].values]
        self.tile_filenames = [byte_arr.decode() for byte_arr in ds["gridfiles"].values]
        self.contacts = [byte_arr.decode() for byte_arr in ds[self.name_contacts].values]
        self.name_contact_index = ds[self.name_contacts].attrs['contact_index']
        self.contact_indices = [byte_arr.decode() for byte_arr in ds[self.name_contact_index].values]
        return True

    def open_netcdf(self, filepath, load_tiles=True) -> bool:
        ds = xr.open_dataset(filepath)
        ok = self.load(ds)
        if ok and load_tiles:
            for i, tile_path in enumerate(self.tile_paths(mosaic_dir=Path(filepath).parent)):
                if not self.tiles[i].open_netcdf(tile_path):
                    raise RuntimeError(f"Failed to load gridspec tile: {tile_path}")
        return ok

    def __eq__(self, other):
        names_are_equal = (
                self.name == other.name and
                self.name_children == other.name_children and
                self.name_contacts == other.name_contacts and
                self.name_contact_index == other.name_contact_index and
                self.name_ntiles_dim == other.name_ntiles_dim and
                self.name_ncontact_dim == other.name_ncontact_dim and
                self.name_dummy == other.name_dummy
        )
        values_are_equal = (
                self.tile_files_root == other.tile_files_root and
                self.tile_names == other.tile_names and
                self.tile_filenames == other.tile_filenames and
                self.contacts == other.contacts and
                self.contact_indices == other.contact_indices
        )
        return names_are_equal and values_are_equal

    @property
    def tiles(self) -> List[GridspecTile]:
        if self._tiles is None:
            self._tiles = [GridspecTile() for _ in self.tile_filenames]
        return self._tiles

    @tiles.setter
    def tiles(self, tiles: List[GridspecTile]):
        raise NotImplementedError("Not allowed")

    def __str__(self):
        header = f"Gridspec mosaic  ({self.name}, {len(self.tile_filenames)} tiles, {len(self.contacts)} contacts)"
        tile_desc = f"Tile files:      "
        tile_desc += ", ".join([f'"{filepath}"' for filepath in self.tile_paths()])
        tile_desc = "\n...              ".join(textwrap.wrap(tile_desc, 80))
        text = header + "\n" + tile_desc
        text += f"\n\nGridspec tiles:"
        for tile in self.tiles:
            text += f"\n{str(tile)}"
        return text


def load_mosaic(filename, load_tiles=True):
    mosaic = GridspecMosaic()
    if not mosaic.open_netcdf(filename, load_tiles=load_tiles):
        raise RuntimeError(f"Failed to load {filename} as a gridspec mosaic")
    return mosaic


def load_tile(filename):
    tile = GridspecTile()
    if not tile.open_netcdf(filename):
        raise RuntimeError(f"Failed to load {filename} as a gridspec tile")
    return tile

