import pytest

import numpy as np
from gridspec.misc.geometry import spherical_excess_area, sph2cart, cart2sph, spherical_angle


def test_coordinate_transforms():
    pl1_deg = np.array((32.1, 43.2))
    pl2_deg = np.array((38.1, 42.1))
    pl3_deg = np.array((41.1, 52.1))
    pl4_deg = np.array((35.1, 49.9))

    pl12_deg = np.array([pl1_deg, pl2_deg])

    pl1_rad = np.deg2rad(pl1_deg)
    pl2_rad = np.deg2rad(pl2_deg)
    pl3_rad = np.deg2rad(pl3_deg)
    pl4_rad = np.deg2rad(pl4_deg)

    answer_cart1 = np.array((0.61752530, 0.57989486, 0.53139857))
    answer_cart2 = np.array((0.58388677, 0.52758218, 0.61703587))
    answer_cart3 = np.array((0.46290283, 0.59462487, 0.6573752))
    answer_cart4 = np.array((0.52698956, 0.62582023, 0.57500525))

    # test sph (rad) -> cart
    assert pytest.approx(answer_cart1, rel=1e-6) == sph2cart(pl1_rad)
    assert pytest.approx(answer_cart2, rel=1e-6) == sph2cart(pl2_rad)
    assert pytest.approx(answer_cart3, rel=1e-6) == sph2cart(pl3_rad)
    assert pytest.approx(answer_cart4, rel=1e-6) == sph2cart(pl4_rad)

    # test sph (deg) -> cart
    assert pytest.approx(answer_cart1, rel=1e-6) == sph2cart(pl1_deg, degrees=True)
    assert pytest.approx(answer_cart2, rel=1e-6) == sph2cart(pl2_deg, degrees=True)
    assert pytest.approx(answer_cart3, rel=1e-6) == sph2cart(pl3_deg, degrees=True)
    assert pytest.approx(answer_cart4, rel=1e-6) == sph2cart(pl4_deg, degrees=True)

    # test sph(rad) -> cart -> sph (rad)
    assert pytest.approx(pl1_rad, rel=1e-6) == cart2sph(sph2cart(pl1_rad))
    assert pytest.approx(pl2_rad, rel=1e-6) == cart2sph(sph2cart(pl2_rad))
    assert pytest.approx(pl3_rad, rel=1e-6) == cart2sph(sph2cart(pl3_rad))
    assert pytest.approx(pl4_rad, rel=1e-6) == cart2sph(sph2cart(pl4_rad))

    # test sph (deg) -> cart -> sph (deg)
    assert pytest.approx(pl1_deg, rel=1e-6) == cart2sph(sph2cart(pl1_deg, degrees=True), degrees=True)
    assert pytest.approx(pl2_deg, rel=1e-6) == cart2sph(sph2cart(pl2_deg, degrees=True), degrees=True)
    assert pytest.approx(pl3_deg, rel=1e-6) == cart2sph(sph2cart(pl3_deg, degrees=True), degrees=True)
    assert pytest.approx(pl4_deg, rel=1e-6) == cart2sph(sph2cart(pl4_deg, degrees=True), degrees=True)

    # test higher order
    assert pytest.approx(pl12_deg, rel=1e-6) == cart2sph(sph2cart(pl12_deg, degrees=True), degrees=True)


def test_spherical_angle():

    a = np.array((0, 0))
    b = np.array((90, 0))
    c = np.array((0, 90))

    v = np.array([
        (a, b, c),
        (b, c, a),
        (c, a, b),
        (a, b, c),
    ])
    v = sph2cart(v, degrees=True)

    v1 = v[..., 0]
    v2 = v[..., 1]
    v3 = v[..., 2]

    answer = np.array([
        np.pi / 2,
        np.pi / 2,
        np.pi / 2,
        np.pi / 2,
    ])

    assert pytest.approx(answer, rel=1e-6) == spherical_angle(v1, v2, v3)


def test_area_calculation_single_cell():

    pt1 = np.deg2rad((32.1, 43.2))
    pt2 = np.deg2rad((38.1, 42.1))
    pt3 = np.deg2rad((41.1, 52.1))
    pt4 = np.deg2rad((35.1, 49.9))
    answer_m2 = pytest.approx(481632579328.0, rel=5e-3)  # I don't think I calculated this answer very accurately

    RADIUS_EARTH=6371000.

    area = spherical_excess_area(pt1, pt2, pt3, pt4, radius=RADIUS_EARTH)
    assert area == answer_m2

    # test other pt orders
    area = spherical_excess_area(pt2, pt3, pt4, pt1, radius=RADIUS_EARTH)
    assert area == answer_m2

    area = spherical_excess_area(pt3, pt2, pt1, pt4, radius=RADIUS_EARTH)
    assert area == answer_m2