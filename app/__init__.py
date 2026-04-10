from flask import Flask
from flask_login import LoginManager

from app.models.user import User
from app.resources.users import UsersResource
from .routes.landing import bp as landing_bp
from .routes.activities import bp as activities_bp

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret_key_yes"
    app.register_blueprint(landing_bp)
    app.register_blueprint(activities_bp)
    login_manager.init_app(app)

    return app

@login_manager.user_loader
def load_user(user_id):
    try:
        user_data = UsersResource().user(int(user_id)).get()
        return User(user_data['id'], user_data['name'], user_data['email'])
    except:
        return None