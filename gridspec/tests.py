from pathlib import Path

import xarray as xr
from click.testing import CliRunner

import gridspec
from gridspec.misc.datafile_ops import split_datafile, join_datafiles, touch_datafiles
from gridspec.cli import gcs, sgcs

SAMPLE_C24_DATAFILE='../sample_data/GCHP.SpeciesConc.20180101_1200z.nc4'


def test_gridspec_save_and_load(tmp_path):
    mosaic = gridspec.GridspecGnomonicCubedSphere(12)
    fpath, _ = mosaic.to_netcdf(directory=tmp_path)
    mosaic2 = gridspec.load_mosaic(fpath)
    assert mosaic == mosaic2
    for t1, t2 in zip(mosaic.tiles, mosaic2.tiles):
        assert t1 == t2


def test_gridspec_split_files(tmp_path):
    mosaic = gridspec.GridspecGnomonicCubedSphere(24)
    gridspec_path, _ = mosaic.to_netcdf(directory=tmp_path)

    split_files = split_datafile(SAMPLE_C24_DATAFILE, tile_dim='nf', gridspec_file=gridspec_path, directory=tmp_path)
    assert len(split_files) == 6
    assert all([Path(fpath).exists() for fpath in split_files])

    joined_file = join_datafiles(
        'GCHP.SpeciesConc.20180101_1200z', gridspec_path,
        tile_dim="nf", directory=tmp_path,
        transpose=('time', 'lev', 'nf', 'Ydim', 'Xdim')
    )
    assert Path(joined_file).exists()

    original = xr.open_dataset(SAMPLE_C24_DATAFILE).drop('cubed_sphere')
    joined = xr.open_dataset(joined_file).drop('cubed_sphere')
    assert joined.identical(original)



def test_touch_dstdatafiles(tmp_path):
    mosaic = gridspec.GridspecGnomonicCubedSphere(12)
    gridspec_path, _ = mosaic.to_netcdf(directory=tmp_path)

    new_files = touch_datafiles(gridspec_path, 'c12_datafiles', directory=tmp_path)
    assert len(new_files) == 6
    assert all([Path(fpath).exists() for fpath in new_files])


def test_cli_create_gcs(tmp_path):
    runner = CliRunner()
    result = runner.invoke(gcs, ['6', '-o', f'{str(tmp_path)}'])
    assert result.exit_code == 0


def test_cli_create_sgcs(tmp_path):
    runner = CliRunner()
    result = runner.invoke(sgcs, ['10', '-s', '2.5', '-t', '25', '46', '-o', f'{str(tmp_path)}'])
    assert result.exit_code == 0
