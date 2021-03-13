from gridspec.misc.datafile_ops import split_datafile, join_datafiles, touch_datafiles
from gridspec.gnom_cube_sphere.gcs_gridspec import GnomonicCubedSphereGridspec
from gridspec.base import LoadGridspec

from pathlib import Path

SAMPLE_C24_DATAFILE='../sample_data/GCHP.SpeciesConc.20180101_1200z.nc4'


def test_gridspec_split_files(tmp_path):
    gs = GnomonicCubedSphereGridspec(24)
    gridspec_path, _ = gs.save(directory=tmp_path)

    split_files = split_datafile(SAMPLE_C24_DATAFILE, tile_dim='nf', gridspec_file=gridspec_path, directory=tmp_path)
    assert len(split_files) == 6
    assert all([Path(fpath).exists() for fpath in split_files])


def test_touch_dstdatafiles(tmp_path):
    gs = GnomonicCubedSphereGridspec(12)
    gridspec_path, _ = gs.save(directory=tmp_path)

    new_files = touch_datafiles(gridspec_path, 'c12_datafiles', directory=tmp_path)
    assert len(new_files) == 6
    assert all([Path(fpath).exists() for fpath in new_files])