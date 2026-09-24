"""Parametric 1m supply crate. No external assets; run through runner build."""
import bpy

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1


def material(name, color, metallic=0):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Metallic"].default_value = metallic
    shader.inputs["Roughness"].default_value = .4
    return mat


paint = material("Teal enamel", (.035, .27, .26))
metal = material("Dark frame", (.075, .09, .11), .65)
accent = material("Amber latch", (.95, .44, .055), .35)


def box(name, position, dimensions, mat, bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    obj["xgh_source_kind"] = "modeled"
    obj["xgh_source_uri"] = "XGameHarness/blender-pack/examples/crate.py"
    obj["xgh_source_license"] = "original-example"
    mod = obj.modifiers.new("Edge bevel", "BEVEL")
    mod.width, mod.segments = bevel, 2
    return obj


box("Body", (0, 0, .42), (.94, .68, .78), paint, .025)
box("Lid", (0, 0, .87), (1, .74, .12), paint, .018)
for x in (-.46, .46):
    for y in (-.33, .33):
        box("Corner rail", (x, y, .43), (.08, .08, .86), metal)
for z in (.09, .73):
    for y in (-.35, .35):
        box("Cross rail", (0, y, z), (.98, .045, .07), metal)
for x in (-.26, .26):
    box("Front latch", (x, -.38, .81), (.10, .055, .20), accent)
for side in (-1, 1):
    for y in (-.13, .13):
        box("Handle mount", (side * .515, y, .61), (.13, .055, .065), metal)
    box("Handle grip", (side * .58, 0, .61), (.04, .31, .055), metal)
