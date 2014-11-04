import server_application
import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return server_application.index()

@app.route("/_map_data")
def world_map():
    return server_application.world_map()

@app.route("/_greenhouse_gas_data")
def greenhouse_gas():
    return server_application.greenhouse_gas_data()

@app.route("/_data")
def data():
    return server_application.data()

if __name__ == "__main__":
    # Fruits = {"5000": 8, "2014": 3, "4": 5, "2011": 2}
    # max_key = max(Fruits, key=Fruits.get)
    # print(max_key)
    # print(Fruits[max_key])
    # max_value = Fruits[max_key]
    # key_for_min = min(Fruits, key=Fruits.get)
    # min_value = Fruits[key_for_min]
    #
    # print(Fruits[max(Fruits.keys(), key = int)])


    # for key in Fruits:
    #     Fruits[key] = ((Fruits[key])-min_value)/(max_value-min_value)
    #     print(Fruits[key])
    #
    server_application.init()
    app.run()
