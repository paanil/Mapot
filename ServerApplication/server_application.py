import json
import flask

util = None
config = None

def init():
    global util
    global config
    
    import os
    path = os.path.dirname(__file__)
    path = os.path.split(path)[0]
    path = os.path.join(path, "Common", "util.py")

    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("util", path)
    util = loader.load_module()
    
    config = util.Config({"DataPath": "../Data/"})
    config.read("config.json")

def hello():
    data_path = config.get_value("DataPath")
    f_name = data_path + "greenhouse_gas.json"
    data = util.read_json(f_name)
    if data is None: flask.abort(500)
    return json.dumps(data)
