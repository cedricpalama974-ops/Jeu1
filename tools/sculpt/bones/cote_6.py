"""6ᵉ côte gauche (sternale) du porc charcutier, avec son cartilage.

Repère local : X = crânial, Y = dorsal, Z = latéral gauche.
L'origine est la tête de la côte, contre le corps vertébral.
Reliefs : tête à deux facettes et crête, col, tubercule articulaire,
angle, corps aplati et large ventralement, sillon costal caudal,
cartilage costal (texture distincte plus tard).
"""
import numpy as np
from sdf import smin, ssub, ellipsoid, sphere, tube, round_cone, fbm

BBOX = ((-3.0, -26.0, -1.2), (3.4, 2.5, 14.5))


def _arc(t):
    """Courbe moyenne de la côte (t de 0 à 1) : monte vers le tubercule,
    s'écarte latéralement puis descend et revient vers le sternum."""
    ang = np.pi * (0.06 + 0.9 * t)
    zz = 12.2 * np.sin(ang) ** 0.85 + 0.6
    yy = 1.2 - 24.0 * t ** 1.15 + 1.6 * np.sin(np.pi * t)
    xx = 0.9 * t + 0.35 * np.sin(np.pi * t * 2)
    return np.array([xx, yy, zz])


def sdf(P):
    ts = np.linspace(0.0, 0.8, 34)
    pts = [_arc(t) for t in ts]
    pts[0] = np.array([0.0, 0.0, 0.2])
    rad = np.interp(ts, [0, 0.05, 0.12, 0.3, 0.8], [0.55, 0.4, 0.5, 0.52, 0.58])
    # corps aplati : section elliptique, grand axe crânio-caudal
    sc = [(1.0 + 1.1 * min(1.0, t * 2.2), (1, 0, 0)) for t in ts]
    rib = tube(P, pts, rad, k=0.35, scale=sc)
    end = _arc(0.8)
    cpts = [end + np.array([0.5 * f, -2.6 * f - 0.8 * f * f, -3.6 * f]) for f in np.linspace(0, 1, 8)]
    cart = tube(P, cpts, np.linspace(0.56, 0.46, 8), k=0.3, scale=[(2.2, (1, 0, 0))] * 8)
    head = ellipsoid(P, (0.0, -0.05, -0.15), (0.75, 0.6, 0.55))
    crest = round_cone(P, (0.0, 0.25, -0.5), (0.0, -0.35, -0.5), 0.16, 0.16)
    tuber = sphere(P, _arc(0.1) + np.array([0.0, 0.42, -0.1]), 0.5)
    d = smin(rib, head, 0.3)
    d = smin(d, tuber, 0.25)
    d = smin(d, cart, 0.25)
    d = ssub(d, crest, -0.0) if False else d
    # deux facettes de la tête, séparées par la crête
    d = ssub(d, sphere(P, (0.55, 0.0, -0.75), 0.35), 0.05)
    d = ssub(d, sphere(P, (-0.55, 0.0, -0.75), 0.35), 0.05)
    # sillon costal (bord caudal, face médiale)
    groove = tube(P, [p + np.array([-1.0, 0, -0.3]) for p in pts[6:26:2]],
                  [0.12] * 10, k=0.15)
    d = ssub(d, groove, 0.06)
    d = d + 0.015 * fbm(P, 2.5, 3, seed=31)
    return d
