import threading

from flask import render_template

import cfg

def init(app):
    from skier import frontend
    from skier import pgpapi
    from skier import pks
    from cfg import API_VERSION
    from skier import pgpactions

    if not cfg.cfg.config.features.disable_frontend:
        app.register_blueprint(frontend.frontend)
        app.register_blueprint(frontend.frontend_keys, url_prefix="/keys")
    app.register_blueprint(pgpapi.pgpapi, url_prefix="/api/v{}".format(API_VERSION))
    app.register_blueprint(pks.legacypks, url_prefix="/pks")

    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.sqlalchemy_uri

    app.jinja_env.globals.update(theme = cfg.cfg.config.theme)

    @app.before_first_request
    def f(*args, **kwargs):
        if cfg.cfg.config.pool_enabled.autosync:
            threading.Thread(target=pgpactions.synch_keys).start()

    @app.errorhandler(404)
    def four_oh_four(error):
        if not cfg.cfg.config.features.disable_frontend:
            return render_template("error/404.html"), 404
        else:
            return "Not Found", 404

    @app.errorhandler(403)
    def four_oh_three(error):
        if not cfg.cfg.config.features.disable_frontend:
            return render_template("error/403.html"), 403
        else:
            return "Forbidden", 403

    @app.errorhandler(500)
    def five_oh_oh(error):
        if not cfg.cfg.config.features.disable_frontend:
            return render_template("error/500.html"), 500
        else:
            return "Internal Server Error", 500

    @app.route("/skier")
    def skier():
        return "", 200
