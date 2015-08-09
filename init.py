from flask import url_for
from werkzeug.utils import redirect


def init(app):
    from skier import frontend
    from skier import pgpapi
    from skier import pks
    from cfg import API_VERSION
    app.register_blueprint(frontend.frontend)
    app.register_blueprint(pgpapi.pgpapi, url_prefix="/api/v{}".format(API_VERSION))
    app.register_blueprint(pks.legacypks, url_prefix="/pks")

    @app.route("/")
    def index():
        return redirect(url_for("frontend.about")), 301