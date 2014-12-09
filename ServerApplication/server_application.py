import json
import flask
from datetime import date
from flask import render_template, request
from common import util

app = flask.Flask(__name__)

config = None
datasets =  {}
total_population = None
surface_area = None

def get_value_with_closest_time(values, time):
    delta = 10000
    value = 0
    T = int(time)
    for t in values:
        d = abs(int(t) - T)
        if d < delta:
            delta = d
            value = values[t]
    return value

def divide(data, by):
    values = data["values"]
    times = data["times"]
    by_data = by["data"]
    new_data = {"values": {}, "times": {}}
    for country_id in values:
        if country_id not in by_data:
            print("No", by["metadata"]["name"], "for", country_id)
            continue
        time = times[country_id]
        divider = get_value_with_closest_time(by_data[country_id], time)
        new_data["values"][country_id] = float(values[country_id]) / float(divider)
        new_data["times"][country_id] = time
    return new_data

def divide_by_pop(data):
    print("divide_by_pop")
    if total_population == None:
        print("Total population data not available")
        return data
    return divide(data, total_population)
    
def divide_by_area(data):
    print("divide_by_area")
    if surface_area == None:
        print("Surface area data not available")
        return data
    return divide(data, surface_area)

parameters = {
    "divbypop": ("Divided by population", divide_by_pop),
    "divbyarea": ("Divided by area", divide_by_area)
}

def read_datasets():
    global datasets
    global total_population
    global surface_area
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
            if metadata["name"] == "Total population":
                total_population = data;
            elif metadata["name"] == "Surface area":
                surface_area = data;
        except:
            print("Failed to read dataset '" + key + "'")

def init():
    global config
    config = util.Config({"DataPath": "../Data/"})
    config.read("config.json")
    read_datasets()

@app.context_processor
def get_queries():
    global datasets
    queries = []
    for id in datasets:
        selected = False
        name = datasets[id]["metadata"]["name"]
        if name == "Total population":
            selected = True
        queries.append( {"id": id, "name": name, "selected": selected} )
        
    queries = sorted(queries, key=lambda query: query["name"]) 
    queries.insert(0, {"id": "none", "name": "None", "selected": False})
    return dict(queries=queries)

@app.context_processor
def get_params():
    params = [{"id": "none", "name": "None"}]
    for id in parameters:
        params.append( {"id": id, "name": parameters[id][0]} )
    return dict(params=params)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/_data")
def data():
    global datasets
    id = request.args.get('id', "", type=str)
    param = request.args.get('param', "", type=str)
    
    data = None
    
    if id == "none":
        data = { "values": {}, "times": {}, "unit": "", "name": "" }
    else:
        try:
            data = get_most_current_data(datasets[id]["data"])
        except:
            print("No data with id '" + id + "'")
            data = {"values": {}, "times": {}}
        
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

def get_most_current_data(data):
    current_data = {"values": {}, "times": {}}
    this_year = date.today().year
    #print(this_year)
    for key in data:
        country = data[key]
        years = map(int, country.keys())
        most_current = years.__next__()
        for year in years:
            if (abs(year - this_year) < abs(most_current - this_year)):
                most_current = year
        #print(most_current)
        current_data["values"][key] = country[str(most_current)]
        current_data["times"][key] = str(most_current)

    return current_data

    
if __name__ == "__main__":
    init()
    app.debug = True
    app.run()
    