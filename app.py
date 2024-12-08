from flask import Flask

APP = Flask(__name__)


@APP.route("/")
def index() -> str:
    return "Congratulations, it's a web app!"


if __name__ == "__main__":
    APP.run(host="127.0.0.1", port=8080, debug=True)
