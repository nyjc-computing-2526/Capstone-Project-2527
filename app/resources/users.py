import hashlib
import os
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import app.storage.db as db

ALLOWED_USER_COLUMNS = {'email', 'password', 'name', 'user_class', 'verified', 'failed_attempts', 'lock_until', 'lockout_count'}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_COOLDOWN_SECONDS = (30, 60, 180, 300)


class UsersResource:
    """Resource class for managing users collection operations."""

    def _normalize_lock_until(self, lock_until):
        if not lock_until:
            return None
        if lock_until.tzinfo is None:
            return lock_until.replace(tzinfo=timezone.utc)
        return lock_until

    def _lockout_message(self, seconds_remaining: int) -> str:
        minutes = seconds_remaining // 60
        seconds = seconds_remaining % 60
        if minutes > 0:
            return f"Too many failed attempts. Please try again in {minutes}m {seconds}s."
        return f"Too many failed attempts. Please try again in {seconds}s."

    def _record_failed_login(self, user: dict) -> str:
        now = datetime.now(timezone.utc)
        failed_attempts = int(user.get('failed_attempts', 0) or 0) + 1
        lockout_count = int(user.get('lockout_count', 0) or 0)
        lock_until = None

        if failed_attempts >= MAX_LOGIN_ATTEMPTS:
            cooldown_seconds = LOGIN_COOLDOWN_SECONDS[min(lockout_count, len(LOGIN_COOLDOWN_SECONDS) - 1)]
            lock_until = now + timedelta(seconds=cooldown_seconds)
            failed_attempts = 0
            lockout_count += 1
            message = f"Too many failed attempts. Please try again in {cooldown_seconds} seconds."
        else:
            remaining = MAX_LOGIN_ATTEMPTS - failed_attempts
            message = f"Invalid credentials. {remaining} attempt(s) remaining."

        self.user(user['id']).update({
            "failed_attempts": failed_attempts,
            "lock_until": lock_until,
            "lockout_count": lockout_count,
        })
        return message

    def reset_login_lockout(self, user_id: int) -> bool:
        return self.user(user_id).update({
            "failed_attempts": 0,
            "lock_until": None,
            "lockout_count": 0,
        })

    def authenticate_with_lockout(self, email: str, password: str) -> dict:
        user = self.get_user_by_email(email)

        if user:
            now = datetime.now(timezone.utc)
            lock_until = self._normalize_lock_until(user.get('lock_until'))
            if lock_until and now < lock_until:
                remaining = int((lock_until - now).total_seconds())
                raise ValueError(self._lockout_message(remaining))

        try:
            return self.authenticate(email, password)
        except ValueError:
            if user:
                raise ValueError(self._record_failed_login(user))
            raise ValueError("Invalid credentials.") from None

    def get_user_by_email(self, email: str) -> dict | None:
        """helper to fetch user by email safely."""
        if not isinstance(email, str) or not email.strip():
            return None
        clean_email = email.strip().lower()
        try:
            return db.get_user_by_email(clean_email)
        except Exception:
            return None

    def user(self, user_id: int) -> "UserResource":
        """Get a UserResource instance for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            UserResource: An instance of UserResource for the user.
        """
        return UserResource(user_id)

    def authenticate(self, email: str, password: str) -> dict:
        """Authenticate user with email and password."""
        if not isinstance(email, str) or not email.strip():
            raise ValueError("Email is required")
        if not isinstance(password, str) or not password:
            raise ValueError("Password is required")

        user = self.get_user_by_email(email)
        if not user or not user.get('password'):
            raise ValueError("Invalid email or password")

        try:
            stored_password = user['password']
            salt_hex, hash_hex = stored_password.split(':', 1)
            salt = bytes.fromhex(salt_hex)

            hashed_input = hashlib.pbkdf2_hmac(
                'sha256', password.encode('utf-8'), salt, 100000
            )

            if hmac.compare_digest(hashed_input.hex(), hash_hex):
                return user

            raise ValueError("Invalid email or password")

        except ValueError:
            raise
        except Exception:
            raise ValueError("Authentication service temporarily unavailable") from None

    def register(self, user_data: dict) -> int:
        """Register a new user."""
        if not isinstance(user_data, dict):
            raise ValueError("Data must be a dictionary")

        sanitized_data = {k: v for k, v in user_data.items() if k in ALLOWED_USER_COLUMNS}

        for field in ['email', 'password', 'name', 'user_class']:
            val = sanitized_data.get(field)
            if not isinstance(val, str) or not val.strip():
                raise ValueError(f"Field '{field}' must be a non-empty string")

        sanitized_data['email'] = sanitized_data['email'].strip().lower()
        sanitized_data['name'] = sanitized_data['name'].strip()

        if self.get_user_by_email(sanitized_data['email']):
            raise ValueError("A user with this email already exists")

        try:
            salt = secrets.token_bytes(32)
            hashed_password = hashlib.pbkdf2_hmac(
                'sha256',
                sanitized_data['password'].encode('utf-8'),
                salt,
                100000
            )
            sanitized_data['password'] = f"{salt.hex()}:{hashed_password.hex()}"

            return db.create_user(sanitized_data)

        except Exception as e:
            raise ValueError(e) from None
    
    def verify_token(self, token: str, type: str) -> dict | None:
        """Verify a password reset token.

        Args:
            token (str): The token to verify.
            type (str): The type of token to verify.

        Returns:
            dict: The token data if valid, None if invalid or expired.

        Raises:
            ValueError: If token verification fails.
        """
        try:
            return db.verify_token(token, type)
        except Exception as e:
            raise ValueError("Failed to verify token") from None
    
    def invalidate_token(self, token: str):
        try:
            db.invalidate_token(token)
        except Exception as e:
            raise ValueError("Failed to invalidate token") from None


