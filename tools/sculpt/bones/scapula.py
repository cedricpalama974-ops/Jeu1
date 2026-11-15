"""Scapula gauche du porc charcutier.

Repère local : Y = axe proximo-distal (0 = cavité glénoïdale, + = bord
dorsal), X = crânial, Z = latéral (+).
Longueur ≈ 20 cm, bord dorsal ≈ 12 cm. Reliefs : lame triangulaire,
fosses supra- et infra-épineuses, épine avec tubérosité de l'épine
volumineuse recourbée caudalement, pas d'acromion (porc), col, cavité
glénoïdale ovale, tubercule supraglénoïdal et processus coracoïde,
bord caudal épaissi, angles crânial et caudal.
"""
import numpy as np
from sdf import smin, ssub, smax, ellipsoid, sphere, tube, round_cone, frame, plate, fbm

BBOX = ((-7.6, -1.2, -1.8), (7.8, 20.8, 4.4))


def _smooth_closed(ctrl, n):
    """Contour fermé lissé (Catmull-Rom) à partir de points de contrôle."""
    out = []
    m = len(ctrl)
    for i in range(m):
        p0, p1, p2, p3 = ctrl[i - 1], ctrl[i], ctrl[(i + 1) % m], ctrl[(i + 2) % m]
        for s in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * s + (2 * p0 - 5 * p1 + 4 * p2 - p3) * s * s
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * s ** 3))
    return out


def _smooth_open(ctrl, n):
    ctrl = np.asarray(ctrl, float)
    top = _smooth_closed(ctrl[1:-1], n)
    return [tuple(ctrl[0])] + [p for p in top if p[1] > 0.05] + [tuple(ctrl[-1])]


def _thick(u, v):
    # lame mince (3 mm) épaissie vers le col et le bord caudal
    t = 0.28 + 0.9 * np.clip((6.0 - v) / 5.0, 0, 1) ** 1.5
    t = t + 0.35 * np.clip((-u - 0.25 * v) / 3.0 + 0.4, 0, 1) * (v < 18)
    return t


def sdf(P):
    I = np.eye(3)
    ctrl = np.array([(-1.7, 2.2), (-2.5, 6.0), (-4.4, 12.0), (-6.3, 17.6), (-6.0, 19.5),
                     (-2.0, 20.2), (2.5, 20.0), (6.0, 19.0), (6.7, 16.8), (5.6, 12.5),
                     (3.5, 7.4), (2.0, 3.8), (1.6, 2.2)])
    outline = _smooth_closed(ctrl, 6)
    blade = plate(P, (0, 0, 0), I, outline, 0.3, round_=0.22, thick_fn=_thick)
    # bord dorsal légèrement renflé (insertion du cartilage scapulaire)
    dors = tube(P, [(-5.8, 19.1, 0.05), (-2.0, 19.85, 0.05), (2.5, 19.7, 0.05), (6.0, 18.7, 0.05)],
                [0.24, 0.26, 0.26, 0.22], k=0.4)
    blade = smin(blade, dors, 0.3)
    # galbe : fosse infra-épineuse et sous-scapulaire légèrement concaves
    blade = blade - 0.0
    # léger galbe : la lame est un peu creusée médialement
    blade = blade + 0.0  # (galbe appliqué par déformation ci-dessous)

    # épine : lame perpendiculaire, hauteur variable, tubérosité
    sp_a, sp_b = np.array([0.35, 3.2, 0.0]), np.array([-0.9, 19.6, 0.0])
    ax = (sp_b - sp_a) / np.linalg.norm(sp_b - sp_a)
    Rsp = np.stack([ax, np.array([0, 0, 1.0]), np.cross(ax, [0, 0, 1.0])])
    L = np.linalg.norm(sp_b - sp_a)
    sp_out = [(0.0, 0.0), (0.0, 0.6), (3.0, 1.4), (6.5, 2.35), (9.5, 2.25),
              (13.5, 1.0), (L, 0.45), (L, 0.0)]
    spine = plate(P, sp_a, Rsp, _smooth_open(sp_out, 5), 0.5, round_=0.2,
                  thick_fn=lambda u, v: 0.62 - 0.2 * np.clip(v / 2.0, 0, 1))
    # tubérosité de l'épine : bourrelet épais sur le bord libre, déversé caudalement
    nrm = np.cross(ax, [0, 0, 1.0])            # direction caudale du plan de l'épine
    tub = tube(P, [sp_a + ax * 4.2 + np.array([0, 0, 1.75]),
                   sp_a + ax * 6.6 + np.array([0, 0, 2.3]) + nrm * 0.45,
                   sp_a + ax * 9.0 + np.array([0, 0, 2.25]) + nrm * 0.9,
                   sp_a + ax * 11.8 + np.array([0, 0, 1.4]) + nrm * 0.4],
               [0.3, 0.55, 0.5, 0.25], k=0.5)
    spine = smin(spine, tub, 0.45)

    # col et cavité glénoïdale
    neck = tube(P, [(0.1, 4.2, 0.1), (0.15, 1.8, 0.15), (0.2, 0.4, 0.15)],
                [1.05, 1.25, 1.65], k=0.3,
                scale=[(1.45, (1, 0, 0))] * 3)
    glen_cup = ellipsoid(P, (0.15, -1.25, 0.15), (1.8, 1.4, 1.4))
    sgt = ellipsoid(P, (2.15, 1.25, 0.25), (0.7, 0.95, 0.65))        # tubercule supraglénoïdal
    cor = ellipsoid(P, (2.05, 1.25, -0.75), (0.45, 0.55, 0.4))       # processus coracoïde
    caud_ridge = tube(P, [(-1.75, 2.6, 0.1), (-3.0, 7.0, 0.05), (-4.9, 13.0, 0.0)],
                      [0.48, 0.42, 0.3], k=0.3)

    d = smin(blade, spine, 0.35)
    d = smin(d, neck, 0.8)
    d = smin(d, caud_ridge, 0.6)
    d = smin(d, sgt, 0.45)
    d = smin(d, cor, 0.3)
    d = ssub(d, glen_cup, 0.18)
    # trou nourricier près du col
    d = ssub(d, round_cone(P, (-1.2, 4.6, 0.6), (-1.0, 5.2, 0.0), 0.06, 0.05), 0.02)
    d = d + 0.02 * fbm(P, 1.8, 3, seed=21) + 0.008 * fbm(P, 8.0, 2, seed=2)
    return d
