import http.client
import xml.etree.ElementTree as ET
import json
from common import util

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

def build_query_body(filename):
    query = util.read_file("queries/" + filename)
    return body_begin + query + body_end

def do_query(filename):
    body = build_query_body(filename)

    connection = http.client.HTTPConnection("data.un.org", 80)
    connection.request("POST", "/ws/NSIStdV20Service.asmx", body, headers)
    response = connection.getresponse()
    content = response.read().decode("utf-8")
    connection.close()

    print(response.status, response.reason)
    if response.status is not 200:
        print("Query " + filename + " failed")
        return None

    return content

def et_find(elem, tag):
    for child in elem.getchildren():
        if child.tag.endswith(tag): return child
        childschild = et_find(child, tag)
        if childschild is not None: return childschild

    return None

def et_findall(elem, tag):
    children = []
    for child in elem.getchildren():
        if tag in child.tag: children.append(child)

    return children

def collect_data(data_name):
    xml_data = do_query(data_name + ".query.xml")
    if xml_data is None: return False


    #print(xml_data.replace(">", ">\n"))

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
    
    data_file = config.get_value("DataPath") + data_name + ".json"

    util.write_json(data_file, data)
    return True

def main():
    # collect_data("mortality")
    # collect_data("death")
    # collect_data("methane")
    # collect_data("greenhouse_gas")
    collect_data("forest")
    # collect_data("crude_birth_rate")
    collect_data("crude_death_rate")
    # collect_data("popdiv_all")

