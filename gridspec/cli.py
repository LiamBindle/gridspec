import click
from gridspec import GridspecGnomonicCubedSphere, GridspecRegularLatLon, load_mosaic
from gridspec.base import GridspecMosaic, GridspecTile, CFSingleTile
from gridspec.misc.datafile_ops import join_datafiles, split_datafile, touch_datafiles

output_dir_option_posargs=('-o', '--output-dir')
output_dir_option_kwargs=dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    default="./",
    help="The directory that output files are written to."
)

cs_size_posargs = ('N',)
cs_size_kwargs = dict(
    type=click.IntRange(min=2)
)

stretch_factor_posargs = ('-s', '--stretch-factor',)
stretch_factor_kwargs = dict(
    type=click.FloatRange(min=1.0),
    required=True,
    metavar="S",
    help="The stretch factor"
)

target_point_posargs = ('-t', '--target-point')
target_point_kwargs = dict(
    type=click.FLOAT,
    nargs=2,
    metavar="LAT LON",
    required=True,
    help="The target latitude and longitude"
)

mosaic_file_posargs = ('-m', '--mosaic',)
mosaic_file_kwargs = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
    required=True,
    help="Mosaic file"
)

tile_dim_posargs = ('-d', '--dim')
tile_dim_kwargs = dict(
    type=click.STRING, metavar="NAME", required=True,
    help="Name of the tile dimension in the data files"
)


@click.group()
def create():
    """ Create a gridspec file
    """
    pass


@create.command()
@click.argument(*cs_size_posargs, **cs_size_kwargs)
@click.option(*output_dir_option_posargs, **output_dir_option_kwargs)
def gcs(n, output_dir):
    """Create a Gnomonic Cubed-Sphere (GCS) grid.

    N is the cubed-sphere size (resolution). For example, N=180 for a C180 grid.
    """
    click.echo(f'Creating gnomonic cubed-sphere grid.')
    click.echo(f'  Cubed-sphere size: C{n}\n')
    gs = GridspecGnomonicCubedSphere(n)
    click.echo('Writing mosaic and tile files')
    mosaic_file, tile_files = gs.to_netcdf(directory=output_dir)
    click.echo(f'  + {mosaic_file}')
    for tile_file in tile_files:
        click.echo(f'  + {tile_file}')
    click.echo(f"\nCreated {len([mosaic_file,*tile_files])} files.")


@create.command()
@click.argument(*cs_size_posargs, **cs_size_kwargs)
@click.option(*stretch_factor_posargs, **stretch_factor_kwargs)
@click.option(*target_point_posargs, **target_point_kwargs)
@click.option(*output_dir_option_posargs, **output_dir_option_kwargs)
def sgcs(n, stretch_factor, target_point, output_dir):
    """Create a Stretched Gnomonic Cubed Sphere (SGCS) grid.

    N is the cubed-sphere size (resolution). For example, N=180 for a C180 grid.
    """
    target_lat = target_point[0]
    target_lon = target_point[1]
    if target_lat < -90.0 or target_lat > 90.0:
        raise click.BadParameter("Target latitude must be in the range [-90°N, 90°N]")
    if target_lon < -180.0 or target_lon > 360.0:
        raise click.BadParameter("Target longitude must be in the range [-180°E, 360°E]")

    click.echo(f'Creating stretched gnomonic cubed-sphere grid.')
    click.echo(f'  Cubed-sphere size: C{n}')
    click.echo(f'  Stretch factor:    {round(stretch_factor, 2)}')
    click.echo(f'  Target point:      {round(target_lat, 2)}°N, {round(target_lon, 2)}°E\n')
    gs = GridspecGnomonicCubedSphere(n, stretch_factor=stretch_factor, target_lat=target_lat, target_lon=target_lon)
    click.echo('Writing mosaic and tile files.')
    mosaic_file, tile_files = gs.to_netcdf(directory=output_dir)
    click.echo(f'  + {mosaic_file}')
    for tile_file in tile_files:
        click.echo(f'  + {tile_file}')
    click.echo(f"\nCreated {len([mosaic_file,*tile_files])} files.")


@create.command()
@click.argument('NY', type=click.IntRange(min=1))
@click.argument('NX', type=click.IntRange(min=1))
@click.option('-b', '--bbox',
              type=click.FLOAT,
              default=(-180, -90, 180, 90),
              nargs=4,
              metavar="XMIN YMIN XMAX YMAX",
              help="Bounding box for the grid")
@click.option(*output_dir_option_posargs, **output_dir_option_kwargs)
def latlon(ny, nx, bbox, output_dir):
    """Create a regular lat-lon grid.

    NY is the number of latitude boxes. NX is the number of longitude boxes.
    """
    xmin = bbox[0]
    ymin = bbox[1]
    xmax = bbox[2]
    ymax = bbox[3]
    for y_bound in [ymax, ymin]:
        if y_bound > 90 or y_bound < -90:
            raise click.BadParameter("Invalid latitude in grid bounding box")
    for x_bound in [xmax, xmin]:
        if x_bound > 360 or x_bound < -180:
            raise click.BadParameter("Invalid longitude in grid bounding box")
    click.echo(f'Creating regular lat-lon grid.')
    click.echo(f'  Latitude dimension:  {ny}')
    click.echo(f'  Longitude dimension: {nx}')
    tile = GridspecRegularLatLon(nx=nx, ny=ny, bbox=bbox)
    click.echo('\nWriting mosaic and tile files.')
    ofile = tile.to_netcdf(directory=output_dir)
    click.echo(f'  + {ofile}')
    click.echo(f"\nCreated 1 file.")



