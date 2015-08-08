from flask import url_for
from werkzeug.utils import redirect


def init(app):
    from skier import frontend
    app.register_blueprint(frontend.frontend)

    @app.route("/")
    def index():
        return redirect(url_for("frontend.about")), 301