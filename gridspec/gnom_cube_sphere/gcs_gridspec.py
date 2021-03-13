from typing import List

import pygeohash as pgh

from gridspec.gnom_cube_sphere.cubesphere import csgrid_GMAO
from gridspec.gnom_cube_sphere.schmidt import scs_transform
from gridspec.base import GridspecMosaic, GridspecTile


class GridspecGnomonicCubedSphere(GridspecMosaic):
    def __init__(self, cs_size, name=None, tile_names=None, tile_filenames=None, stretch_factor=1, target_lat=-90, target_lon=170):
        do_schmidt = stretch_factor != 1 or target_lat != -90 or target_lon != 170
        if name is None:
            if not do_schmidt:
                name = 'c{cs_size}_gridspec'
            else:
                name = 'c{cs_size}_s{stretch_factor}_t{target_geohash}_gridspec'
        if tile_names is None:
            tile_names = 'tile{tile_number}'
        if tile_filenames is None:
            if not do_schmidt:
                tile_filenames = 'c{cs_size}.{tile_name}.nc'
            else:
                tile_filenames = 'c{cs_size}_s{stretch_factor}_t{target_geohash}.{tile_name}.nc'

        filler_dict = dict(
            cs_size=cs_size,
            stretch_factor=f"{stretch_factor:.2f}".replace(".", "d"),
            target_geohash=pgh.encode(target_lat, target_lon),
        )
        name = name.format(**filler_dict)
        tnames = []
        filenames = []
        for i in range(6):
            filler_dict['tile_number'] = i+1
            tnames.append(tile_names.format(**filler_dict))
            filler_dict['tile_name'] = tnames[-1]
            filenames.append(tile_filenames.format(**filler_dict))

        supergrid_lat, supergrid_lon = self.calc_supergrid_latlon(cs_size, stretch_factor, target_lat, target_lon)
        tile_attrs = dict(
            geometry="spherical",
            north_pole="0.0 90.0",
            projection="cube_gnomonic",
            discretization="logically_rectangular",
            conformal="FALSE"
        )
        super(GridspecGnomonicCubedSphere, self).__init__(
            name=name,
            tile_filenames=filenames,
            contacts=self.get_contacts(name, tnames),
            contact_indices=self.get_contact_indices(cs_size),
            tiles=[GridspecTile(
                name=tnames[i],
                supergrid_lats=supergrid_lat[i, ...],
                supergrid_lons=supergrid_lon[i, ...],
                attrs=tile_attrs

            ) for i in range(len(tnames))]
        )

    @staticmethod
    def calc_supergrid_latlon(cs_size, stretch_factor=1, target_lat=-90, target_lon=170):
        do_schmidt = stretch_factor != 1 or target_lat != -90 or target_lon != 170
        if do_schmidt:
            offset = 0
        else:
            offset = -10

        supergrid = csgrid_GMAO(cs_size*2, offset)
        supergrid_lon = supergrid['lon_b']
        supergrid_lat = supergrid['lat_b']

        if do_schmidt:
            for f in range(6):
                lon = supergrid_lon[f,...].flatten()
                lat = supergrid_lat[f, ...].flatten()

                lon, lat = scs_transform(
                    lon, lat, stretch_factor, target_lon, target_lat
                )
                supergrid_lon[f, ...] = lon.reshape((cs_size * 2 + 1, cs_size * 2 + 1))
                supergrid_lat[f, ...] = lat.reshape((cs_size * 2 + 1, cs_size * 2 + 1))

        return supergrid_lat, supergrid_lon

    @staticmethod
    def get_contacts(name, tile_names):
        contacts = [
            f"{name}:{tile_names[0]}::{name}:{tile_names[1]}",
            f"{name}:{tile_names[0]}::{name}:{tile_names[2]}",
            f"{name}:{tile_names[0]}::{name}:{tile_names[4]}",
            f"{name}:{tile_names[0]}::{name}:{tile_names[5]}",
            f"{name}:{tile_names[1]}::{name}:{tile_names[2]}",
            f"{name}:{tile_names[1]}::{name}:{tile_names[3]}",
            f"{name}:{tile_names[1]}::{name}:{tile_names[5]}",
            f"{name}:{tile_names[2]}::{name}:{tile_names[3]}",
            f"{name}:{tile_names[2]}::{name}:{tile_names[4]}",
            f"{name}:{tile_names[3]}::{name}:{tile_names[4]}",
            f"{name}:{tile_names[3]}::{name}:{tile_names[5]}",
            f"{name}:{tile_names[4]}::{name}:{tile_names[5]}"
        ]
        return contacts

    @staticmethod
    def get_contact_indices(cs_size):
        contact_indices =[
            f"{cs_size*2}:{cs_size*2},1:{cs_size*2}::1:1,1:{cs_size*2}",
            f"1:{cs_size*2},{cs_size*2}:{cs_size*2}::1:1,{cs_size*2}:1",
            f"1:1,1:{cs_size*2}::{cs_size*2}:1,{cs_size*2}:{cs_size*2}",
            f"1:{cs_size*2},1:1::1:{cs_size*2},{cs_size*2}:{cs_size*2}",
            f"1:{cs_size*2},{cs_size*2}:{cs_size*2}::1:{cs_size*2},1:1",
            f"{cs_size*2}:{cs_size*2},1:{cs_size*2}::{cs_size*2}:1,1:1",
            f"1:{cs_size*2},1:1::{cs_size*2}:{cs_size*2},{cs_size*2}:1",
            f"{cs_size*2}:{cs_size*2},1:{cs_size*2}::1:1,1:{cs_size*2}",
            f"1:{cs_size*2},{cs_size*2}:{cs_size*2}::1:1,{cs_size*2}:1",
            f"1:{cs_size*2},{cs_size*2}:{cs_size*2}::1:{cs_size*2},1:1",
            f"{cs_size*2}:{cs_size*2},1:{cs_size*2}::{cs_size*2}:1,1:1",
            f"{cs_size*2}:{cs_size*2},1:{cs_size*2}::1:1,1:{cs_size*2}"
        ]
        return contact_indices
