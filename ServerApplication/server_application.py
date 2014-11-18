import json
import flask
from flask import render_template, request
from common import util

config = None
datasets =  {}

def divide_by_pop(data):
    print("divide_by_pop")
    
def divide_by_area(data):
    print("divide_by_area")

parameters = {
    "divbypop": ("Divided by population", divide_by_pop),
    "divbyarea": ("Divided by area", divide_by_area)
}

def read_datasets():
    global datasets
    data_path = config.get_value("DataPath")
    
    meta = util.read_json(data_path + "metadata.json")
    if meta is None:
        print("Failed to read metadata")
        return
    
    for key in meta.keys():
        file = data_path + key + ".json"
        data = util.read_json(file)
        try:
            metadata = data["metadata"]
            id = metadata["id"]
            datasets[id] = data
        except:
            print("Failed to read dataset '" + key + "'")

def init():
    global config
    config = util.Config({"DataPath": "../Data/"})
    config.read("config.json")
    read_datasets()

def get_queries():
    global datasets
    queries = [{"id": "none", "name": "None"}]
    for id in datasets:
        queries.append( {"id": id, "name": datasets[id]["metadata"]["name"]} )
    return queries

def get_params():
    params = [{"id": "none", "name": "None"}]
    for id in parameters:
        params.append( {"id": id, "name": parameters[id][0]} )
    return params

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
    global datasets
    id = request.args.get('id', "", type=str)
    param = request.args.get('param', "", type=str)
    
    data = None
    try:
        data = get_newest_data(datasets[id]["data"])
    except:
        print("No data with id '" + id + "'")
        data = {}
    
    try:
        param_func = parameters[param][1]
        param_func(data)
    except:
        print("No parameter with id: '" + param + "'")
    
    return flask.json.dumps(data)

def get_newest_data(data):
    newest_data = {}
    for key in data:
        country = data[key]
        max_year = max(country.keys(), key=int)
        newest_data[key] = country[max_year]

    return newest_data
