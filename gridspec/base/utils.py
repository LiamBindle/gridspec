import xarray as xr


def string_da(value, **attrs):
    da = xr.DataArray(data=value).astype('S255')
    da.attrs.update(attrs)
    return da


def string_array_da(values, dim, **attrs):
    da = xr.DataArray(data=[*values], dims=dim).astype('S255')
    da.attrs.update(attrs)
    return da


def first_da_matching_standard_name(ds, standard_name):
    return ds.filter_by_attrs(standard_name=standard_name).to_array()[0]