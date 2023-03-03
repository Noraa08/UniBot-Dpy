from flask import Flask
from threading import Thread
import logging, random
import sys

cli = sys.modules["flask.cli"]
cli.show_server_banner = lambda *x: None

app = Flask("")

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)
log.disabled = True
app.logger.disabled = False


@app.route("/")
def home():
    return (
        f"<h1>  ¡Conectado!</h1>"
        + "<style>body {background-color: #202126;} h1 {color: #ffff;}</style>"
    )


def run():
    app.run(host="0.0.0.0", port=random.randint(2000, 9000))


def keep_alive():
    t = Thread(target=run)
    t.start()
