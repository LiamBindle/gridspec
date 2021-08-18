import numpy as np

from gridspec.base import CFSingleTile


class GridspecRegularLatLon(CFSingleTile):
    def __init__(self, nx, ny, name='regular_lat_lon_{ny}x{nx}',
                 bbox=(-180, -90, 180, 90), pole_centered=False, dateline_centered=False):
        filler_dict=dict(nx=nx, ny=ny)
        name = name.format(**filler_dict)

        bbox = list(bbox)
        if pole_centered:
            dy = (bbox[3] - bbox[1])/(ny-1)
            bbox[1] -= dy/2
            bbox[3] += dy/2

        if dateline_centered:
            dx = (bbox[2] - bbox[0])/nx
            bbox[0] -= dx/2
            bbox[2] -= dx/2

        supergrid_lons = np.linspace(bbox[0], bbox[2], nx*2+1)
        supergrid_lats = np.linspace(bbox[1], bbox[3], ny*2+1)

        if pole_centered:  # restrict bounds to [-90, 90]; agrees with ESMF_RegridWeightGen
            supergrid_lats = np.clip(supergrid_lats, -90, 90)

        super().__init__(name=name)
        self.init_from_supergrids(supergrid_lats, supergrid_lons)


if __name__ == '__main__':
    tile = GridspecRegularLatLon(576, 361, dateline_centered=True)
    tile._update_supergrids()
    area = tile._calc_area()

    print('area for ', tile)
    print(f'    min res.:     {np.sqrt(area.max()/1e6):.1f} km')
    print(f'    max res.:     {np.sqrt(area.min()/1e6):.1f} km')
    print(f'    mean res.:    {np.sqrt(area.mean()/1e6):.1f} km')
    print(f'    dim0 spacing: {np.diff(tile.lat_bnds[0,:]).item():.4f}°N')
    print(f'    dim1 spacing: {np.diff(tile.lon_bnds[0,:]).item():.4f}°E')

    #tile.to_netcdf(f'/home/liam/dev/gridspec/scratch')
    # tile.to_netcdf(f'/home/liam/dev/gridspec/scratch/{tile.name}.nc')