import unittest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.storage import db


class TestDBExecuteValidation(unittest.TestCase):

    def test_invalid_fetch_value(self):
        with self.assertRaises(ValueError):
            db.db_execute("SELECT 1", fetch="invalid")


class TestActivityFunctions(unittest.TestCase):

    @patch("app.storage.db.db_execute")
    @patch("app.storage.db.join_activity")
    def test_create_activity_success(self, mock_join, mock_db):
        mock_db.return_value = {"id": 1}

        data = {
            "title": "Test",
            "description": "Desc",
            "date": "2025-01-01",
            "started_at": "2025-01-01 10:00",
            "ended_at": "2025-01-01 12:00",
            "created_by": 99,
            "venue": "Room A",
            "private": False
        }

        result = db.create_activity(data)

        self.assertEqual(result, 1)
        mock_join.assert_called_once_with(1, 99)

    def test_create_activity_invalid_column(self):
        data = {"invalid_col": "oops"}

        with self.assertRaises(ValueError):
            db.create_activity(data)

    @patch("app.storage.db.db_execute")
    def test_update_activity_success(self, mock_db):
        mock_db.return_value = 1

        data = {"id": 1, "title": "Updated"}

        result = db.update_activity(data)

        self.assertTrue(result)

    def test_update_activity_missing_id(self):
        result = db.update_activity({"title": "No ID"})
        self.assertFalse(result)

    def test_update_activity_invalid_column(self):
        result = db.update_activity({"id": 1, "bad": "value"})
        self.assertFalse(result)


class TestParticipantFunctions(unittest.TestCase):

    @patch("app.storage.db.db_execute")
    def test_join_activity_success(self, mock_db):
        mock_db.return_value = 1

        result = db.join_activity(1, 2)

        self.assertTrue(result)

    @patch("app.storage.db.db_execute")
    def test_leave_activity_success(self, mock_db):
        mock_db.return_value = 1

        result = db.leave_activity(1, 2)

        self.assertTrue(result)

    @patch("app.storage.db.db_execute")
    def test_update_participant_attendance(self, mock_db):
        mock_db.return_value = 1

        result = db.update_participant_attendance(
            1, 2, "present", "on time", 99
        )

        self.assertTrue(result)


class TestUserFunctions(unittest.TestCase):

    @patch("app.storage.db.db_execute")
    def test_create_user_success(self, mock_db):
        mock_db.return_value = {"id": 10}

        data = {
            "name": "Test",
            "email": "test@test.com",
            "password": "hashed",
            "user_class": "A",
            "verified": False,
            "failed_attempts": 0,
            "locked_until": None,
            "lockout_count": 0
        }

        result = db.create_user(data)

        self.assertEqual(result, 10)

    def test_create_user_invalid_column(self):
        with self.assertRaises(ValueError):
            db.create_user({"bad": "value"})

    @patch("app.storage.db.db_execute")
    def test_update_user_success(self, mock_db):
        mock_db.return_value = 1

        result = db.update_user({"id": 1, "name": "New"})

        self.assertTrue(result)

    def test_update_user_invalid(self):
        result = db.update_user({"id": 1, "bad": "value"})
        self.assertFalse(result)


class TestVerificationTokenFunctions(unittest.TestCase):

    @patch("app.storage.db.db_execute")
    def test_verify_token_valid(self, mock_db):
        future_time = datetime.now(timezone.utc) + timedelta(hours=1)

        mock_db.return_value = {
            "token": "abc",
            "type": "email",
            "expiry": future_time
        }

        result = db.verify_token("abc", "email")

        self.assertIsNotNone(result)

    @patch("app.storage.db.db_execute")
    def test_verify_token_expired(self, mock_db):
        past_time = datetime.now(timezone.utc) - timedelta(hours=1)

        mock_db.return_value = {
            "token": "abc",
            "type": "email",
            "expiry": past_time
        }

        result = db.verify_token("abc", "email")

        self.assertIsNone(result)

    @patch("app.storage.db.db_execute")
    def test_verify_token_not_found(self, mock_db):
        mock_db.return_value = None

        result = db.verify_token("abc", "email")

        self.assertIsNone(result)

    @patch("app.storage.db.db_execute")
    def test_invalidate_token_success(self, mock_db):
        mock_db.side_effect = [1, 2]  # first delete, then cleanup

        result = db.invalidate_token("abc")

        self.assertTrue(result)

    @patch("app.storage.db.db_execute")
    def test_invalidate_token_not_found(self, mock_db):
        mock_db.return_value = 0

        result = db.invalidate_token("abc")

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()