import bpy
from mathutils import Vector
import json
import sys
import os

# Three.js blender export module 'export_threejs.py'
# note: - it is assumed to be in the same folder with this file
#       - it must define THREE_exportGeometry custom property like this:
# bpy.types.Object.THREE_exportGeometry = bpy.props.BoolProperty(default = True)
#       - add this definition in it or our script won't work
sys.path.append(os.path.dirname(__file__))
import export_threejs


def clear_scene(scene):
    for object in scene.objects:
        object.select = True
    bpy.ops.object.delete()

    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)


def get_data(shp_path):
    path = os.path.dirname(__file__)
    path = os.path.join(path, "shp2threejs.py")
    with os.popen("python " + path + " " + shp_path) as f:
        return json.loads(f.read())


def build_mesh(mesh, regions):
    extrude_vec = Vector((0.0, 0.0, 1.0))
    
    verts = []
    edges = []
    
    for pointset in regions:
        first = len(verts)
        for pt in pointset:
            index = len(verts)
            verts.append((pt[0], pt[1], 0.0))
            edges.append([index, index + 1])
        last = len(edges) - 1
        edges[last][1] = first

    mesh.from_pydata(verts, edges,[])
    
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={"value":extrude_vec})
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode = 'OBJECT')


def create_scene(scene, data):
    for country in data:
        name = country[0]
        regions = country[1]

        mesh = bpy.data.meshes.new(name)
        object = bpy.data.objects.new(name, mesh)

        scene.objects.link(object)
        scene.objects.active = object

        build_mesh(mesh, regions)


def export_scene(scene, path):
    data = {}

    for object in scene.objects:
        file = object.name + ".js"

        text = export_threejs.generate_mesh_string([object], scene,
            True,   # option_vertices
            False,  # option_vertices_truncate
            True,   # option_faces
            False,  # option_normals
            False,  # option_uv_coords
            False,  # option_materials
            False,  # option_colors
            False,  # option_bones
            False,  # option_skinning
            "None", # align_model
            True,   # flipyz
            1.0,    # option_scale
            True,   # export_single_model
            False,  # option_copy_textures
            file,   # filepath
            False,  # option_animation_morph
            False,  # option_animation_skeletal
            False,  # option_frame_index_as_time
            1)[0]   # option_frame_step

        data[object.name] = json.loads(text)

    with open(path, "w") as f:
        f.write(json.dumps(data, separators=(",", ":")))


def run(shp_file, out_file):
    data = get_data(shp_file)
    scene = bpy.context.scene
    clear_scene(scene)
    create_scene(scene, data)
    export_scene(scene, out_file)


argv = sys.argv
argc = len(argv)
try:
    argv = argv[argv.index("--"):]
    argc = len(argv)
except ValueError:
    pass

if argc < 2:
    print("Give .shp file as 1st argument")
elif argc < 3:
    print("Give output file as 2nd argument")
else:
    run(argv[1], argv[2])