@click.command()
@click.argument('filepath', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True))
def dump(filepath):
    """Print information about a gridspec file
    """
    import xarray as xr
    ds = xr.open_dataset(filepath)

    mosaic = GridspecMosaic()
    is_mosaic = mosaic.load(ds)
    if is_mosaic:
        mosaic = load_mosaic(filepath)  # load_mosaic also loads all the tiles
        print(mosaic)
        return

    tile = GridspecTile()
    is_tile = tile.load(ds)
    if is_tile:
        print(tile)
        return

    cf_single_tile = CFSingleTile()
    is_cf_single_tile = cf_single_tile.load(ds)
    if is_cf_single_tile:
        print(cf_single_tile)
        return

    raise click.BadParameter(f"{filepath} is not a gridspec tile or mosaic")

@click.group()
def utils():
    """A collection of gridspec utilities"""
    pass

@utils.command()
@click.argument('datafile',
                nargs=-1, required=True,
                type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True))
@click.option(*mosaic_file_posargs, **mosaic_file_kwargs)
@click.option(*tile_dim_posargs, **tile_dim_kwargs)
@click.option(*output_dir_option_posargs, **output_dir_option_kwargs)
def split(datafile, mosaic, dim, output_dir):
    """
    Split a (stacked) data file into separate data files for each tile.

    DATAFILE... are the data files that are split.
    """
    click.echo(f'Splitting {len(datafile)} datafiles along dimension "{dim}"')
    new_files = []
    for f in datafile:
        split_files = split_datafile(f, dim, mosaic, directory=output_dir)
        for file in split_files:
            click.echo(f"  + {file}")
        new_files.extend(split_files)
    click.echo(f'\nCreated {len(new_files)} files.')

@utils.command()
@click.argument('file_prefix', nargs=-1, required=True, type=click.STRING)
@click.option('-m', '--mosaic',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
              required=True,
              help="Path to gridspec mosaic")
@click.option(*output_dir_option_posargs, **output_dir_option_kwargs)
def touch(file_prefix, mosaic, output_dir):
    """
    Create new empty data files. This is useful for the --dstdatafile argument in ESMF_Regrid.

    FILE_PREFIX... are the name prefixes for the empty data files that are created.
    """
    click.echo(f'Creating empty data files.')
    new_files = []
    for fprefix in file_prefix:
        files = touch_datafiles(mosaic, fprefix, directory=output_dir)
        new_files.extend(files)
        for f in files:
            click.echo(f"  + {f}")
    click.echo(f'\nCreated {len(new_files)} files.')


@utils.command()
@click.argument('file_prefix', nargs=-1, required=True, type=click.STRING)
@click.option(*mosaic_file_posargs, **mosaic_file_kwargs)
@click.option(*tile_dim_posargs, **tile_dim_kwargs)
@click.option('-s', '--spec',
              type=click.File(), metavar="JSONSPEC", required=True,
              help="The joining spec (JSON) file path")
@click.option(*output_dir_option_posargs, **output_dir_option_kwargs)
def join(file_prefix, mosaic, dim, spec, output_dir):
    """
    Create new empty data files. This is useful for the --dstdatafile argument in ESMF_Regrid.

    FILE_PREFIX... are the name prefixes for the empty data files that are created.
    """
    import json
    from pathlib import Path
    click.echo('Loading join specification')
    join_spec = json.loads(spec.read())

    rename_pairs = join_spec.get('rename_dict', {})
    if len(rename_pairs) > 0:
        msg = '  Renaming:' + ", ".join(f"{o} to {n}" for o, n in rename_pairs.items())
        click.echo(msg)
    coord_attrs = join_spec.get('coord_attrs_dict', {})
    if len(coord_attrs) > 0:
        for coord, attr in coord_attrs.items():
            click.echo(f'  Assigning attributes:')
            for k, v in attr.items():
                click.echo(f'    {coord}:{k}="{v}"')
    transpose = join_spec.get('transpose', [])
    if len(transpose) > 0:
        msg = '  Transpose: (' + ", ".join([t for t in transpose]) + ")"
        click.echo(msg)
    else:
        transpose=None

    click.echo(f'\nJoining data files.')
    new_files = []
    for fprefix in file_prefix:
        file = join_datafiles(fprefix, mosaic, tile_dim=dim, directory=output_dir, rename_dict=rename_pairs, coord_attrs_dict=coord_attrs, transpose=transpose)
        new_files.append(file)
        filesize = round(Path(file).stat().st_size / 1024**2)
        click.echo(f"  + {file} ({filesize:,} MB)")
    click.echo(f'\nCreated {len(new_files)} files.')



