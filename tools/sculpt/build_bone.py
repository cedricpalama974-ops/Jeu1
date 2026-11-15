"""Construit un os : python build_bone.py <nom> <pas_cm> <sortie.ply>"""
import importlib, sys, time, os
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "bones"))
from sdf import mesh_sdf, write_ply

name, step, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
m = importlib.import_module(name)
t = time.time()
v, f, _ = mesh_sdf(m.sdf, *m.BBOX, step)
write_ply(out, v, f)
print(f"{name}: {len(v)} sommets, {len(f)} faces, {time.time()-t:.1f}s")
