import numpy as np


def sph2cart(pl, degrees=False):
    if degrees:
        pl = np.deg2rad(pl)

    xyz_shape = list(pl.shape)
    xyz_shape[-1] = 3
    xyz = np.zeros(xyz_shape)

    xyz[..., 0] = np.cos(pl[..., 0]) * np.cos(pl[..., 1])
    xyz[..., 1] = np.cos(pl[..., 0]) * np.sin(pl[..., 1])
    xyz[..., 2] = np.sin(pl[..., 0])

    return xyz


def cart2sph(xyz, degrees=False):
    pl_shape = list(xyz.shape)
    pl_shape[-1] = 2
    pl = np.zeros(pl_shape)

    pl[..., 0] = np.arcsin(xyz[..., 2])
    pl[..., 1] = np.arctan2(xyz[..., 1], xyz[..., 0])

    if degrees:
        pl = np.rad2deg(pl)

    return pl


def spherical_angle(v1, v2, v3):
    p = np.cross(v1, v2)
    q = np.cross(v1, v3)
    #d = np.sqrt(np.dot(p, p) * np.dot(q, q))
    pp = np.sum(p*p, axis=-1)
    qq = np.sum(q*q, axis=-1)
    pq = np.sum(p*q, axis=-1)
    d = np.sqrt(pp * qq)
    return np.arccos(pq/d)


def spherical_excess_area(ll, ul, ur, lr, radius=6371000.):
    v1 = sph2cart(ll)
    v2 = sph2cart(lr)
    v3 = sph2cart(ul)
    a1 = spherical_angle(v1, v2, v3)

    v1 = sph2cart(lr)
    v2 = sph2cart(ur)
    v3 = sph2cart(ll)
    a2 = spherical_angle(v1, v2, v3)

    v1 = sph2cart(ur)
    v2 = sph2cart(ul)
    v3 = sph2cart(lr)
    a3 = spherical_angle(v1, v2, v3)

    v1 = sph2cart(ul)
    v2 = sph2cart(ur)
    v3 = sph2cart(ll)
    a4 = spherical_angle(v1, v2, v3)

    area = (a1 + a2 + a3 + a4 - 2.*np.pi) * radius * radius
    return area

