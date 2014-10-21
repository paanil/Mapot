import json
import flask
from common import util

config = None

def init():
    global config
    config = util.Config({"DataPath": "../Data/"})
    config.read("config.json")

def hello():
    data_path = config.get_value("DataPath")
    f_name = data_path + "greenhouse_gas.json"
    data = util.read_json(f_name)
    if data is None: flask.abort(500)
    return json.dumps(data)
