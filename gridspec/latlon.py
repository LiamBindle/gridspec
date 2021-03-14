import numpy as np

from gridspec.base import CFSingleTile


class GridspecRegularLatLon(CFSingleTile):
    def __init__(self, nx, ny, name='regular_lat_lon_{ny}x{nx}', bbox=(-180, -90, 180, 90)):
        filler_dict=dict(nx=nx, ny=ny)
        name = name.format(**filler_dict)
        supergrid_lons = np.linspace(bbox[0], bbox[2], nx*2+1)
        supergrid_lats = np.linspace(bbox[1], bbox[3], ny*2+1)
        super().__init__(name=name)
        self.init_from_supergrids(supergrid_lats, supergrid_lons)


if __name__ == '__main__':
    tile = GridspecRegularLatLon(180, 91)
    tile.to_netcdf(f'/home/liam/dev/gridspec/scratch')
    # tile.to_netcdf(f'/home/liam/dev/gridspec/scratch/{tile.name}.nc')