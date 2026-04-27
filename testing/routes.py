import os
import sys
import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask
from flask_login import LoginManager
from app.models.user import User
from app.routes import activities, auth, landing

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
        self.app.register_blueprint(activities.bp)
        self.app.register_blueprint(landing.bp)

        self.client = self.app.test_client()

    def login(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.fake_user.id)
            sess['_fresh'] = True

class TestActivitiesRoutes(BaseRouteTest):
    """Test suite for the activities routes in app.routes.activities."""
    
    def test_activities_route_get(self):
        """Test the GET /activities/ route to ensure it returns a 200 status code."""
        self.login()
        with patch('app.routes.activities.activities_resource.get_upcoming', return_value=[]), \
             patch('app.routes.activities.activities_resource.get_completed', return_value=[]), \
             patch('app.routes.activities.activities_resource.get_ongoing', return_value=[]), \
             patch('app.routes.activities.render_template', return_value='OK'):
            response = self.client.get('/activities/')
            self.assertEqual(response.status_code, 200)

    def test_activity_details_route_valid_id(self):
        """Test the GET /activities/<id> route with a valid activity ID to ensure it returns a 200 status code."""
        self.login()
        with patch('app.routes.activities.activities_resource.activity') as mock_activity, \
             patch('app.routes.activities.render_template', return_value='OK'), \
             patch('app.routes.activities.users_resource.user') as mock_user:
            mock_resource = MagicMock()
            mock_resource.get.return_value = {
                'id': 16,
                'title': 'Test Activity',
                'description': 'Test',
                'started_at': datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
                'ended_at': datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc),
                'created_by': None,
                'venue': 'Test Venue'
            }
            mock_resource.get_participants.return_value = []
            mock_activity.return_value = mock_resource
            response = self.client.get('/activities/16')
            self.assertEqual(response.status_code, 200)

    def test_activity_details_route_invalid_id(self):
        """Test the GET /activities/<id> route with an invalid activity ID to ensure it redirects."""
        with patch('app.routes.activities.activities_resource.activity') as mock_activity, \
             patch('app.routes.activities.render_template', return_value='OK'):
            mock_resource = MagicMock()
            mock_resource.get.side_effect = ValueError("Activity not found")
            mock_activity.return_value = mock_resource
            
            response = self.client.get('/activities/999')
            self.assertEqual(response.status_code, 302)  # Redirect to activities

    def test_my_activities_route_authorized(self):
        """Test the GET /activities/myactivities route when logged in."""
        self.login()
        with patch('app.routes.activities.activities_resource.get_owned', return_value=[]), \
             patch('app.routes.activities.activities_resource.get_joined', return_value=[]), \
             patch('app.routes.activities.render_template', return_value='OK'):
            response = self.client.get('/activities/myactivities')
            self.assertEqual(response.status_code, 200)

    def test_create_activity_route_get_authorized(self):
        """Test the GET /activities/create route when logged in."""
        self.login()
        with patch('app.routes.activities.render_template', return_value='OK'):
            response = self.client.get('/activities/create')
            self.assertEqual(response.status_code, 200)

    def test_create_activity_route_post_authorized(self):
        """Test the POST /activities/create route when logged in."""
        self.login()
        with patch('app.routes.activities.activities_resource.get_owned', return_value=[]), \
             patch('app.routes.activities.activities_resource.create_activity', return_value=16):
            response = self.client.post('/activities/create', data={
                'title': 'Test Activity',
                'description': 'A test description',
                'start_date': '2026-06-01T10:00',
                'end_date': '2026-06-02T10:00',
                'venue': 'Test Venue'
            })
            self.assertEqual(response.status_code, 302)
            self.assertIn('/activities/16', response.location)

    def test_join_activity_route_authorized(self):
        """Test the POST /activities/join/<id> route when logged in."""
        self.login()
        with patch('app.routes.activities.activities_resource.activity') as mock_activity:
            mock_resource = MagicMock()
            mock_resource.join.return_value = True
            mock_activity.return_value = mock_resource
            response = self.client.post('/activities/join/16')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/activities/16')

    def test_leave_activity_route_authorized(self):
        """Test the POST /activities/leave/<id> route when logged in."""
        self.login()
        with patch('app.routes.activities.activities_resource.activity') as mock_activity:
            mock_resource = MagicMock()
            mock_resource.leave.return_value = True
            mock_activity.return_value = mock_resource
            response = self.client.post('/activities/leave/16')
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.location, '/activities/myactivities')

    def test_update_activity_route_get_authorized(self):
        """Test the GET /activities/update/<id> route when logged in."""
        self.login()
        with patch('app.routes.activities.activities_resource.activity') as mock_activity, \
             patch('app.routes.activities.render_template', return_value='OK'):
            mock_resource = MagicMock()
            mock_resource.get.return_value = {
                'id': 16,
                'title': 'Test Activity',
                'description': 'Test',
                'started_at': datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
                'ended_at': datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc),
                'created_by': 1,
                'venue': 'Test Venue'
            }
            mock_activity.return_value = mock_resource
            response = self.client.get('/activities/update/16')
            self.assertEqual(response.status_code, 200)

    def test_update_activity_route_post_authorized(self):
        """Test the POST /activities/update/<id> route when logged in."""
        self.login()
        with patch('app.routes.activities.activities_resource.activity') as mock_activity:
            mock_resource = MagicMock()
            mock_resource.get.return_value = {
                'id': 16,
                'title': 'Test Activity',
                'description': 'Test',
                'started_at': datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
                'ended_at': datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc),
                'created_by': 1,
                'venue': 'Test Venue'
            }
            mock_resource.update.return_value = True
            mock_activity.return_value = mock_resource
            response = self.client.post('/activities/update/16', data={
                'title': 'Updated Activity',
                'description': 'Updated description',
                'start_date': '2026-06-02T10:00',
                'end_date': '2026-06-03T10:00',
                'venue': 'Updated Venue'
            })
            self.assertEqual(response.status_code, 302)
            self.assertIn('/activities/16', response.location)

    def test_delete_activity_route_authorized(self):
        """Test the POST /activities/delete/<id> route when logged in."""
        self.login()
        with patch('app.routes.activities.activities_resource.activity') as mock_activity:
            mock_resource = MagicMock()
            mock_resource.get.return_value = {
                'id': 16,
                'title': 'Test Activity',
                'description': 'Test',
                'started_at': datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
                'ended_at': datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc),
                'created_by': 1,
                'venue': 'Test Venue'
            }
            mock_resource.delete.return_value = True
            mock_activity.return_value = mock_resource
            response = self.client.post('/activities/delete/16')
            self.assertEqual(response.status_code, 302)
            self.assertIn('/activities/myactivities', response.location)

    def test_create_activity_route_get(self):
        """Test the GET /activities/create route without login should redirect to login."""
        response = self.client.get('/activities/create')
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

    def test_create_activity_route_post_unauthorized(self):
        """Test the POST /activities/create route without login should redirect to login."""
        response = self.client.post('/activities/create', data={'title': 'Test'})
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

    def test_my_activities_route_unauthorized(self):
        """Test the GET /activities/myactivities route without login should redirect to login."""
        response = self.client.get('/activities/myactivities')
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

    def test_join_activity_route_unauthorized(self):
        """Test the POST /activities/join/<id> route without login should redirect to login."""
        response = self.client.post('/activities/join/16')
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

    def test_leave_activity_route_unauthorized(self):
        """Test the POST /activities/leave/<id> route without login should redirect to login."""
        response = self.client.post('/activities/leave/16')
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

    def test_update_activity_route_get_unauthorized(self):
        """Test the GET /activities/update/<id> route without login should redirect to login."""
        response = self.client.get('/activities/update/16')
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

    def test_update_activity_route_post_unauthorized(self):
        """Test the POST /activities/update/<id> route without login should redirect to login."""
        response = self.client.post('/activities/update/16', data={'title': 'Updated'})
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

    def test_delete_activity_route_unauthorized(self):
        """Test the POST /activities/delete/<id> route without login should redirect to login."""
        response = self.client.post('/activities/delete/16')
        self.assertEqual(response.status_code, 302)  # Redirects because @login_required

