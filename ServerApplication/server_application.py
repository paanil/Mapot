import json
import flask
from flask import render_template, request
from common import util

config = None
datasets =  {}
total_population = None

def divide_by_pop(data):
    if total_population != None:
        print("Total population data not available")
        return data
    values = data["values"]
    times = data["times"]
    new_data = {"values": {}, "times": {}}
    for country_id in values:
        if country_id not in total_population:
            print("No population for", country_id)
            continue
        time = times[country_id]
        country_pop = total_population[country_id]
        if time not in country_pop:
            print("No population for", country_id, times)
            continue
        new_data["values"][country_id] = float(values[country_id]) / float(country_pop[time])
        new_data["times"][country_id] = time
    return new_data
    
def divide_by_area(data):
    print("divide_by_area")
    return data

parameters = {
    "divbypop": ("Divided by population", divide_by_pop),
    "divbyarea": ("Divided by area", divide_by_area)
}

def read_datasets():
    global datasets
    global total_population;
    data_path = config.get_value("DataPath")
    
    meta = util.read_json(data_path + "metadata.json")
    if meta is None:
        print("Failed to read metadata")
        return
    
    for key in meta.keys():
        file = data_path + key + ".json"
        data = util.read_json(file)
        try:
            #data["metadata"]["unit"] = meta[key]["unit"] # check if this is done in data collector
            metadata = data["metadata"]
            if metadata["name"] == "Total population":
                total_population = data;
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
        data = param_func(data)
    except:
        print("No parameter with id: '" + param + "'")

    data["unit"] = datasets[id]["metadata"]["unit"]
    data["name"] = datasets[id]["metadata"]["name"]

    return flask.json.dumps(data)

def get_newest_data(data):
    newest_data = {"values": {}, "times": {}}
    for key in data:
        country = data[key]
        max_year = max(country.keys(), key=int)
        newest_data["values"][key] = country[max_year]
        newest_data["times"][key] = max_year

    return newest_data
