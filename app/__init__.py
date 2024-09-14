# app/__init__.py
from flask import Flask
from .socketio_instance import socketio
from .routes import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(main_blueprint)
    socketio.init_app(app)
    return app