class UserResource:
    """Resource class for managing individual user operations."""

    def __init__(self, user_id: int):
        """Initialize UserResource with a user ID.

        Args:
            user_id (int): The ID of the user.

        Raises:
            ValueError: If user_id is invalid.
        """
        try:
            self.user_id = int(user_id)
            if self.user_id <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("User ID must be a positive integer")

    def get(self):
        """Retrieve the user details.

        Returns:
            dict: The user data without password.

        Raises:
            ValueError: If user not found or retrieval fails.
        """
        try:
            user = db.get_user_by_id(self.user_id)
            if user is None:
                raise ValueError(f"User {self.user_id} not found")
            return user
        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to retrieve user {self.user_id}") from e

    def update(self, user_data: dict) -> bool:
        """Update the user with new data.

        Args:
            user_data (dict): Dictionary containing fields to update.

        Returns:
            bool: True if update was successful.

        Raises:
            ValueError: If user_data is invalid or update fails.
        """
        if not isinstance(user_data, dict):
            raise ValueError("Update data must be a dictionary")

        updates = {"id": self.user_id}
        for k in ALLOWED_USER_COLUMNS:
            if k not in user_data:
                continue

            val = user_data[k]
            if isinstance(val, bool):
                updates[k] = val
            elif isinstance(val, int):
                updates[k] = val
            elif isinstance(val, datetime):
                updates[k] = val
            elif val is None and k == "lock_until":
                updates[k] = None
            elif isinstance(val, str) and val.strip():
                updates[k] = val.strip()

        if len(updates) == 1:
            raise ValueError("No valid fields provided for update")

        if 'email' in updates:
            updates['email'] = updates['email'].lower()

        if 'password' in updates:
            salt = secrets.token_bytes(32)
            hashed = hashlib.pbkdf2_hmac(
                'sha256',
                updates['password'].encode('utf-8'),
                salt,
                100000
            )
            updates['password'] = f"{salt.hex()}:{hashed.hex()}"

        try:
            success = db.update_user(updates)
            if not success:
                raise ValueError("User not found")
            return success
        except Exception as e:
            print("Actual error: " + str(e))
            raise ValueError("Update failed") from None

    def delete(self) -> bool:
        """Delete the user.

        Returns:
            bool: True if deletion was successful.

        Raises:
            ValueError: If deletion fails.
        """
        try:
            user = db.get_user_by_id(self.user_id)
            if user is None:
                raise ValueError(f"User {self.user_id} not found")

            for activity in db.get_owned(self.user_id):
                activity_id = activity["id"]
                db.delete_participant_activity(activity_id)
                deleted_activity = db.delete_activity(activity_id)
                if not deleted_activity:
                    raise ValueError(f"Failed to delete owned activity {activity_id}")

            db.delete_participant_user(self.user_id)
            db.delete_verification_tokens_for_user(self.user_id)

            success = db.delete_user(self.user_id)
            if not success:
                raise ValueError(f"User {self.user_id} not found")

            return success
        except ValueError:
            raise
        except Exception as e:
            raise ValueError("Delete failed") from None
        
    def create_verification_token(self, data: dict):
        """Create a verification token for password reset.

        Args:
            token (str): The token to be stored.
            expires_at (datetime): The expiration time of the token.
            type (str): The type of verification token.
        Returns:
            bool: True if token creation was successful.
        Raises:
            ValueError: If token creation fails.
        """
        try:
            data['user_id'] = self.user_id
            db.create_verification_token(data)
        except Exception as e:
            raise ValueError("Failed to create verification token") from None
