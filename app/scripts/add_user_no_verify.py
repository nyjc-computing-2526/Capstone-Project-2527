import argparse

from app.resources.users import UsersResource


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new user account without email verification.")
    parser.add_argument("email", help="User email")
    parser.add_argument("password", help="User password")
    parser.add_argument("name", help="User full name")
    parser.add_argument("user_class", help="User class / year group")
    args = parser.parse_args()

    users = UsersResource()
    user_id = users.register_without_verification({
        "email": args.email,
        "password": args.password,
        "name": args.name,
        "user_class": args.user_class,
    })
    print(f"Created user id: {user_id}")


if __name__ == "__main__":
    main()
