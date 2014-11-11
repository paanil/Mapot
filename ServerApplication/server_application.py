import json
import flask
from flask import render_template, request
from common import util
#from glob import glob
#import os

config = None
datasets =  {}

def read_datasets():
    global datasets
    data_path = config.get_value("DataPath")
    
    meta = util.read_json(data_path + "metadata.json")
    if meta is None:
        print("Failed to read metadata")
        return
    
    for key in meta.keys():#glob(os.path.join(data_path, "*.json")):
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
    queries = []
    for key in datasets:
        queries.append( (key, datasets[key]["metadata"]["name"]) )
    return datasets.keys()
    #print(queries)
    #return queries

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
    color = request.args.get('color', "", type=str)
    height = request.args.get('height', "", type=str)
    
    color_data = None
    height_data = None
    
    try:
        color_data = datasets[color]
        color_data = get_newest_data(color_data["data"])
    except:
        color_data = {}
        
    try:
        height_data = datasets[height]
        height_data = get_newest_data(height_data["data"])
    except:
        height_data = {}

    #print(color_data)
    #print(height_data)
    
    return flask.json.dumps({"color": color_data, "height":  height_data})

def get_newest_data(data):
    newest_data = {}
    for key in data:
        country = data[key]
        max_year = max(country.keys(), key=int)
        newest_data[key] = country[max_year]

    return newest_data
