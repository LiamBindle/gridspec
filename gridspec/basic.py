import numpy as np
import unicodedata
import xarray as xr


def string_da(value, **attrs):
    da = xr.DataArray(data=value).astype('S255')
    da.attrs.update(attrs)
    return da


def string_array_da(values, dim, **attrs):
    da = xr.DataArray(data=[*values], dims=dim).astype('S255')
    da.attrs.update(attrs)
    return da


def create_mosaic_ds(name, tilenames, gridfiles,
                     contacts, contact_indices,
                     gridfiles_path="./",
                     children_name="gridtiles",
                     contacts_name="contacts",
                     contact_index_name="contact_index",
                     ntiles_dim_name="ntiles",
                     ncontact_dim_name="ncontact",):
    ds = xr.Dataset()
    ds['mosaic'] = string_da(
        name,
        standard_name="grid_mosaic_spec",
        children=children_name,
        contact_regions=contacts_name,
        grid_descriptor="",
    )
    ds['gridlocation'] = string_da(
        gridfiles_path,
        standard_name="grid_file_location",
    )
    ds['gridfiles'] = string_array_da(
        values=gridfiles,
        dim=ntiles_dim_name,
    )
    ds[children_name] = string_array_da(
        values=tilenames,
        dim=ntiles_dim_name,
    )
    ds[contacts_name] = string_array_da(
        values=contacts,
        dim=ncontact_dim_name,
        standard_name="grid_contact_spec",
        contact_type="boundary",
        alignment="true",
        contact_index=contact_index_name,
        orientation="orient",
    )
    ds[contact_index_name] = string_array_da(
        values=contact_indices,
        dim=ncontact_dim_name,
        standard_name="starting_ending_point_index_of_contact"
    )
    return ds


def create_tile_simple_noncompliant(tilename, x, y, ydim_name='YCdim', xdim_name='XCdim'):
    ds = xr.Dataset()
    ds['tile'] = string_da(
        tilename,
        standard_name="grid_tile_spec",
        geometry="spherical",
        north_pole="0.0 90.0",
        projection="cube_gnomonic",
        discretization="logically_rectangular",
        conformal="FALSE"
    )
    ds['x'] = xr.DataArray(
        x, dims=[ydim_name, xdim_name],
        attrs=dict(standard_name="geographic_longitude", units="degree_east")
    )
    ds['y'] = xr.DataArray(
        y, dims=[ydim_name, xdim_name],
        attrs=dict(standard_name="geographic_latitude", units="degree_north")
    )
    return ds

