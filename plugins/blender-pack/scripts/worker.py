"""Runs inside Blender; shared by batch and the live bridge."""
from __future__ import annotations
import json
import math
from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import bmesh
from mathutils import Vector
from common import read_json, write_json


def inspect_scene(max_triangles=None):
    objects = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            mesh.calc_loop_triangles()
            points = [evaluated.matrix_world @ v.co for v in mesh.vertices]
            bounds = {"min": [min(v[i] for v in points) for i in range(3)],
                      "max": [max(v[i] for v in points) for i in range(3)]} if points else None
            bm = bmesh.new()
            try:
                bm.from_mesh(mesh)
                nonmanifold = sum(not e.is_manifold for e in bm.edges)
                loose = sum(not v.link_edges for v in bm.verts)
            finally:
                bm.free()
            objects.append({"name": obj.name, "vertices": len(mesh.vertices),
                "triangles": len(mesh.loop_triangles), "nonmanifold_edges": nonmanifold,
                "loose_vertices": loose, "uv_layers": len(mesh.uv_layers),
                "materials": [m.name if m else None for m in obj.data.materials],
                "dimensions": [round(v, 6) for v in obj.dimensions],
                "world_bounds": bounds,
                "scale": list(obj.scale), "negative_scale": obj.matrix_world.determinant() < 0,
                "finite_vertices": all(math.isfinite(x) for v in mesh.vertices for x in v.co),
                "source_kind": obj.get("xgh_source_kind", "unknown"),
                "source_uri": obj.get("xgh_source_uri", ""),
                "source_license": obj.get("xgh_source_license", "")})
        finally:
            evaluated.to_mesh_clear()
    triangles = sum(obj["triangles"] for obj in objects)
    bounded = [o["world_bounds"] for o in objects if o["world_bounds"]]
    bounds = {"min": [min(b["min"][i] for b in bounded) for i in range(3)],
              "max": [max(b["max"][i] for b in bounded) for i in range(3)]} if bounded else None
    if bounds:
        bounds["dimensions"] = [bounds["max"][i] - bounds["min"][i] for i in range(3)]
    images = [{"name": img.name, "path": img.filepath,
               "missing": bool(img.source == "FILE" and not img.packed_file and not Path(bpy.path.abspath(img.filepath)).is_file())}
              for img in bpy.data.images if img.source == "FILE"]
    return {"blender": bpy.app.version_string, "file": bpy.data.filepath,
        "units": bpy.context.scene.unit_settings.system,
        "unit_scale": bpy.context.scene.unit_settings.scale_length,
        "mesh_objects": len(objects), "triangles": triangles, "objects": objects, "images": images,
        "world_bounds": bounds,
        "triangle_budget": max_triangles,
        "within_triangle_budget": None if max_triangles is None else triangles <= max_triangles,
        "visual_review": "not_performed", "engine_import": "not_performed",
        "note": "Nonmanifold edges can be intentional on open surfaces; UV and material requirements depend on the brief. Counts do not establish visual quality."}


def preview(job):
    scene = bpy.context.scene
    mesh_objects = [o for o in scene.objects if o.type == "MESH" and not o.hide_render]
    if not mesh_objects:
        raise ValueError("No visible mesh to preview")
    corners = [o.matrix_world @ Vector(c) for o in mesh_objects for c in o.bound_box]
    low = Vector([min(c[i] for c in corners) for i in range(3)])
    high = Vector([max(c[i] for c in corners) for i in range(3)])
    center = (low + high) / 2
    diameter = max((high - low).length, .1)
    camera = bpy.data.objects.new("XGH_ReviewCamera", bpy.data.cameras.new("XGH_ReviewCamera"))
    scene.collection.objects.link(camera)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = diameter * 1.15
    camera.data.clip_end = diameter * 20 + 100
    scene.camera = camera
    for name, offset, power in [("Key", (2, -3, 4), 1600), ("Fill", (-3, -1, 2), 900), ("Rim", (1, 3, 4), 1400)]:
        light = bpy.data.objects.new("XGH_" + name, bpy.data.lights.new("XGH_" + name, "AREA"))
        scene.collection.objects.link(light)
        light.location = center + Vector(offset) * diameter
        light.rotation_euler = (center - light.location).to_track_quat("-Z", "Y").to_euler()
        light.data.energy = power * diameter * diameter
        light.data.shape = "DISK"
        light.data.size = diameter * 2
    scene.world = bpy.data.worlds.new("XGH_ReviewWorld")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs[0].default_value = (.13, .15, .19, 1)
    scene.world.node_tree.nodes.get("Background").inputs[1].default_value = .5
    # CPU Cycles is portable on headless machines, without requiring a graphics context.
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 16
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    views = []
    for name, direction in [("front", (0, -1, .15)), ("side", (1, 0, .15)), ("back", (0, 1, .15)), ("top", (0, 0, 1)), ("hero", (1, -1.4, 1)), ("hero-left", (-1, -1.4, 1))]:
        camera.location = center + Vector(direction).normalized() * diameter * 3
        camera.rotation_euler = (center - camera.location).to_track_quat("-Z", "Y").to_euler()
        output = job / (name + ".png")
        scene.render.filepath = str(output)
        bpy.ops.render.render(write_still=True)
        views.append({"view": name, "path": str(output)})
    return views


