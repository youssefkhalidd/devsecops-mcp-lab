from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.routes import tickets_bp

    app.register_blueprint(tickets_bp)

    return app
