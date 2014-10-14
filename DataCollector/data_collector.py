import http.client

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

def build_query_body():
    query = read_query_file("greenhouse_gas.xml")
    return body_begin + query + body_end

def do_query():
    connection = http.client.HTTPConnection("data.un.org", 80)
    body = build_query_body()
    connection.request("POST", "/ws/NSIStdV20Service.asmx", body, headers)
    response = connection.getresponse()
    print(response.status, response.reason)
    content = response.read().decode("utf-8")
    print(content.replace(">", ">\n"))
    connection.close()

def main():
    do_query()
