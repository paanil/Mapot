import server_application
import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return server_application.index()

@app.route("/_data")
def data():
    return server_application.data()

@app.context_processor
def inject_queries():
    return dict(queries=server_application.get_queries())

@app.context_processor
def inject_parameters():
    return dict(params=server_application.get_params())

if __name__ == "__main__":
    server_application.init()
    app.debug = True
    app.run()
