from flask import render_template


def init(app):
    from skier import frontend
    from skier import pgpapi
    from skier import pks
    from cfg import API_VERSION
    app.register_blueprint(frontend.frontend)
    app.register_blueprint(frontend.frontend_keys, url_prefix="/keys")
    app.register_blueprint(pgpapi.pgpapi, url_prefix="/api/v{}".format(API_VERSION))
    app.register_blueprint(pks.legacypks, url_prefix="/pks")

    @app.errorhandler(404)
    def four_oh_four(error):
        return render_template("error/404.html"), 404

    @app.errorhandler(403)
    def four_oh_three(error):
        return render_template("error/403.html"), 403

    @app.route("/skier")
    def skier():
        return "", 200