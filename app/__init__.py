from flask import Flask, redirect, request, render_template
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

import os
import logging

from .models.user import User
from .resources.users import UsersResource
from .routes.landing import bp as landing_bp
from .routes.activities import bp as activities_bp
from .routes.auth import bp as auth_bp
from .utils.sanitize_util import render_markdown_safe

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY environment variable is not set. The application cannot start.")
    if len(secret_key) < 32:
        raise RuntimeError("SECRET_KEY must be at least 32 characters long.")
    app.secret_key = secret_key

    app.config['RECAPTCHA_SITE_KEY'] = os.getenv('RECAPTCHA_SITE_KEY')
    app.config['RECAPTCHA_SECRET_KEY'] = os.getenv('RECAPTCHA_SECRET_KEY')
    if not app.config['RECAPTCHA_SITE_KEY'] or not app.config['RECAPTCHA_SECRET_KEY']:
        logging.warning("RECAPTCHA_SITE_KEY or RECAPTCHA_SECRET_KEY is not set — reCAPTCHA will not function.")
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = not app.debug

    CSRFProtect(app)

    app.jinja_env.filters['markdown_safe'] = render_markdown_safe

    _CSP = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://www.google.com https://www.gstatic.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "frame-src https://www.google.com; "
        "connect-src 'self' https://www.google.com; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    @app.before_request
    def enforce_https():
        if not app.debug and not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            code = 308 if request.method == 'POST' else 301
            return redirect(url, code=code)

    @app.after_request
    def apply_security_headers(response):
        if not app.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = _CSP
        response.headers.pop('Server', None)
        return response

    @app.errorhandler(400)
    def bad_request(e):
        return render_template('error.html', code=400, message='Bad request.'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error.html', code=403, message='Access denied.'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', code=404, message='Page not found.'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('error.html', code=500, message='An unexpected error occurred.'), 500

    login_manager = LoginManager() 
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            user_data = UsersResource().user(int(user_id)).get()
            return User(user_data['id'], user_data['name'], user_data['email'], user_data['user_class'],  user_data['password'])
        except Exception:
            return None

    app.register_blueprint(landing_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(auth_bp)

    return app