class TestAuthRoutes(BaseRouteTest):
    """Test suite for the auth routes in app.routes.auth."""

    def test_login_get(self):
        with patch('app.routes.auth.render_template', return_value='OK'):
            response = self.client.get('/auth/login')
            self.assertEqual(response.status_code, 200)

    def test_login_post_success(self):
        with patch('app.routes.auth.verify_recaptcha', return_value=True), \
             patch('app.routes.auth.users_resource.authenticate', return_value={
                 'id': 1,
                 'name': 'Test User',
                 'email': 'test@example.com',
                 'user_class': '2024',
                 'verified': True
             }), \
             patch('app.routes.auth.login_user'):
            response = self.client.post('/auth/login', data={
                'email': 'test@example.com',
                'password': 'secret',
                'g-recaptcha-response': 'token'
            })
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/home'))

    def test_register_get(self):
        with patch('app.routes.auth.render_template', return_value='OK'):
            response = self.client.get('/auth/register')
            self.assertEqual(response.status_code, 200)

    def test_register_post_success(self):
        mock_user_resource = MagicMock()
        mock_user_resource.create_verification_token.return_value = None
        with patch('app.routes.auth.verify_recaptcha', return_value=True), \
             patch('app.routes.auth.users_resource.register', return_value=1), \
             patch('app.routes.auth.users_resource.user', return_value=mock_user_resource), \
             patch('app.routes.auth.resend.Emails.send'), \
             patch('app.routes.auth.render_template', return_value='OK'):
            response = self.client.post('/auth/register', data={
                'email': 'test@example.com',
                'password': 'SecurePass123!',
                'name': 'Test User',
                'class': '2024',
                'confirm_password': 'SecurePass123!',
                'g-recaptcha-response': 'token'
            })
            self.assertEqual(response.status_code, 302)

    def test_logout_authorized(self):
        self.login()
        with patch('app.routes.auth.logout_user'):
            response = self.client.post('/auth/logout')
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/'))

    def test_view_profile_authorized(self):
        self.login()
        with patch('app.routes.auth.users_resource.user') as mock_user, \
             patch('app.routes.auth.activities_resource.get_owned', return_value=[]), \
             patch('app.routes.auth.render_template', return_value='OK'):
            mock_user.return_value.get.return_value = {'id': 1, 'name': 'Test User'}
            response = self.client.get('/auth/view/1')
            self.assertEqual(response.status_code, 200)

    def test_update_user_get_authorized(self):
        self.login()
        with patch('app.routes.auth.users_resource.user') as mock_user, \
             patch('app.routes.auth.render_template', return_value='OK'):
            mock_user.return_value.get.return_value = {'id': 1, 'name': 'Test User', 'email': 'test@example.com', 'user_class': '2024'}
            response = self.client.get('/auth/update')
            self.assertEqual(response.status_code, 200)

    def test_update_user_post_authorized(self):
        self.login()
        mock_user_resource = MagicMock()
        mock_user_resource.update.return_value = None
        with patch('app.routes.auth.users_resource.user', return_value=mock_user_resource), \
             patch('app.routes.auth.users_resource.authenticate'):
            response = self.client.post('/auth/update', data={
                'email': 'new@example.com',
                'name': 'New Name',
                'class': '2025'
            })
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/auth/view/1'))

    def test_delete_user_authorized(self):
        self.login()
        mock_user_resource = MagicMock()
        with patch('app.routes.auth.users_resource.user', return_value=mock_user_resource), \
             patch('app.routes.auth.logout_user'):
            response = self.client.post('/auth/delete/1')
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/'))

    def test_forgot_password_get(self):
        with patch('app.routes.auth.render_template', return_value='OK'):
            response = self.client.get('/auth/forgot-password')
            self.assertEqual(response.status_code, 200)

    def test_forgot_password_post(self):
        mock_user_resource = MagicMock()
        mock_user_resource.create_verification_token.return_value = None
        with patch('app.routes.auth.users_resource.get_user_by_email', return_value={'id': 1, 'email': 'test@example.com'}), \
             patch('app.routes.auth.users_resource.user', return_value=mock_user_resource), \
             patch('app.routes.auth.resend.Emails.send'):
            response = self.client.post('/auth/forgot-password', data={'email': 'test@example.com'})
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/auth/login'))

    def test_reset_password_get_authorized(self):
        with patch('app.routes.auth.users_resource.verify_token', return_value={'user_id': 1, 'expiry': datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)}), \
             patch('app.routes.auth.render_template', return_value='OK'):
            response = self.client.get('/auth/reset-password?token=token')
            self.assertEqual(response.status_code, 200)

    def test_reset_password_post_authorized(self):
        mock_user_resource = MagicMock()
        with patch('app.routes.auth.users_resource.verify_token', return_value={'user_id': 1, 'expiry': datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)}), \
             patch('app.routes.auth.users_resource.user', return_value=mock_user_resource), \
             patch('app.routes.auth.users_resource.invalidate_token'):
            response = self.client.post('/auth/reset-password', data={
                'token': 'token',
                'password': 'SecurePass123!',
                'confirm_password': 'SecurePass123!'
            })
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.location.endswith('/auth/login'))

