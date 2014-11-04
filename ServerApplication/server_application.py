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

    color_path = data_path + color + ".json"
    height_path = data_path + height + ".json"

    # return flask.jsonify(color=color, height=height)

    color_data = util.read_json(color_path)
    height_data = util.read_json(height_path)
    if data is None:
        flask.abort(500)
    color_data = get_newest_data(color_data["data"])    # Pick only the data from the latest year available
    height_data = get_newest_data(height_data["data"])
    print(color_data)
    print(height_data)
    return flask.json.dumps({"color": color_data, "height":  height_data})

def get_newest_data(data):
    newest_data = {}
    for key in data:
        country = data[key]
        max_year = max(country.keys(), key=int)
        newest_data[key] = country[max_year]

    return newest_data
