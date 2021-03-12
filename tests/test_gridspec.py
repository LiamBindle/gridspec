import pytest

from gridspec.gnom_cube_sphere.gcs_gridspec import GnomonicCubedSphereGridspec
from gridspec.base import LoadGridspec


def test_gridspec_save_and_load(tmp_path):
    gs = GnomonicCubedSphereGridspec(12)
    fpath = gs.save(directory=tmp_path)
    gs2 = LoadGridspec(fpath)
    assert gs.mosaic() == gs2.mosaic()
    for t1, t2 in zip(gs.tiles(), gs2.tiles()):
        assert t1 == t2