import urllib.request
from zipfile import ZipFile
import tempfile
import os
import sys
from optparse import OptionParser


help = "Usage: build.py [path to blender] \n" + \
       "Path to blender is optional if blender is in path."
parser = OptionParser()
parser.add_option("-p", "--path-to-python", dest="python")
parser.add_option("-b", "--path-to-blender", dest="blender")
args, _ = parser.parse_args()

if args.blender is None:
    args.blender = "blender"

if args.python is None:
    args.python = "python"

def unzip(file_name, extract_path):
    with ZipFile(file_name, 'r') as map_zip:
        map_zip.extractall(extract_path)

def execute(blender_path, python_path):
    current_dir = os.path.dirname(__file__)

    threejs_export_script_path = os.path.join(current_dir, "export_threejs.py")
    threejs_exporter_url = 'https://raw.githubusercontent.com/mrdoob/three.js/master/utils/exporters/blender/2.65/scripts/addons/io_mesh_threejs/export_threejs.py'
    urllib.request.urlretrieve(threejs_exporter_url, threejs_export_script_path)

    mapdata_url = 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip'
    file_name = urllib.request.urlretrieve(mapdata_url)[0]
    extract_path = tempfile.gettempdir()
    unzip(file_name, extract_path)
    blender_script_path = os.path.join(current_dir, "blender_script.py")
    shape_file_path = os.path.join(extract_path, "ne_110m_admin_0_countries")
    mapdata_path = os.path.abspath(os.path.join(current_dir, "..", "Data", "world_map.json"))
    return_value = os.system(blender_path + " -b -P " + blender_script_path + " -- " + shape_file_path + " " + mapdata_path + " " + python_path)
    if return_value is not 0:
        print("Blender failed")
        print(help)
        sys.exit(1)

execute(args.blender, args.python)
# if len(sys.argv) > 1:
#     if sys.argv[1] == "--help":
#         print(help)
#     else:
#         execute(sys.argv[1])
# else:
#     execute("blender")