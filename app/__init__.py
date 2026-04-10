from flask import Flask
from flask_login import LoginManager

from app.models.user import User
from app.resources.users import get_user_by_id
from .routes.landing import bp as landing_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.register_blueprint(landing_bp) 
    login_manager.init_app(app)
    return app

@login_manager.user_loader
def load_user(user_id):
    row = get_user_by_id(user_id)
    if row is None:
        return None
    return User(row['id'], row['name'], row['email'], row['password'])