def init(app):
    from skier import skier
    app.register_blueprint(skier.skier)