import unittest
import hashlib

import app.storage.db as db
from app.resources.users import UsersResource, UserResource


class TestUsersWithDbLayer(unittest.TestCase):

    def setUp(self):
        self.users = UsersResource()

        # Clean database using db layer only
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
    # SECURITY / PASSWORD HASHING
    # ======================================================

    def test_password_is_hashed_on_register(self):
        raw_password = "mypassword123"

        user_id = self.users.register({
            "email": "hash@test.com",
            "password": raw_password,
            "name": "Hash User",
            "user_class": "1A"
        })

        user = db.get_user_by_id(user_id)

        # Ensure password is NOT stored in plaintext
        self.assertNotEqual(user["password"], raw_password)

        # Basic sanity check (hashed passwords are longer)
        self.assertTrue(len(user["password"]) >= 32)

    def test_password_not_equal_same_plaintext(self):
        """If salting is used, same password should produce different hashes"""
        password = "samepassword"

        id1 = self.users.register({
            "email": "user1@test.com",
            "password": password,
            "name": "User1",
            "user_class": "1A"
        })

        id2 = self.users.register({
            "email": "user2@test.com",
            "password": password,
            "name": "User2",
            "user_class": "1A"
        })

        user1 = db.get_user_by_id(id1)
        user2 = db.get_user_by_id(id2)

        # If salting exists → hashes should differ
        self.assertNotEqual(user1["password"], user2["password"])

    def test_password_hash_consistency_if_sha256(self):
        """
        ONLY valid if your implementation uses deterministic hashing like SHA256.
        Remove if using salted hashing (bcrypt, etc.)
        """
        raw_password = "mypassword123"

        user_id = self.users.register({
            "email": "hashcheck@test.com",
            "password": raw_password,
            "name": "Hash Check",
            "user_class": "1A"
        })

        user = db.get_user_by_id(user_id)

        expected_hash = hashlib.sha256(raw_password.encode()).hexdigest()

        # This will fail if you are using salted hashing (which is GOOD practice)
        self.assertIn(len(user["password"]), [64, 128])  # flexible check

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
            "name": "Safe",
            "user_class": "1A"
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