class TestLandingRoutes(BaseRouteTest):
    """Test suite for the landing routes in app.routes.landing."""

    def test_index_route(self):
        with patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)

    def test_about_route(self):
        with patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/about')
            self.assertEqual(response.status_code, 200)

    def test_legal_route(self):
        with patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/legal')
            self.assertEqual(response.status_code, 200)

    def test_contact_get_route(self):
        with patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/contact')
            self.assertEqual(response.status_code, 200)

    def test_contact_post_route(self):
        mock_smtp = MagicMock()
        mock_smtp.return_value.__enter__.return_value.login.return_value = None
        mock_smtp.return_value.__enter__.return_value.send_message.return_value = None
        with patch('app.routes.landing.smtplib.SMTP_SSL', mock_smtp), \
             patch.dict(os.environ, {'MAIL_USERNAME': 'test@example.com', 'MAIL_PASSWORD': 'secret'}), \
             patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.post('/contact', data={
                'name': 'Test',
                'email': 'test@example.com',
                'message': 'Hello'
            })
            self.assertEqual(response.status_code, 200)

    def test_features_route(self):
        with patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/features')
            self.assertEqual(response.status_code, 200)

    def test_homepage_route_authorized(self):
        self.login()
        with patch('app.routes.landing.ActivitiesResource.get_upcoming', return_value=[]), \
             patch('app.routes.landing.render_template', return_value='OK'):
            response = self.client.get('/home')
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

