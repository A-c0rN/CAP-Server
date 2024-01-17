from flask import Flask


def create_app():
    app = Flask(__name__)

    app.config[
        "SECRET_KEY"
    ] = "yLy2QgApUomsc0DmUlfUvJc4IkFwr1poTiUGsR3SIjmIZnxUyFC7CuOEK52iGGDB2OpSiddtBZESYyeSlWW23."

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
