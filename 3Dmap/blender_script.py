import bpy
from mathutils import Vector
import json
import sys
import os

# Three.js blender export module 'export_threejs.py'
# needs THREE_exportGeometry custom property to be defined like this:
bpy.types.Object.THREE_exportGeometry = bpy.props.BoolProperty(default = True)
# The module is assumed to be in the same folder with this file.
sys.path.append(os.path.dirname(__file__))
import export_threejs


def clear_scene(scene):
    for object in scene.objects:
        object.select = True
    bpy.ops.object.delete()

    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)


def get_data(shp_path, python_path):
    path = os.path.dirname(__file__)
    path = os.path.join(path, "shp2json.py")

    with os.popen(python_path + " " + path + " " + shp_path) as f:
        return json.loads(f.read())


def separate_substracting_regions(regions):
    substracting = []
    num_regions = len(regions)
    for i in range(0, num_regions):
        region = regions[i]
        last_point = len(region) - 1
        pt1 = region[last_point]
        pt2 = region[0]
        sum = (pt2[0] - pt1[0]) * (pt2[1] + pt1[1])
        for j in range(0, last_point): # we dont want to add last edge twice
            pt1 = region[j]
            pt2 = region[j + 1]
            sum = sum + (pt2[0] - pt1[0]) * (pt2[1] + pt1[1])
        if sum < 0:
            substracting.append(i)
    
    regions_sub = []
    regions_normal = []
    for i in range(0, num_regions):
        if i in substracting:
            regions_sub.append(regions[i])
        else:
            regions_normal.append(regions[i])
    return (regions_normal, regions_sub)


def build_mesh(mesh, regions, height):
    extrude_vec = Vector((0.0, 0.0, height))
    
    verts = []
    edges = []
    
    for region in regions:
        first = len(verts)
        for pt in region:
            index = len(verts)
            verts.append((pt[0], pt[1], 0.0))
            edges.append([index, index + 1])
        last = len(edges) - 1
        edges[last][1] = first

    mesh.from_pydata(verts, edges,[])
    
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={"value":extrude_vec})
    bpy.ops.mesh.edge_face_add()
    bpy.ops.mesh.select_all(action='SELECT')
    if height > 1.0: # TODO: fix this
        bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.quads_convert_to_tris()
    bpy.ops.object.mode_set(mode = 'OBJECT')


def boolean_substract(object, object_sub):
    bpy.context.scene.objects.active = object
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
    bpy.context.object.modifiers["Boolean"].object = object_sub
    bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Boolean")


def delete_sub_objects(scene):
    for object in scene.objects:
        if object.name.endswith("_sub"):
            object.select = True
    bpy.ops.object.delete()

    for mesh in bpy.data.meshes:
        try:
            bpy.data.meshes.remove(mesh)
        except:
            pass


def create_scene(scene, data):
    for country in data:
        name = country[0]
        regions = country[1]
        
        regions_normal, regions_sub = separate_substracting_regions(regions)

        mesh = bpy.data.meshes.new(name)
        object = bpy.data.objects.new(name, mesh)
        
        scene.objects.link(object)
        scene.objects.active = object

        build_mesh(mesh, regions_normal, 1.0)
        
        if len(regions_sub) > 0:
            mesh_sub = bpy.data.meshes.new(name + "_sub")
            object_sub = bpy.data.objects.new(name + "_sub", mesh_sub)
            
            scene.objects.link(object_sub)
            scene.objects.active = object_sub

            build_mesh(mesh_sub, regions_sub, 1.5)
            
            boolean_substract(object, object_sub)
    
    delete_sub_objects(scene)


def export_scene(scene, path):
    data = []

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

        #data[object.name] = json.loads(text)
        data.append((object.name, json.loads(text)))

        dir, _ = os.path.split(path)
        if not os.path.isdir(dir):
            os.makedirs(dir)

    with open(path, "w") as f:
        f.write(json.dumps(data, separators=(",", ":")))


def run(shp_file, out_file, python_path):
    data = get_data(shp_file, python_path)
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
elif argc < 4:
    print("Give path to python as 3rd argument")
else:
    run(argv[1], argv[2], argv[3])

