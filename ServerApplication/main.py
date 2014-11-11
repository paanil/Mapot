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

#queries = ["methane", "death", "crude_death_rate"]

@app.context_processor
def inject_queries():
    return dict(queries=server_application.get_queries())
    #return dict(queries=queries)

if __name__ == "__main__":
    server_application.init()
    app.run()
