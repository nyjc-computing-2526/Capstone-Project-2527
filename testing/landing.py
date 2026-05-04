import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_login import LoginManager
from app.models.user import User
from app.routes import landing, auth


class BaseRouteTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder='../app/templates')
        self.app.config['TESTING'] = True
        self.app.secret_key = 'test_secret_key'

        self.login_manager = LoginManager()
        self.login_manager.login_view = 'auth.login'
        self.login_manager.init_app(self.app)

        self.fake_user = User(1, 'Test User', 'test@example.com', '2024', None)

        @self.login_manager.user_loader
        def load_user(user_id):
            if str(user_id) == str(self.fake_user.id):
                return self.fake_user
            return None

        self.app.register_blueprint(auth.bp)
        self.app.register_blueprint(landing.bp)

        self.client = self.app.test_client()

    def login(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.fake_user.id)
            sess['_fresh'] = True

    def logout(self):
        with self.client.session_transaction() as sess:
            sess.clear()


class TestLandingAuthAccess(BaseRouteTest):
    """Focus: Ensure routes behave correctly depending on login state"""

    def test_homepage_requires_login_redirect(self):
        """NOT logged in → should redirect to login"""
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_homepage_logged_in_access(self):
        """Logged in → should access homepage"""
        self.login()
        with patch('app.routes.landing.ActivitiesResource.get_upcoming', return_value=[]), \
             patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/home')
            self.assertEqual(response.status_code, 200)

    def test_homepage_after_logout_redirect(self):
        """Login → Logout → try access → should redirect"""
        self.login()
        self.logout()

        response = self.client.get('/home')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_public_routes_access_without_login(self):
        """Public pages should always be accessible"""
        routes = ['/', '/about', '/legal', '/features', '/contact']

        for route in routes:
            with patch('app.routes.landing.render_template', return_value='OK'):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_contact_post_not_blocked_by_auth(self):
        """Contact form should work even when not logged in"""
        with patch('app.routes.landing.smtplib.SMTP_SSL') as mock_smtp, \
             patch.dict(os.environ, {'MAIL_USERNAME': 'test@example.com', 'MAIL_PASSWORD': 'secret'}), \
             patch('app.routes.landing.render_template', return_value='OK'):

            mock_smtp.return_value.__enter__.return_value.login.return_value = None
            mock_smtp.return_value.__enter__.return_value.send_message.return_value = None

            response = self.client.post('/contact', data={
                'name': 'Test',
                'email': 'test@example.com',
                'message': 'Hello'
            })

            self.assertEqual(response.status_code, 200)

    def test_session_token_controls_access(self):
        """Directly manipulate session token to simulate login/logout"""
        
        # No token → blocked
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 302)

        # Add token → allowed
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.fake_user.id)
            sess['_fresh'] = True

        with patch('app.routes.landing.ActivitiesResource.get_upcoming', return_value=[]), \
             patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/home')
            self.assertEqual(response.status_code, 200)

        # Remove token → blocked again
        with self.client.session_transaction() as sess:
            sess.clear()

        response = self.client.get('/home')
        self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()