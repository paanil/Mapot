import bpy
from mathutils import Vector

def create_mesh(coords):
	extrudeVec = Vector((0.0, 0.0, 1.0))

	me = bpy.data.meshes.new("MyMesh")
	ob = bpy.data.objects.new("MyObject", me)
	bpy.context.scene.objects.link(ob)
	
	edges = []
	num_coords = len(coords)
	for i in xrange(0, num_coords - 1):
		edges.append((i, i + 1))
	edges.append(num_coords - 1, 0)

	me.from_pydata(coords, edges,[])
	
	bpy.context.scene.objects.active = ob
	bpy.ops.object.mode_set(mode = 'EDIT')
	bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":extrudeVec})
	bpy.ops.mesh.fill()

def run():
	coords=[(-1.0, -1.0, 0.0), (1.0, -1.0, 0.0), (1.0, 1.0 ,0.0), (-1.0, 1.0,0.0)]
	create_mesh(coords)