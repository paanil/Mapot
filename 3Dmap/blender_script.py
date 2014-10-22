import bpy
from mathutils import Vector
import json
import sys
import os

sys.path.append(os.path.dirname(__file__))

import export_threejs

def export(path):
    save_path = os.path.dirname(path)
    sce = bpy.context.scene
    
    data = {}
    for ob in sce.objects:
        filepath = os.path.join(save_path, ob.name + ".js")
        
        text, model_string = export_threejs.generate_mesh_string([ob], sce,
            True, # option_vertices
            False, # option_vertices_truncate
            True, # option_faces
            False, # option_normals
            False, # option_uv_coords
            False, # option_materials
            False, # option_colors
            False, # option_bones
            False, # option_skinning
            "None", # align_model
            True, # flipyz
            1.0, # option_scale
            True, # export_single_model
            False, # option_copy_textures
            filepath, # filepath
            False, # option_animation_morph
            False, # option_animation_skeletal
            False, # option_frame_index_as_time
            1) # option_frame_step
    
        data[ob.name] = json.loads(text)
     
    with open(path, "w") as f:
        f.write(json.dumps(data, separators=(",", ":")))

def build_mesh(me, polygons):
    extrudeVec = Vector((0.0, 0.0, 1.0))
    
    coords = []
    edges = []
    
    for points in polygons:
        first = len(coords)
        for co in points:
            index = len(coords)
            coords.append((co[0], co[1], 0.0))
            edges.append([index, index + 1])
        last = len(edges) - 1
        edges[last][1] = first

    me.from_pydata(coords, edges,[])
    
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.extrude_edges_move(TRANSFORM_OT_translate={"value":extrudeVec})
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.mode_set(mode = 'OBJECT')

def clear_scene():
    for ob in bpy.context.scene.objects:
        ob.select = True
    
    bpy.ops.object.delete()
    
    for me in bpy.data.meshes:
        bpy.data.meshes.remove(me)
    
def run():
    #filepath = os.path.join(os.path.dirname(__file__), "test.json")
    
    #data = shp2threejs.get_shapes_of_countries(19, "C:\\MyTemp\\ne_110m_admin_0_countries\\ne_110m_admin_0_countries.shp")
    
    if len(sys.argv) < 2:
        print("Give .shp file as argument")
        return
    
    
    shp_path = sys.argv[1]#"C:\\MyTemp\\ne_110m_admin_0_countries\\ne_110m_admin_0_countries.shp"
    
    sys.stderr.write(shp_path)
    
    clear_scene()
    
    #with open("c:\\mytemp\\data.json", "r") as f:
    #    data = json.loads(f.read())
    
    f = os.popen("python shp2threejs.py " + shp_path)
    data = json.loads(f.read())
    f.close()
    
    for country in data:
        area = country[0]
        polygons = country[1]
        
        me = bpy.data.meshes.new(area)
        ob = bpy.data.objects.new(area, me)
        
        bpy.context.scene.objects.link(ob)
        bpy.context.scene.objects.active = ob
    
        build_mesh(me, polygons)
    
    export("kala.json")

run()