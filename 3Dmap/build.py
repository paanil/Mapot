import urllib.request
from zipfile import ZipFile
import tempfile
import os
import sys
from optparse import OptionParser


help = "Usage: build.py [path to blender] \n" + \
       "Path to blender is optional if blender is in path."
parser = OptionParser()
parser.add_option("-p", "--path-to-python", dest="python", default="python")
parser.add_option("-b", "--path-to-blender", dest="blender", default="blender")
args, _ = parser.parse_args()

def unzip(file_name, extract_path):
    with ZipFile(file_name, 'r') as map_zip:
        map_zip.extractall(extract_path)

def build_map_data(blender_path, python_path, mapdata_url, map_file_name, shape_file_name):
    current_dir = os.path.dirname(__file__)
    
    zip_file_path = urllib.request.urlretrieve(mapdata_url)[0]
    extract_path = tempfile.gettempdir()
    unzip(zip_file_path, extract_path)
    blender_script_path = os.path.join(current_dir, "blender_script.py")
    shape_file_path = os.path.join(extract_path, shape_file_name)
    mapdata_path = os.path.abspath(os.path.join(current_dir, "..", "Data", map_file_name))
    return_value = os.system(blender_path + " -b -P " + blender_script_path + " -- " + shape_file_path + " " + mapdata_path + " " + python_path)
    if return_value is not 0:
        print("Blender failed")
        print(help)
        sys.exit(1)

def execute(blender_path, python_path):
    current_dir = os.path.dirname(__file__)

    threejs_export_script_path = os.path.join(current_dir, "export_threejs.py")
    threejs_exporter_url = 'https://raw.githubusercontent.com/mrdoob/three.js/master/utils/exporters/blender/2.65/scripts/addons/io_mesh_threejs/export_threejs.py'
    urllib.request.urlretrieve(threejs_exporter_url, threejs_export_script_path)
    
    build_map_data(
        blender_path=blender_path,
        python_path=python_path,
        mapdata_url='http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip',
        map_file_name='world_map.json',
        shape_file_name='ne_110m_admin_0_countries')
    
    build_map_data(
        blender_path=blender_path,
        python_path=python_path,
        mapdata_url = 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries.zip',
        map_file_name='world_map_hd.json',
        shape_file_name='ne_50m_admin_0_countries')

execute(args.blender, args.python)
# if len(sys.argv) > 1:
#     if sys.argv[1] == "--help":
#         print(help)
#     else:
#         execute(sys.argv[1])
# else:
#     execute("blender")