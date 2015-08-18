from flask import render_template

import cfg


def init(app, cache):
    from skier import frontend
    from skier import pgpapi
    from skier import pks
    from cfg import API_VERSION

    app.register_blueprint(frontend.frontend)
    app.register_blueprint(frontend.frontend_keys, url_prefix="/keys")
    app.register_blueprint(pgpapi.pgpapi, url_prefix="/api/v{}".format(API_VERSION))
    app.register_blueprint(pks.legacypks, url_prefix="/pks")

    app.config["SQLALCHEMY_DATABASE_URI"] = cfg.sqlalchemy_uri

    app.config["CACHE_REDIS_HOST"] = cfg.redis_host
    app.config["CACHE_REDIS_PORT"] = cfg.cfg.config.redis.port
    app.config["CACHE_REDIS_DB"] = cfg.cfg.config.redis.db

    @app.errorhandler(404)
    def four_oh_four(error):
        return render_template("error/404.html"), 404

    @app.errorhandler(403)
    def four_oh_three(error):
        return render_template("error/403.html"), 403

    @app.route("/skier")
    def skier():
        return "", 200