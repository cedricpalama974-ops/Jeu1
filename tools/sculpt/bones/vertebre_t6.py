"""Vertèbre thoracique T6 du porc charcutier.

Repère local : X = crânial, Y = dorsal, Z = gauche.
Reliefs : corps (tête convexe, fosse concave), fovéas costales crâniales et
caudales, pédicules avec foramen vertébral latéral (caractère du porc),
lame, foramen vertébral, processus épineux haut incliné caudalement à
sommet épaissi, processus transverses avec fovéa costale et processus
mamillaire, processus articulaires crâniaux (facettes dorsales) et caudaux.
"""
import numpy as np
from sdf import smin, ssub, smax, ellipsoid, sphere, tube, round_cone, box, frame, plate, fbm

BBOX = ((-4.6, -1.6, -3.3), (2.6, 10.2, 3.3))


def sdf(P):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    # corps : cylindre court à section en cœur (aplati dorsalement)
    body = tube(P, [(-1.25, 0.0, 0.0), (1.25, 0.0, 0.0)], [1.3, 1.3], k=0)
    body = smax(body, -(y + 1.15), 0.3)                 # face ventrale aplatie
    crest = round_cone(P, (-1.0, -1.05, 0), (1.0, -1.1, 0), 0.25, 0.25)
    body = smin(body, crest, 0.4)
    taille = 0.18 * np.exp(-(x / 0.9) ** 2)             # taille du corps
    body = body + taille
    head = sphere(P, (0.75, 0.05, 0), 1.25)             # tête légèrement convexe
    body = smin(body, smax(head, -(x - 1.2), 0.1), 0.3)
    fossa = sphere(P, (-2.35, 0.1, 0), 1.25)            # fosse caudale concave
    body = ssub(body, fossa, 0.15)

    # arc vertébral : deux pédicules + lame, plus court que le corps
    canal = tube(P, [(-3.0, 1.7, 0.0), (3.0, 1.7, 0.0)], [0.8, 0.8])
    ped = None
    for s in (-1, 1):
        pd = box(P, (0.0, 1.35, 1.0 * s), (0.85, 0.75, 0.32), r=0.25)
        ped = pd if ped is None else smin(ped, pd, 0)
    lamina = box(P, (-0.15, 2.45, 0.0), (1.0, 0.32, 1.25), r=0.25)
    arch = smin(ped, lamina, 0.4)
    arch = ssub(arch, canal, 0.12)
    # échancrures vertébrales crâniale et caudale (trous de conjugaison)
    notch_cr = tube(P, [(1.15, 1.05, -2.0), (1.15, 1.05, 2.0)], [0.38, 0.38])
    notch_cd = tube(P, [(-1.15, 1.05, -2.0), (-1.15, 1.05, 2.0)], [0.5, 0.5])
    arch = ssub(arch, smin(notch_cr, notch_cd, 0), 0.15)
    # foramen vertébral latéral (porc)
    lat_for = tube(P, [(0.05, 1.45, -2.0), (0.05, 1.45, 2.0)], [0.16, 0.16])

    # processus épineux : lame inclinée caudalement, sommet renflé
    Rs = frame((0.0, 1.0, 0.0), (1.0, 0.0, 0.0))
    tilt = np.radians(18)
    ax = np.array([-np.sin(tilt), np.cos(tilt), 0.0])
    cr = np.array([np.cos(tilt), np.sin(tilt), 0.0])
    Rsp = np.stack([cr, ax, np.cross(cr, ax)])
    outline = [(-1.0, 2.3), (1.05, 2.3), (0.75, 6.0), (0.85, 9.6), (-0.8, 9.6), (-0.95, 6.0)]
    spine = plate(P, (0.0, 0.0, 0.0), Rsp, outline, 0.42, round_=0.18,
                  thick_fn=lambda u, v: 0.32 + 0.22 * np.clip((v - 7.5) / 2.0, 0, 1)
                  + 0.12 * np.clip((3.0 - v) / 1.0, 0, 1) + 0.08 * np.clip(-u, 0, 1))
    summit = round_cone(P, ax * 9.35 + cr * -0.75, ax * 9.45 + cr * 0.8, 0.32, 0.3)
    spine = smin(spine, summit, 0.3)

    # processus transverses (dorso-latéraux) avec fovéa costale
    tps = None
    for s in (-1, 1):
        tp = round_cone(P, (-0.1, 2.0, 0.6 * s), (-0.3, 2.45, 2.25 * s), 0.55, 0.48)
        mam = ellipsoid(P, (0.35, 2.85, 1.5 * s), (0.45, 0.32, 0.3))   # processus mamillaire
        tp = smin(tp, mam, 0.3)
        fov = sphere(P, (0.2, 2.15, 2.75 * s), 0.38)                    # fovéa du processus transverse
        tp = ssub(tp, fov, 0.08)
        tps = tp if tps is None else smin(tps, tp, 0)
    # processus articulaires crâniaux (facettes regardant dorsalement)
    acr = None
    for s in (-1, 1):
        a = ellipsoid(P, (1.3, 2.35, 0.75 * s), (0.6, 0.28, 0.5))
        acr = a if acr is None else smin(acr, a, 0)
    # processus articulaires caudaux (sous l'épine, facettes ventrales)
    acd = None
    for s in (-1, 1):
        a = ellipsoid(P, (-1.35, 2.6, 0.55 * s), (0.6, 0.3, 0.45))
        acd = a if acd is None else smin(acd, a, 0)

    d = smin(body, arch, 0.45)
    d = smin(d, spine, 0.5)
    d = smin(d, tps, 0.4)
    d = smin(d, acr, 0.3)
    d = smin(d, acd, 0.3)
    d = ssub(d, canal, 0.12)
    d = ssub(d, lat_for, 0.06)
    # fovéas costales du corps (crâniale et caudale, de chaque côté)
    for s in (-1, 1):
        d = ssub(d, sphere(P, (1.25, 0.75, 1.15 * s), 0.42), 0.06)
        d = ssub(d, sphere(P, (-1.3, 0.75, 1.15 * s), 0.38), 0.06)
    d = d + 0.02 * fbm(P, 2.2, 3, seed=3) + 0.008 * fbm(P, 9.0, 2, seed=8)
    return d
