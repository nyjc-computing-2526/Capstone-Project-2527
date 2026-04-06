from flask import Flask
from .routes.landing import bp as landing_bp

def create_app():
    app = Flask(__name__)
    app.register_blueprint(landing_bp) 
    return app