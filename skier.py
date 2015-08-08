from flask import render_template
from app import app

import cfg


@app.route("/")
def index():
    return render_template("about.html")

if __name__ == '__main__':
    app.run()
