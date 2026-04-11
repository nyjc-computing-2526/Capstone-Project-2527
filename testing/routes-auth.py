import unittest
from app import create_app
from unittest.mock import patch
from datetime import datetime, timezone, timedelta


class TestAuth(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    # ------------------------
    # BASIC PAGE LOAD TESTS
    # ------------------------
    def test_login_page_loads(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)

    def test_forgot_password_page(self):
        response = self.client.get('/auth/forgot-password')
        self.assertEqual(response.status_code, 200)

    # ------------------------
    # LOGIN TESTS
    # ------------------------
    @patch('app.resources.users.UsersResource.authenticate')
    def test_login_success(self, mock_auth):
        mock_auth.return_value = {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com'
        }

        response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': '123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    @patch('app.resources.users.UsersResource.authenticate')
    def test_login_fail(self, mock_auth):
        mock_auth.side_effect = ValueError("Invalid credentials")

        response = self.client.post('/auth/login', data={
            'email': 'something like this shouldn"t pass',
            'password': 'wrong'
        })

        self.assertIn(b'Invalid credentials', response.data)

    # ------------------------
    # REGISTER TESTS
    # ------------------------
    @patch('app.resources.users.UsersResource.register')
    def test_register_success(self, mock_register):
        response = self.client.post('/auth/register', data={
            'email': 'test@test.com',
            'password': '123',
            'confirm_password': '123',
            'name': 'Test',
            'class': '1A'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    def test_register_password_mismatch(self):
        response = self.client.post('/auth/register', data={
            'email': 'test@test.com',
            'password': '123',
            'confirm_password': '456',
            'name': 'Test',
            'class': '1A'
        })

        self.assertIn(b'Passwords do not match', response.data)

    # ------------------------
    # LOGOUT TESTS
    # ------------------------
    def test_logout_requires_login(self):
        response = self.client.post('/auth/logout')
        self.assertEqual(response.status_code, 302)  # redirect

    @patch('app.resources.users.UsersResource.authenticate')
    def test_logout_after_login(self, mock_auth):
        mock_auth.return_value = {
            'id': 1,
            'name': 'Test',
            'email': 'test@test.com'
        }

        # login first
        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': '123'
        })

        response = self.client.post('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # ------------------------
    # FORGOT PASSWORD TEST
    # ------------------------
    @patch('app.resources.users.UsersResource.get_user_by_email')
    @patch('resend.Emails.send')
    def test_forgot_password(self, mock_send, mock_get_user):
        mock_get_user.return_value = {"id": 1}

        response = self.client.post('/auth/forgot-password', data={
            'email': 'test@test.com'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    # ------------------------
    # RESET PASSWORD TESTS
    # ------------------------
    @patch('app.resources.users.UsersResource.verify_token')
    def test_reset_password_get_valid(self, mock_verify):

        mock_verify.return_value = {
            "user_id": 1,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
        }

        response = self.client.get('/auth/reset-password?token=abc')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'resetpassword', response.data.lower())

    # -----------------------------
    # GET - INVALID TOKEN
    # -----------------------------
    @patch('app.resources.users.UsersResource.verify_token')
    def test_reset_password_get_invalid(self, mock_verify):

        mock_verify.return_value = None

        response = self.client.get('/auth/reset-password?token=bad')

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Invalid token', response.data)

    # -----------------------------
    # GET - MISSING TOKEN
    # -----------------------------
    def test_reset_password_get_missing_token(self):

        response = self.client.get('/auth/reset-password')

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Missing token', response.data)

    # -----------------------------
    # POST - SUCCESS CASE
    # -----------------------------
    @patch('app.resources.users.UsersResource.invalidate_token')
    @patch('app.resources.users.UsersResource.user')
    @patch('app.resources.users.UsersResource.verify_token')
    def test_reset_password_post_success(self, mock_verify, mock_user, mock_invalidate):

        mock_verify.return_value = {
            "user_id": 1,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
        }

        # 🔥 Fix chained call: user().update()
        mock_user_instance = mock_user.return_value
        mock_user_instance.update = MagicMock()

        response = self.client.post('/auth/reset-password', data={
            "token": "abc",
            "password": "newpassword"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)

    # -----------------------------
    # POST - EXPIRED TOKEN
    # -----------------------------
    @patch('app.resources.users.UsersResource.verify_token')
    def test_reset_password_post_expired(self, mock_verify):

        mock_verify.return_value = {
            "user_id": 1,
            "expires_at": datetime.now(timezone.utc) - timedelta(minutes=5)
        }

        response = self.client.post('/auth/reset-password', data={
            "token": "abc",
            "password": "newpassword"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Token expired', response.data)

if __name__ == '__main__':
    unittest.main()