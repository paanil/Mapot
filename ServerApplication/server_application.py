import json
import flask
from flask import render_template, request
from common import util

config = None

def init():
    global config
    config = util.Config({"DataPath": "../Data/"})
    config.read("config.json")

def index():
    return render_template("index.html")

def greenhouse_gas_data():
    data_path = config.get_value("DataPath")
    f_name = data_path + "greenhouse_gas.json"
    data = util.read_json(f_name)
    if data is None:
        flask.abort(500)
    return json.dumps(data)

def world_map():
    data_path = config.get_value("DataPath")
    data = util.read_file(data_path + "world_map.json")
    if data is None:
        flask.abort(500)
    return data

def data():
    color = request.args.get('color', "", type=str)
    height = request.args.get('height', "", type=str)
    data_path = config.get_value("DataPath")

    f_name = data_path + color +".json"
    # return flask.jsonify(color=color, height=height)


    data = util.read_json(f_name)
    if data is None:
        flask.abort(500)
    return json.dumps(data)