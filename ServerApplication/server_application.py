import json
import sys
import flask
import config


def hello():

    data_path = config.get_value("DataPath")
    f_name = data_path + "greenhouse_gas.json"
    data = config.read_data_from_json(f_name)
    if data is None: flask.abort(500)
    return json.dumps(data)
