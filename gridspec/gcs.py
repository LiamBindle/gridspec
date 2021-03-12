from gridspec.basic import create_mosaic_ds, create_tile_simple_noncompliant

from gridspec.grids.gnomonic_cube_sphere import make_grid_CS


def create_gcs_mosaic(cs_size,
                      name="c{cs_size}_mosaic",
                      tilenames='tile{tile_number}',
                      gridfiles_names='c{cs_size}.{tile_name}.nc',
                      ):
    name=name.format(cs_size=cs_size)
    tiles = [tilenames.format(cs_size=cs_size, tile_number=tile_number) for tile_number in range(1,7)]
    gridfiles = [gridfiles_names.format(
        cs_size=cs_size,
        tile_number=tile_number+1,
        tile_name=tile_name
    ) for tile_number, tile_name in enumerate(tiles)]
    contacts = [
        f"{name}:{tiles[0]}::{name}:{tiles[1]}",
        f"{name}:{tiles[0]}::{name}:{tiles[2]}",
        f"{name}:{tiles[0]}::{name}:{tiles[4]}",
        f"{name}:{tiles[0]}::{name}:{tiles[5]}",
        f"{name}:{tiles[1]}::{name}:{tiles[2]}",
        f"{name}:{tiles[1]}::{name}:{tiles[3]}",
        f"{name}:{tiles[1]}::{name}:{tiles[5]}",
        f"{name}:{tiles[2]}::{name}:{tiles[3]}",
        f"{name}:{tiles[2]}::{name}:{tiles[4]}",
        f"{name}:{tiles[3]}::{name}:{tiles[4]}",
        f"{name}:{tiles[3]}::{name}:{tiles[5]}",
        f"{name}:{tiles[4]}::{name}:{tiles[5]}"
    ]
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
    ds = create_mosaic_ds(name, tiles, gridfiles, contacts, contact_indices)
    ds.to_netcdf(f'{name}.nc')
    return ds


def create_gcs_tiles(cs_size, tilenames='tile{tile_number}', gridfiles='c{cs_size}.{tile_name}.nc'):
    grid, _ = make_grid_CS(cs_size)
    x = grid['lon_b']
    y = grid['lat_b']
    tiles = []
    for face in range(6):
        template_dict = dict(tile_number=face+1, cs_size=cs_size)
        tilename = tilenames.format(**template_dict)
        template_dict['tile_name'] = tilename
        ds = create_tile_simple_noncompliant(
            tilename,
            x[face], y[face]
        )
        gridfile_name = gridfiles.format(**template_dict)
        ds.to_netcdf(gridfile_name)
        tiles.append(ds)
    return tiles

if __name__ == '__main__':
    cs_size = 24
    create_gcs_tiles(cs_size)
    create_gcs_mosaic(cs_size)