def export_roundtrip(job, format):
    if format not in {"glb", "fbx"}:
        raise ValueError("Unsupported export format")
    before = inspect_scene()
    sources = job / "sources.json"
    write_json(sources, {"source_blend": before["file"], "objects": [
        {key: obj[key] for key in ("name", "source_kind", "source_uri", "source_license")}
        for obj in before["objects"]], "note": "Keep this sidecar with the export; interchange formats may drop custom properties."})
    path = job / ("asset." + format)
    if format == "glb":
        bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", export_cameras=False, export_lights=False, export_apply=True)
    else:
        bpy.ops.export_scene.fbx(filepath=str(path), object_types={"MESH", "ARMATURE", "EMPTY"}, add_leaf_bones=False)
    if not path.is_file() or not path.stat().st_size:
        raise RuntimeError("Export did not produce a nonempty file")
    # Current scene is a disposable batch copy. Read exported bytes, not the source scene.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if format == "glb":
        bpy.ops.import_scene.gltf(filepath=str(path))
    else:
        bpy.ops.import_scene.fbx(filepath=str(path))
    after = inspect_scene()
    result = {"path": str(path), "sources": str(sources), "bytes": path.stat().st_size, "before": before, "after": after,
              "reimport_has_meshes": after["mesh_objects"] > 0, "engine_import": "not_performed"}
    result["comparison"] = {
        "triangles_equal": before["triangles"] == after["triangles"],
        "bounds_match_1e_4": bool(before["world_bounds"] and after["world_bounds"] and all(
            abs(a-b) <= 1e-4 for key in ("min", "max")
            for a, b in zip(before["world_bounds"][key], after["world_bounds"][key]))),
        "materials_before": sorted({m for o in before["objects"] for m in o["materials"] if m}),
        "materials_after": sorted({m for o in after["objects"] for m in o["materials"] if m}),
        "visual_equivalence": "not_performed"}
    if after["mesh_objects"] == 0:
        raise RuntimeError("Export reimport contains no meshes")
    return result


def run(config):
    job = Path(config["job"])
    action = config["action"]
    if action == "build":
        # Expose explicit output and workspace paths; relative reads resolve from workspace.
        sys.argv = [config["script"]]
        runpy.run_path(str(job / "source.py"), init_globals={"XGH_OUTPUT": job, "XGH_WORKSPACE": Path(config["workspace"]), "XGH_SOURCE": config["script"]}, run_name="__main__")
        path = job / "scene.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path))
        result = {"blend": str(path), "inspection": inspect_scene(config.get("max_triangles"))}
    elif action == "inspect":
        result = inspect_scene(config.get("max_triangles"))
    elif action == "preview":
        result = {"views": preview(job), "note": "Review lighting only; input .blend was not saved or modified."}
    elif action == "export":
        result = export_roundtrip(job, config.get("format", "glb"))
    else:
        raise ValueError("Unsupported action")
    write_json(job / "result.json", result)


if __name__ == "__main__":
    run(read_json(sys.argv[sys.argv.index("--") + 1]))
