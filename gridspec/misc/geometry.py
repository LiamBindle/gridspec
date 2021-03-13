import numpy as np


def sph2cart(phi, lam):
    x = np.cos(phi) * np.cos(lam)
    y = np.cos(phi) * np.sin(lam)
    z = np.sin(phi)
    return x, y, z


def cart2sph(x, y, z):
    phi = np.arcsin(z)
    lam = np.arctan2(y, x)
    return phi, lam


def spherical_angle(v1, v2, v3):
    p = np.cross(v1, v2)
    q = np.cross(v1, v3)
    d = np.sqrt(np.dot(p, p) * np.dot(q, q))
    return np.arccos(np.dot(p, q)/d)


def spherical_excess_area(ll_phi, ll_lam,
                          ul_phi, ul_lam,
                          ur_phi, ur_lam,
                          lr_phi, lr_lam,
                          radius=6371000.):
    v1 = sph2cart(ll_phi, ll_lam)
    v2 = sph2cart(lr_phi, lr_lam)
    v3 = sph2cart(ul_phi, ul_lam)
    a1 = spherical_angle(v1, v2, v3)

    v1 = sph2cart(lr_phi, lr_lam)
    v2 = sph2cart(ur_phi, ur_lam)
    v3 = sph2cart(ll_phi, ll_lam)
    a2 = spherical_angle(v1, v2, v3)

    v1 = sph2cart(ur_phi, ur_lam)
    v2 = sph2cart(ul_phi, ul_lam)
    v3 = sph2cart(lr_phi, lr_lam)
    a3 = spherical_angle(v1, v2, v3)

    v1 = sph2cart(ul_phi, ul_lam)
    v2 = sph2cart(ur_phi, ur_lam)
    v3 = sph2cart(ll_phi, ll_lam)
    a4 = spherical_angle(v1, v2, v3)

    area = (a1 + a2 + a3 + a4 - 2.*np.pi) * radius * radius
    return area


if __name__ == '__main__':
    from gridspec.constants import RADIUS_EARTH
    pt1 = (32.1, 43.2)
    pt2 = (38.1, 42.1)
    pt3 = (41.1, 52.1)
    pt4 = (35.1, 49.9)
    correct_area_m2 = 481632579328

    my_area = spherical_excess_area(RADIUS_EARTH,
                                    *np.deg2rad(pt1),
                                    *np.deg2rad(pt2),
                                    *np.deg2rad(pt3),
                                    *np.deg2rad(pt4))
    my_area2 = spherical_excess_area(RADIUS_EARTH,
                                    *np.deg2rad(pt2),
                                    *np.deg2rad(pt3),
                                    *np.deg2rad(pt4),
                                    *np.deg2rad(pt1))
    my_area3 = spherical_excess_area(RADIUS_EARTH,
                                     *np.deg2rad(pt3),
                                     *np.deg2rad(pt2),
                                     *np.deg2rad(pt1),
                                     *np.deg2rad(pt4))

    print(f"Correct value : {correct_area_m2:e} (m+2)")
    print(f"Calculated value: {my_area:e} (m+2)")
    print(f"Calculated value: {my_area2:e} (m+2)")
    print(f"Calculated value: {my_area3:e} (m+2)")