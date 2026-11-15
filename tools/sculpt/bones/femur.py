"""Fémur gauche du porc charcutier (~110 kg).

Repère local : Y = axe long (0 = bas des condyles, + = proximal),
X = crânial, Z = latéral (+) / médial (−).
Longueur trochanter–condyles ≈ 21 cm ; tête ≈ 3,6 cm de diamètre.
Reliefs : tête et fovéa, col, grand trochanter et fosse trochantérique,
crête intertrochantérique, petit trochanter, trou nourricier, trochlée à
deux lèvres, condyles et fosse intercondylaire, épicondyles, fosse
d'extension, fosse supracondylaire.
"""
import numpy as np
from sdf import (smin, smax, ssub, ellipsoid, sphere, tube, round_cone, frame,
                 fbm, box)

BBOX = ((-4.2, -0.5, -5.2), (4.2, 22.0, 3.8))


def sdf(P):
    x, y, z = P[:, 0], P[:, 1], P[:, 2]

    # ---------------------------------------------------- diaphyse
    shaft = tube(
        P,
        [(-0.1, 3.6, 0.0), (0.15, 6.5, 0.0), (0.3, 10.5, 0.0),
         (0.25, 14.5, 0.0), (0.0, 17.2, -0.3)],
        [1.55, 1.3, 1.22, 1.3, 1.55], k=0.8)
    # ligne âpre caudale (léger relief rugueux)
    aspera = round_cone(P, (-1.15, 6.0, 0.35), (-1.2, 15.2, -0.35), 0.22, 0.26)
    shaft = smin(shaft, aspera, 0.45)

    # ---------------------------------------------------- extrémité distale
    # massif épiphysaire, aplati crânio-caudalement vers le haut
    distal = ellipsoid(P, (0.15, 2.7, 0.0), (2.25, 2.4, 2.35))
    # trochlée : bloc crânial en forme de poulie (cylindre d'axe ~Z)
    Rt = frame((0.25, 1, 0), (1, 0, 0))   # axe long de la trochlée ~ Y incliné
    troch_body = ellipsoid(P, (1.3, 2.9, -0.05), (2.3, 1.15, 1.75),
                           frame((0.15, 1, 0), (1, 0, 0)))
    groove = tube(P, [(3.15, 0.9, -0.08), (3.15, 3.0, -0.05), (2.75, 5.3, -0.05)],
                  [0.62, 0.66, 0.42], k=0.2)
    # lèvres (la médiale un peu plus forte)
    lip_m = tube(P, [(2.2, 1.1, -1.25), (2.75, 3.0, -1.2), (2.35, 5.2, -0.9)],
                 [0.55, 0.62, 0.3], k=0.3)
    lip_l = tube(P, [(2.2, 1.2, 1.1), (2.7, 3.0, 1.05), (2.3, 5.0, 0.85)],
                 [0.5, 0.58, 0.28], k=0.3)
    troch = smin(smin(troch_body, lip_m, 0.4), lip_l, 0.4)
    troch = ssub(troch, groove, 0.3)

    # condyles caudaux (ellipsoïdes inclinés), fosse intercondylaire
    Rc = frame((1, -0.35, 0), (0, 1, 0))
    cond_m = ellipsoid(P, (-0.75, 1.2, -1.32), (1.65, 1.25, 0.95), Rc)
    cond_l = ellipsoid(P, (-0.75, 1.25, 1.22), (1.6, 1.22, 0.9), Rc)
    # échancrure intercondylaire : ouverte en bas et en arrière
    notch = tube(P, [(-2.8, -0.6, 0.0), (-1.4, 0.3, 0.0), (-0.1, 0.9, 0.0)],
                 [0.62, 0.55, 0.38], k=0.25)
    epi_m = ellipsoid(P, (-0.25, 2.3, -2.0), (1.15, 1.0, 0.42))
    epi_l = ellipsoid(P, (-0.2, 2.5, 1.95), (1.1, 1.0, 0.4))
    ext_fossa = ellipsoid(P, (1.25, 1.9, 2.05), (0.42, 0.38, 0.3))
    supra = ellipsoid(P, (-1.95, 5.0, 0.85), (0.45, 1.0, 0.55))
    # face poplitée légèrement creuse
    popl = ellipsoid(P, (-2.35, 4.2, -0.1), (0.5, 1.4, 1.1))

    d = smin(shaft, distal, 1.4)
    d = smin(d, troch, 0.9)
    d = smin(d, smin(cond_m, cond_l, 0.25), 0.7)
    d = smin(d, smin(epi_m, epi_l, 0.2), 0.5)
    d = ssub(d, notch, 0.25)
    d = ssub(d, ext_fossa, 0.15)
    d = ssub(d, supra, 0.4)
    d = ssub(d, popl, 0.6)

    # ---------------------------------------------------- extrémité proximale
    head_c = np.array([0.35, 19.65, -2.55])
    head = sphere(P, head_c, 1.8)
    # col court, net : la tête déborde (lèvre de la tête)
    neck = round_cone(P, (0.15, 18.4, -0.9), head_c + (0.0, -0.25, 0.9), 1.25, 1.15)
    fovea = ellipsoid(P, head_c + np.array([-0.25, -0.75, -1.62]), (0.28, 0.5, 0.16),
                      frame((0, 1, 0), (1, 0, 0)))

    prox = ellipsoid(P, (-0.05, 17.4, -0.2), (1.85, 2.4, 1.85))
    # grand trochanter : lame épaisse latérale, sommet au niveau de la tête,
    # bord caudal recourbé médialement
    Rg = frame((1, 0.25, 0), (0, 1, 0))
    gt_main = ellipsoid(P, (0.2, 19.55, 1.25), (2.0, 1.7, 0.78), Rg)
    gt_hook = ellipsoid(P, (-1.25, 20.25, 0.55), (0.75, 1.15, 0.85))
    gt_top = round_cone(P, (1.2, 20.5, 1.2), (-1.3, 21.0, 0.75), 0.5, 0.62)
    gt = smin(smin(gt_main, gt_hook, 0.4), gt_top, 0.5)
    tfossa = ellipsoid(P, (-1.35, 19.2, -0.35), (0.7, 1.25, 0.72))
    itc = tube(P, [(-1.5, 20.0, 0.7), (-1.6, 17.8, 0.1), (-1.5, 16.0, -0.85)],
               [0.42, 0.4, 0.36], k=0.3)
    lt = ellipsoid(P, (-1.3, 15.7, -1.2), (0.62, 0.95, 0.55))

    d = smin(d, prox, 1.2)
    d = smin(d, neck, 0.45)
    d = smin(d, head, 0.18)
    d = smin(d, gt, 0.6)
    d = smin(d, itc, 0.35)
    d = smin(d, lt, 0.4)
    d = ssub(d, tfossa, 0.3)
    d = ssub(d, fovea, 0.12)

    # trou nourricier
    nut = round_cone(P, (-1.25, 12.0, 0.3), (-0.55, 12.8, 0.2), 0.07, 0.06)
    d = ssub(d, nut, 0.02)

    # micro-relief : plus marqué hors surfaces articulaires
    artic = np.minimum.reduce([
        np.linalg.norm(P - head_c, axis=1) - 2.1,
        np.abs(x - 2.4) + np.abs(y - 3.0) * 0.6 - 1.6,
        np.abs(x + 0.75) + np.abs(y - 1.2) - 1.8])
    rough = np.clip(artic / 0.6, 0.15, 1.0)
    d = d + rough * 0.03 * fbm(P, 1.6, 3, seed=11) + 0.012 * fbm(P, 7.0, 2, seed=5)
    return d
