"""Rendu de contrôle d'un ou plusieurs maillages sous 6 angles.

blender-python render_check.py <sortie.png> <titre> <fichier.ply> [...]
Vues : crâniale, caudale, latérale, médiale, proximale, 3/4.
"""
import sys, math, os
import bpy, bmesh
from mathutils import Vector

out, title, files = sys.argv[1], sys.argv[2], sys.argv[3:]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
objs = []
for f in files:
    bpy.ops.wm.ply_import(filepath=f, forward_axis="Y", up_axis="Z")
    o = bpy.context.selected_objects[0]
    objs.append(o)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    m = o.modifiers.new("lisse", "CORRECTIVE_SMOOTH")
    m.iterations = 4; m.smooth_type = "LENGTH_WEIGHTED"; m.use_only_smooth = True

mat = bpy.data.materials.new("os")
mat.use_nodes = True
nt = mat.node_tree
b = nt.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (0.86, 0.80, 0.68, 1)
b.inputs["Roughness"].default_value = 0.55
b.inputs["Subsurface Weight"].default_value = 0.08
b.inputs["Subsurface Radius"].default_value = (0.3, 0.2, 0.12)
tex = nt.nodes.new("ShaderNodeTexNoise"); tex.inputs["Scale"].default_value = 60; tex.inputs["Detail"].default_value = 8
bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.12
nt.links.new(tex.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 0.6
mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
mix.inputs["Factor"].default_value = 0.55
mix.inputs[6].default_value = (0.86, 0.80, 0.68, 1)
nt.links.new(ao.outputs["AO"], mix.inputs[7]); nt.links.new(mix.outputs[2], b.inputs["Base Color"])
for o in objs: o.data.materials.append(mat)

# boîte englobante
pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
ctr = (lo + hi) / 2; size = max(hi - lo)

world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.92, 0.93, 0.95, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
for rot, en in (((0.6, 0.2, 0.8), 3.5), ((-0.4, 0.3, -2.4), 1.2)):
    l = bpy.data.lights.new("l", "SUN"); l.energy = en; l.angle = 0.35
    lo_ = bpy.data.objects.new("l", l); lo_.rotation_euler = rot; sc.collection.objects.link(lo_)

cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = size * 1.12
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
sc.render.engine = "CYCLES"; sc.cycles.samples = 48; sc.cycles.use_denoising = True
sc.render.resolution_x = sc.render.resolution_y = 640
sc.view_settings.view_transform = "AgX"

# axes locaux : X crânial, Y proximal, Z latéral
views = {"craniale": (1, 0, 0), "caudale": (-1, 0, 0), "laterale": (0, 0, 1),
         "mediale": (0, 0, -1), "proximale": (0, 1, 0.001), "3/4": (0.7, 0.35, 0.65)}
labels = os.environ.get("LABELS")
if labels:
    views = dict(zip(labels.split(","), views.values()))
tmp = []
for i_v, (name, d) in enumerate(views.items()):
    d = Vector(d).normalized()
    co.location = ctr + d * size * 3
    up = Vector((0, 0, 1)) if i_v == 4 else Vector((0, 1, 0))
    fwd = (-d).normalized(); upv = up - fwd * up.dot(fwd); upv.normalize()
    right = fwd.cross(upv)
    from mathutils import Matrix
    M = Matrix((right, upv, -fwd)).transposed().to_4x4(); M.translation = co.location
    co.matrix_world = M
    p = f"{out}.{len(tmp)}.png"; sc.render.filepath = p
    bpy.ops.render.render(write_still=True); tmp.append((name, p))

from PIL import Image, ImageDraw
W = 640; sheet = Image.new("RGB", (W * 3, W * 2 + 40), (245, 245, 245))
dr = ImageDraw.Draw(sheet); dr.text((10, 10), title, fill=(20, 20, 20))
for i, (name, p) in enumerate(tmp):
    im = Image.open(p).convert("RGB"); x, y = (i % 3) * W, 40 + (i // 3) * W
    sheet.paste(im, (x, y)); dr.text((x + 10, y + 10), "vue " + name, fill=(30, 30, 30)); os.remove(p)
sheet.save(out); print("ok", out)
