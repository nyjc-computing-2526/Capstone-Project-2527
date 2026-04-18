import os
import psycopg2


def use_test_db():
    """
    Point all DB calls to the test database.
    MUST be called before importing anything that uses db.py.
    """
    os.environ["DATABASE_URL"] = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql://user:password@postgres:5432/test_db"
    )


def reset_db():
    """
    Wipes and recreates schema for a clean test state.
    """
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("""
    DROP TABLE IF EXISTS participants;
    DROP TABLE IF EXISTS verification_tokens;
    DROP TABLE IF EXISTS activities;
    DROP TABLE IF EXISTS users;
    """)

    cur.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        user_class TEXT,
        verified BOOLEAN DEFAULT FALSE
    );
    """)

    cur.execute("""
    CREATE TABLE activities (
        id SERIAL PRIMARY KEY,
        title TEXT,
        description TEXT,
        date TIMESTAMP,
        started_at TIMESTAMP,
        ended_at TIMESTAMP,
        created_by INTEGER REFERENCES users(id),
        venue TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE participants (
        user_id INTEGER REFERENCES users(id),
        activity_id INTEGER REFERENCES activities(id)
    );
    """)

    cur.execute("""
    CREATE TABLE verification_tokens (
        user_id INTEGER REFERENCES users(id),
        token TEXT,
        expiry TIMESTAMP,
        type TEXT
    );
    """)

    conn.commit()
    cur.close()
    conn.close()