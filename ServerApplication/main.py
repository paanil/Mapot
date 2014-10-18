import server_application
import config
from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return server_application.hello()

if __name__ == "__main__":
    config.read("config.json")
    app.run()
