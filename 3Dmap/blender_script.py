import bpy
from mathutils import Vector
import json
import sys
import os

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

def run():
    filepath = os.path.join(os.path.dirname(__file__), "test.json")
    
    data = None
    with open(filepath, "r") as f:
        data = json.loads(f.read())
    
    for area,polygons in data.items():
        me = bpy.data.meshes.new(area)
        ob = bpy.data.objects.new(area, me)
        
        bpy.context.scene.objects.link(ob)
        bpy.context.scene.objects.active = ob
    
        build_mesh(me, polygons)
