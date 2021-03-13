import click

@click.group()
def create():
    """ Create a gridspec file
    """
    pass

@create.command()
@click.argument('N',
                type=click.IntRange(min=2))
@click.option('--output-dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
              default="./",
              help="The directory that the mosaic file is saved to")
def gcs(n, output_dir):
    """Create a Gnomonic Cubed-Sphere (GCS) grid.

    N is the cubed-sphere size (resolution). For example, N=180 for a C180 grid.
    """
    from gridspec.gnom_cube_sphere.gcs_gridspec import GnomonicCubedSphereGridspec
    click.echo(f'Creating gnomonic cubed-sphere grid.')
    click.echo(f'  Cubed-sphere size: C{n}\n')
    gs = GnomonicCubedSphereGridspec(n)
    click.echo('Writing mosaic and tile files')
    mosaic_file, tile_files = gs.save(directory=output_dir)
    click.echo(f'  + {mosaic_file}')
    for tile_file in tile_files:
        click.echo(f'  + {tile_file}')
    click.echo(f"\nCreated {len([mosaic_file,*tile_files])} files.")


@create.command()
@click.argument('N',
                type=click.IntRange(min=2))
@click.option('-s', '--stretch-factor',
              type=click.FloatRange(min=1.0),
              required=True,
              metavar="S",
              help="The stretch factor")
@click.option('-t', '--target-point',
              type=click.FLOAT,
              nargs=2,
              metavar="LAT LON",
              required=True,
              help="The target latitude and longitude")
@click.option('--output-dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
              metavar="PATH",
              default="./",
              help="The directory that the mosaic file is saved to")
def sgcs(n, stretch_factor, target_point, output_dir):
    """Create a Stretched Gnomonic Cubed Sphere (SGCS) grid.

    N is the cubed-sphere size (resolution). For example, N=180 for a C180 grid.
    """
    from gridspec.gnom_cube_sphere.gcs_gridspec import GnomonicCubedSphereGridspec

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
    gs = GnomonicCubedSphereGridspec(n, stretch_factor=stretch_factor, target_lat=target_lat, target_lon=target_lon)
    click.echo('Writing mosaic and tile files.')
    mosaic_file, tile_files = gs.save(directory=output_dir)
    click.echo(f'  + {mosaic_file}')
    for tile_file in tile_files:
        click.echo(f'  + {tile_file}')
    click.echo(f"\nCreated {len([mosaic_file,*tile_files])} files.")


@click.group()
def utils():
    """A collection of gridspec utilities"""
    pass

@utils.command()
@click.argument('filepath', type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True))
def show(filepath):
    """Print information about a gridspec file
    """
    import xarray as xr
    ds = xr.open_dataset(filepath)
    from gridspec.base import TileFile, LoadGridspec
    is_mosaic = True
    try:
        mosaic = LoadGridspec(filepath)
        print(mosaic)
    except ValueError:
        is_mosaic = False

    is_tile = True
    if not is_mosaic:
        try:
            tile = TileFile()
            tile.from_ds(ds)
            print(tile)
        except ValueError:
            is_tile = False

    if not is_mosaic and not is_tile:
        raise click.BadParameter(f"{filepath} is not a gridspec file")

@utils.command()
@click.argument('datafile',
                nargs=-1, required=True,
                type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True))
@click.option('-m', '--mosaic',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
              required=True,
              help="Path to gridspec mosaic")
@click.option('-d', '--dim',
              type=click.STRING, metavar="NAME", required=True,
              help="The name of tile dimension in the data files")
@click.option("-o", '--output-dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
              metavar="PATH",
              default="./",
              help="The directory that the mosaic file is saved to")
def split_datafile(datafile, mosaic, dim, output_dir):
    """
    Split a (stacked) data file into separate data files for each tile.

    DATAFILE... are the data files that are split.
    """
    from gridspec.misc.datafile_ops import split_datafile

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
@click.option("-o", '--output-dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
              metavar="PATH",
              default="./",
              help="The directory that the mosaic file is saved to")
def new_datafiles(file_prefix, mosaic, output_dir):
    """
    Create new empty data files. This is useful for the --dstdatafile argument in ESMF_Regrid.

    FILE_PREFIX... are the name prefixes for the empty data files that are created.
    """
    from gridspec.misc.datafile_ops import touch_datafiles

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
@click.option('-m', '--mosaic',
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True),
              required=True,
              help="Path to gridspec mosaic")
@click.option('-d', '--dim',
              type=click.STRING, metavar="NAME", required=True,
              help="The name of tile dimension in the data files")
@click.option('-s', '--spec',
              type=click.File(), metavar="JSONSPEC", required=True,
              help="The joining spec (JSON) file path")
@click.option("-o", '--output-dir',
              type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
              metavar="PATH",
              default="./",
              help="The directory that the mosaic file is saved to")
def join_datafiles(file_prefix, mosaic, dim, spec, output_dir):
    """
    Create new empty data files. This is useful for the --dstdatafile argument in ESMF_Regrid.

    FILE_PREFIX... are the name prefixes for the empty data files that are created.
    """
    import json
    from gridspec.misc.datafile_ops import join_datafiles
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



