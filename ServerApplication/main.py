import server_application
import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return server_application.hello()

@app.route("/_map_data")
def world_map():
    return server_application.world_map()

if __name__ == "__main__":
    server_application.init()
    app.run()
