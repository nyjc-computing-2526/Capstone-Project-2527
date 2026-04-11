from flask import Flask
from flask_login import LoginManager

from .models.user import User
from .resources.users import UsersResource
from .routes.landing import bp as landing_bp
from .routes.activities import bp as activities_bp
from .routes.auth import bp as auth_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "secret_key_yes"

    login_manager = LoginManager() 
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user_data = UsersResource().user(int(user_id)).get()
            print("Loaded user:", user_data)
            return User(user_data['id'], user_data['name'], user_data['email'], user_data['user_class'],  user_data['password'])
        except Exception as e:
            print("user_loader error:", e)
            return None

    app.register_blueprint(landing_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(auth_bp)

    return app