import http.client
import xml.etree.ElementTree as ET
import json
from os.path import isfile, isdir, join, split, basename, splitext
from glob import glob
from common import util
import os
import errno

config = None

def init():
    global config
    config = util.Config({"DataPath": "../Data/"})
    config.read("config.json")

headers = { "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://ec.europa.eu/eurostat/sri/service/2.0/GetCompactData" }

body_begin = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetCompactData xmlns="http://ec.europa.eu/eurostat/sri/service/2.0">
      <Query>
"""
body_end = """</Query>
    </GetCompactData>
  </soap:Body>
</soap:Envelope>
"""

def build_query_body(file_path):
    query = util.read_file(file_path)
    sub = '<?xml version="1.0" encoding="utf-8"?>'

    query = util.read_file(file_path)
    query = query.replace(sub, '')
    return body_begin + query + body_end

def do_query(file_path):
    body = build_query_body(file_path)

    connection = http.client.HTTPConnection("data.un.org", 80)
    connection.request("POST", "/ws/NSIStdV20Service.asmx", body, headers)
    response = connection.getresponse()
    content = response.read().decode("utf-8")
    connection.close()

    print(response.status, response.reason)
    if response.status is not 200:
        print("Query " + file_path + " failed")
        return None

    return content

def et_find(elem, tag):
    for child in elem.getiterator():
        if child.tag.endswith(tag):
            return child

def et_findall(elem, tag):
    children = []
    for child in elem.getchildren():
        if tag in child.tag: children.append(child)

    return children

def collect_data(file_path):
    name, _ = splitext(basename(file_path))
    print("Downloading: " + name)
    xml_data = do_query(file_path)
    if xml_data is None: return False

#    print(xml_data.replace(">", ">\n"))

    root = ET.fromstring(xml_data)
    dataset = et_find(root, "DataSet")

    data = {}

    for series in et_findall(dataset, "Series"):
        area = series.get("REF_AREA")
        obs_dict = {}

        for obs in et_findall(series, "Obs"):
            year = int(obs.get("TIME_PERIOD"))
            value = float(obs.get("OBS_VALUE"))
            obs_dict[year] = value

        data[area] = obs_dict

    if not os.path.isdir(config.get_value("DataPath")):
        os.makedirs(config.get_value("DataPath"))

    data_file = config.get_value("DataPath") + name + ".json"

    util.write_json(data_file, data)
    return True

def main(path):
    if isfile(path):
        collect_data(path)
    elif isdir(path):
        for file in glob(join(path, "*.xml")): #TODO: threading
            collect_data(file)
