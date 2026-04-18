import unittest

# IMPORTANT: must be first
from db_for_testing import use_test_db, reset_db

use_test_db()

from app.resources.users import UsersResource, UserResource


class TestUsersIntegration(unittest.TestCase):

    def setUp(self):
        reset_db()
        self.users = UsersResource()

    # -------------------------
    # REGISTER TESTS
    # -------------------------
    def test_register_success(self):
        user_id = self.users.register({
            "email": "test@test.com",
            "password": "123",
            "name": "Test User",
            "user_class": "1A"
        })

        self.assertIsInstance(user_id, int)
        self.assertGreater(user_id, 0)

    def test_register_duplicate_email(self):
        self.users.register({
            "email": "test@test.com",
            "password": "123",
            "name": "Test User",
            "user_class": "1A"
        })

        with self.assertRaises(ValueError):
            self.users.register({
                "email": "test@test.com",
                "password": "456",
                "name": "Another",
                "user_class": "1B"
            })

    # -------------------------
    # AUTH TESTS
    # -------------------------
    def test_authenticate_success(self):
        self.users.register({
            "email": "auth@test.com",
            "password": "mypassword",
            "name": "Auth User",
            "user_class": "1A"
        })

        user = self.users.authenticate("auth@test.com", "mypassword")
        self.assertEqual(user["email"], "auth@test.com")

    def test_authenticate_failure_wrong_password(self):
        self.users.register({
            "email": "auth2@test.com",
            "password": "mypassword",
            "name": "Auth User",
            "user_class": "1A"
        })

        with self.assertRaises(ValueError):
            self.users.authenticate("auth2@test.com", "wrongpassword")

    def test_authenticate_failure_wrong_email(self):
        with self.assertRaises(ValueError):
            self.users.authenticate("doesnotexist@test.com", "password")

    # -------------------------
    # GET ALL TESTS
    # -------------------------
    def test_get_all_returns_list(self):
        self.users.register({
            "email": "a@test.com",
            "password": "123",
            "name": "A",
            "user_class": "1A"
        })

        self.users.register({
            "email": "b@test.com",
            "password": "123",
            "name": "B",
            "user_class": "1A"
        })

        users = self.users.get_all()

        self.assertIsInstance(users, list)
        self.assertGreaterEqual(len(users), 2)

    # -------------------------
    # UPDATE TESTS
    # -------------------------
    def test_update_user_name(self):
        user_id = self.users.register({
            "email": "update@test.com",
            "password": "123",
            "name": "Old Name",
            "user_class": "1A"
        })

        user = UserResource(user_id)
        result = user.update({"name": "New Name"})

        self.assertTrue(result)

        updated = user.get()
        self.assertEqual(updated["name"], "New Name")

    def test_update_password(self):
        user_id = self.users.register({
            "email": "pw@test.com",
            "password": "123",
            "name": "Test",
            "user_class": "1A"
        })

        user = UserResource(user_id)
        result = user.update({"password": "newpass"})

        self.assertTrue(result)

        updated = user.get()
        self.assertNotEqual(updated["password"], "newpass")
        self.assertIn(":", updated["password"])

    def test_update_verified_boolean(self):
        user_id = self.users.register({
            "email": "verified@test.com",
            "password": "123",
            "name": "Test",
            "user_class": "1A"
        })

        user = UserResource(user_id)
        result = user.update({"verified": True})

        self.assertTrue(result)

        updated = user.get()
        self.assertTrue(updated.get("verified"))

    def test_update_invalid_no_fields(self):
        user_id = self.users.register({
            "email": "empty@test.com",
            "password": "123",
            "name": "Test",
            "user_class": "1A"
        })

        user = UserResource(user_id)

        with self.assertRaises(ValueError):
            user.update({})

    # -------------------------
    # DELETE TESTS
    # -------------------------
    def test_delete_user_success(self):
        user_id = self.users.register({
            "email": "delete@test.com",
            "password": "123",
            "name": "Delete Me",
            "user_class": "1A"
        })

        user = UserResource(user_id)

        result = user.delete()

        self.assertTrue(result)

        with self.assertRaises(ValueError):
            user.get()

    def test_delete_nonexistent_user(self):
        user = UserResource(99999)

        with self.assertRaises(ValueError):
            user.delete()

    # -------------------------
    # TOKEN TESTS
    # -------------------------
    def test_verify_token_invalid(self):
        result = self.users.verify_token("fake-token", "reset")
        self.assertIsNone(result)

    def test_invalidate_token_no_error(self):
        # should not raise even if token doesn't exist
        try:
            self.users.invalidate_token("fake-token")
        except Exception as e:
            self.fail(f"invalidate_token raised unexpectedly: {e}")


if __name__ == "__main__":
    unittest.main()