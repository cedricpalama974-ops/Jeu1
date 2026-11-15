"""Bibliothèque de sculpture par champs de distance signée (SDF).

Chaque os est décrit comme une composition de volumes élémentaires (têtes,
fûts à section variable, lames, crêtes) fusionnés par union lisse, creusés
par soustraction lisse (fosses, foramens) puis légèrement déformés par un
bruit basse fréquence pour casser la régularité géométrique.
Le champ est échantillonné sur une grille fine (0,5 à 0,8 mm) et converti en
maillage par marching cubes ; Blender se charge ensuite du lissage, de la
retopologie, des UV, de la cuisson et du rendu.

Unités : centimètres.
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------- utilitaires

def _v(p):
    return np.asarray(p, dtype=np.float64)


def smin(a, b, k):
    """Union lisse polynomiale (rayon de raccord k)."""
    if k <= 0:
        return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def ssub(a, b, k):
    """a privé de b, raccord lisse."""
    return smax(a, -b, k)


def frame(axis_x, axis_y):
    """Repère orthonormé à partir de deux directions approximatives."""
    x = _v(axis_x) / np.linalg.norm(axis_x)
    y = _v(axis_y) - np.dot(axis_y, x) * x
    y /= np.linalg.norm(y)
    z = np.cross(x, y)
    return np.stack([x, y, z])


def to_local(P, origin, R):
    """Coordonnées de P (N×3) dans le repère (origin, R lignes = axes)."""
    return (P - _v(origin)) @ R.T


# ---------------------------------------------------------------- primitives

def sphere(P, c, r):
    return np.linalg.norm(P - _v(c), axis=1) - r


def ellipsoid(P, c, radii, R=None):
    q = P - _v(c)
    if R is not None:
        q = q @ R.T
    r = _v(radii)
    k0 = np.linalg.norm(q / r, axis=1)
    k1 = np.linalg.norm(q / (r * r), axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def round_cone(P, a, b, ra, rb):
    """Segment ab à rayon variant linéairement de ra à rb."""
    a, b = _v(a), _v(b)
    ba = b - a
    l2 = float(np.dot(ba, ba))
    pa = P - a
    t = np.clip(pa @ ba / l2, 0.0, 1.0)
    d = np.linalg.norm(pa - t[:, None] * ba, axis=1)
    return d - (ra + (rb - ra) * t)


def tube(P, pts, radii, k=0.0, scale=None):
    """Fût le long d'une polyligne avec rayons par point.

    scale : facteurs (sy, sz) appliqués à la section dans un repère local
    approximatif (aplatissement en ellipse) — optionnel, par point.
    """
    pts = [_v(p) for p in pts]
    d = None
    for i in range(len(pts) - 1):
        if scale is None:
            di = round_cone(P, pts[i], pts[i + 1], radii[i], radii[i + 1])
        else:
            di = _flat_cone(P, pts[i], pts[i + 1], radii[i], radii[i + 1],
                            scale[i], scale[i + 1])
        d = di if d is None else smin(d, di, k)
    return d


def _flat_cone(P, a, b, ra, rb, sa, sb):
    """Cône à section elliptique ; s = (facteur, direction du grand axe)."""
    ba = b - a
    l2 = float(np.dot(ba, ba))
    pa = P - a
    t = np.clip(pa @ ba / l2, 0.0, 1.0)
    q = pa - t[:, None] * ba
    fa, ua = sa
    fb, ub = sb
    u = _v(ua) * (1 - t)[:, None] + _v(ub) * t[:, None]
    u -= (u @ ba / l2)[:, None] * ba
    u /= np.maximum(np.linalg.norm(u, axis=1), 1e-9)[:, None]
    f = fa + (fb - fa) * t
    qu = np.sum(q * u, axis=1)
    qv = q - qu[:, None] * u
    # on dilate la composante selon u : le cercle devient ellipse (f×r, r)
    dist = np.sqrt((qu / f) ** 2 + np.sum(qv * qv, axis=1))
    r = ra + (rb - ra) * t
    return (dist - r) * np.minimum(f, 1.0)


def box(P, c, half, R=None, r=0.0):
    q = P - _v(c)
    if R is not None:
        q = q @ R.T
    q = np.abs(q) - (_v(half) - r)
    out = np.linalg.norm(np.maximum(q, 0.0), axis=1)
    inn = np.minimum(np.max(q, axis=1), 0.0)
    return out + inn - r


def plane(P, point, normal):
    n = _v(normal) / np.linalg.norm(normal)
    return (P - _v(point)) @ n


def torus(P, c, R_axes, major, minor):
    q = to_local(P, c, R_axes)
    xz = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2) - major
    return np.sqrt(xz ** 2 + q[:, 1] ** 2) - minor


# ------------------------------------------------- lames (os plats, épines)

def polygon2d(px, py, poly):
    """Distance signée à un polygone 2D (négatif dedans)."""
    poly = _v(poly)
    n = len(poly)
    d = np.full(px.shape, np.inf)
    s = np.ones(px.shape)
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        e = b - a
        wx, wy = px - a[0], py - a[1]
        t = np.clip((wx * e[0] + wy * e[1]) / float(e @ e), 0, 1)
        dx, dy = wx - t * e[0], wy - t * e[1]
        d = np.minimum(d, dx * dx + dy * dy)
        c1 = py >= a[1]
        c2 = py < b[1]
        c3 = e[0] * wy > e[1] * wx
        flip = (c1 & c2 & c3) | (~c1 & ~c2 & ~c3)
        s = np.where(flip, -s, s)
    return s * np.sqrt(d)


def plate(P, origin, R, outline, thick, round_=0.15, thick_fn=None):
    """Lame : contour 2D (dans le plan x,y local) extrudé sur l'épaisseur z.

    thick_fn(x, y) peut moduler l'épaisseur (bords amincis, renflements).
    """
    q = to_local(P, origin, R)
    d2 = polygon2d(q[:, 0], q[:, 1], outline)
    h = thick * 0.5 if thick_fn is None else thick_fn(q[:, 0], q[:, 1]) * 0.5
    dz = np.abs(q[:, 2]) - h
    w = np.stack([d2 + round_, dz + round_], axis=1)
    out = np.linalg.norm(np.maximum(w, 0.0), axis=1)
    inn = np.minimum(np.max(w, axis=1), 0.0)
    return out + inn - round_


# ------------------------------------------------------------- déformation

def _hash3(ix, iy, iz, seed):
    h = (ix * 73856093) ^ (iy * 19349663) ^ (iz * 83492791) ^ (seed * 2654435761)
    h = (h ^ (h >> 13)) * 1274126177
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0 * 2.0 - 1.0


def value_noise(P, freq, seed=0):
    q = P * freq
    i = np.floor(q).astype(np.int64)
    f = q - i
    u = f * f * (3 - 2 * f)
    res = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = ((u[:, 0] if dx else 1 - u[:, 0]) *
                     (u[:, 1] if dy else 1 - u[:, 1]) *
                     (u[:, 2] if dz else 1 - u[:, 2]))
                res = res + w * _hash3(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return res


def fbm(P, freq, octaves=3, seed=0):
    s, a, f = 0.0, 1.0, freq
    for o in range(octaves):
        s = s + a * value_noise(P, f, seed + o)
        a *= 0.5
        f *= 2.03
    return s


# ------------------------------------------------------------ maillage

def mesh_sdf(fn, bmin, bmax, step, chunk=2_000_000):
    """Échantillonne fn sur une grille et extrait l'isosurface 0."""
    from skimage.measure import marching_cubes

    bmin, bmax = _v(bmin), _v(bmax)
    n = np.ceil((bmax - bmin) / step).astype(int) + 1
    xs = [bmin[i] + np.arange(n[i]) * step for i in range(3)]
    vol = np.empty(n, dtype=np.float32)
    X, Y = np.meshgrid(xs[0], xs[1], indexing="ij")
    XY = np.stack([X.ravel(), Y.ravel()], axis=1)
    per = max(1, chunk // len(XY))
    for z0 in range(0, n[2], per):
        zs = xs[2][z0:z0 + per]
        P = np.concatenate([np.column_stack([XY, np.full(len(XY), z)]) for z in zs])
        vol[:, :, z0:z0 + len(zs)] = fn(P).reshape(len(zs), n[0], n[1]).transpose(1, 2, 0)
    verts, faces, normals, _ = marching_cubes(vol, 0.0, spacing=(step, step, step))
    return verts + bmin, faces, normals


def write_ply(path, verts, faces):
    with open(path, "wb") as f:
        f.write((
            "ply\nformat binary_little_endian 1.0\n"
            f"element vertex {len(verts)}\nproperty float x\nproperty float y\nproperty float z\n"
            f"element face {len(faces)}\nproperty list uchar int vertex_indices\nend_header\n"
        ).encode())
        f.write(verts.astype("<f4").tobytes())
        fa = np.empty(len(faces), dtype=[("n", "u1"), ("i", "<i4", 3)])
        fa["n"] = 3
        fa["i"] = faces
        f.write(fa.tobytes())
