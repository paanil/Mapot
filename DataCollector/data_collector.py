import http.client
import xml.etree.ElementTree as ET
import json
import config

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

def read_query_file(filename):
    query = ""
    with open("queries/" + filename, "r") as f:
        query = f.read()
    return query

def build_query_body(filename):
    query = read_query_file(filename)
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
        if tag in child.tag: return child
        elem = et_find(child, tag)
        if elem is not None: return elem

    return None

def et_findall(elem, tag):
    children = []
    for child in elem.getchildren():
        if tag in child.tag: children.append(child)

    return children

def write_json(filename, data):
    data_path = config.get_value("DataPath")
    with open(data_path + filename, "w") as f:
        f.write(json.dumps(data, sort_keys=True, indent=4))

def collect_data(data_name):
    xml_data = do_query(data_name + ".query.xml")
    if xml_data is None: return False

    # with open("tiedosto.txt", "w") as f:
    #     f.write(xml_data.replace(">", ">\n"))

    # print(xml_data.replace(">", ">\n"))

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

    write_json(data_name + ".json", data)
    return True

def main():
    # collect_data("death")
    collect_data("methane")
    # collect_data("greenhouse_gas")

    # ghg_data = do_query("greenhouse_gas.xml")
    # if ghg_data is None: return

    # root = ET.fromstring(ghg_data)
    # dataset = et_find(root, "DataSet")
    #
    # for series in et_findall(dataset, "Series"):
    #     area = series.get("REF_AREA")
    #     print(area + ":")
    #     for obs in et_findall(series, "Obs"):
    #         year = obs.get("TIME_PERIOD")
    #         value = obs.get("OBS_VALUE")
    #         print("  " + year + ": " + value)

    # ns1 = "{http://schemas.xmlsoap.org/soap/envelope/}"
    # ns2 = "{http://ec.europa.eu/eurostat/sri/service/2.0}"
    # ns3 = "{http://www.SDMX.org/resources/SDMXML/schemas/v2_0/message}"
    # ns4 = "{urn:estat:sdmx.infomodel.keyfamily.KeyFamily=UNSD:DSD_GHG_UNDATA:1.0:compact}"
    #
    # root = ET.fromstring(ghg_data)
    # dataset = root.find(ns1 + "Body").\
    #     find(ns2 + "GetCompactDataResponse").\
    #     find(ns2 + "GetCompactDataResult").\
    #     find(ns3 + "CompactData").\
    #     find(ns4 + "DataSet")
    #
    # for series in dataset.findall(ns4 + "Series"):
    #     area = series.get("REF_AREA")
    #     print(area + ":")
    #     for obs in series.findall(ns4 + "Obs"):
    #         year = obs.get("TIME_PERIOD")
    #         value = obs.get("OBS_VALUE")
    #         print("  " + year + ": " + value)
