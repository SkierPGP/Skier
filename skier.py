from flask import redirect, url_for
from app import app

import cfg

@app.route("/")
def index():
    return redirect(url_for("skier.about")), 301

if __name__ == '__main__':
    app.run()
