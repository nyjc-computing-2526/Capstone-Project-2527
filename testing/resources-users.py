import unittest

import app.storage.db as db
from app.resources.users import UsersResource, UserResource


class TestUsersWithDbLayer(unittest.TestCase):

    def setUp(self):
        self.users = UsersResource()

        # Use db.py functions only (no raw SQL in tests)
        for u in db.get_activities() or []:
            db.db_execute("DELETE FROM participants", None)
        db.db_execute("DELETE FROM verification_tokens", None)
        db.db_execute("DELETE FROM users", None)
    # ======================================================
    # NORMAL CASES
    # ======================================================

    def test_register_normal(self):
        user_id = self.users.register({
            "email": "normal@test.com",
            "password": "password123",
            "name": "Normal User",
            "user_class": "1A"
        })

        user = db.get_user_by_id(user_id)

        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "normal@test.com")

    def test_update_normal(self):
        user_id = self.users.register({
            "email": "update@test.com",
            "password": "password123",
            "name": "Old Name",
            "user_class": "1A"
        })

        user = UserResource(user_id)
        result = user.update({"name": "New Name"})

        self.assertTrue(result)

        updated = db.get_user_by_id(user_id)
        self.assertEqual(updated["name"], "New Name")

    def test_delete_normal(self):
        user_id = self.users.register({
            "email": "delete@test.com",
            "password": "password123",
            "name": "To Delete",
            "user_class": "1A"
        })

        user = UserResource(user_id)
        result = user.delete()

        self.assertTrue(result)
        self.assertIsNone(db.get_user_by_id(user_id))

    # ======================================================
    # ABNORMAL CASES
    # ======================================================

    def test_duplicate_email(self):
        self.users.register({
            "email": "dup@test.com",
            "password": "password123",
            "name": "User1",
            "user_class": "1A"
        })

        with self.assertRaises(ValueError):
            self.users.register({
                "email": "dup@test.com",
                "password": "password123",
                "name": "User2",
                "user_class": "1A"
            })

    def test_empty_registration(self):
        with self.assertRaises(ValueError):
            self.users.register({
                "email": "",
                "password": "",
                "name": "",
                "user_class": ""
            })

    def test_invalid_update(self):
        user_id = self.users.register({
            "email": "invalid@test.com",
            "password": "password123",
            "name": "User",
            "user_class": "1A"
        })

        user = UserResource(user_id)

        with self.assertRaises(ValueError):
            user.update({})

    def test_invalid_user_id(self):
        with self.assertRaises(ValueError):
            UserResource(-999)

    # ======================================================
    # EXTREME CASES
    # ======================================================

    def test_long_input(self):
        long_str = "x" * 3000

        user_id = self.users.register({
            "email": f"{long_str}@test.com",
            "password": long_str,
            "name": long_str,
            "user_class": "1A"
        })

        user = db.get_user_by_id(user_id)
        self.assertIsNotNone(user)

    def test_special_characters(self):
        user_id = self.users.register({
            "email": "weird+123@test.com",
            "password": "!@#$%^&*()",
            "name": "名前🚀",
            "user_class": "1A"
        })

        user = db.get_user_by_id(user_id)
        self.assertEqual(user["email"], "weird+123@test.com")

    def test_sql_injection_like_input(self):
        user_id = self.users.register({
            "email": "safe@test.com",
            "password": "pass123",
            "name": "Safe"
        })

        user = UserResource(user_id)

        result = user.update({
            "name": "'; DROP TABLE users; --"
        })

        self.assertTrue(result)

        still_exists = db.get_user_by_id(user_id)
        self.assertIsNotNone(still_exists)


if __name__ == "__main__":
    unittest.main()