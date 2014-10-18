import server_application
import flask

app = flask.Flask(__name__)

@app.route("/")
def index():
    return server_application.hello()

if __name__ == "__main__":
    server_application.init()
    app.run()
