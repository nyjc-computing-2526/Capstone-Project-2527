import os
import json
import re
import psycopg2
import psycopg2.extras
import psycopg2.pool
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

ALLOWED_COLUMNS_ACTIVITIES = ["title", "description", "date", "started_at", "created_by", "ended_at", "venue", "private"]
ALLOWED_COLUMNS_PARTICIPANTS = ["user_id", "activity_id", "attendance_status", "attendance_reason", "attendance_marked_at", "attendance_marked_by"]
ALLOWED_COLUMNS_USERS = ["name", "email", "password", "user_class", "verified", "failed_attempts", "locked_until", "lockout_count"]
ALLOWED_COLUMNS_VERIFICATION_TOKENS = ["user_id", "token", "expiry", "type"]
ALLOWED_COLUMNS_SECURITY_AUDIT_LOGS = [
    "user_id",
    "user_email",
    "http_method",
    "request_path",
    "endpoint",
    "ip_address",
    "user_agent",
    "resource_name",
    "resource_action",
    "target_id",
    "request_metadata",
]
_CONNECTION_POOL = None


def _get_security_audit_log_table():
    table_name = os.getenv("SECURITY_AUDIT_LOG_TABLE", "security_audit_logs")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError("SECURITY_AUDIT_LOG_TABLE must be a simple SQL identifier")
    return table_name


def _get_connection_pool():
    global _CONNECTION_POOL
    if _CONNECTION_POOL is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set")
        minconn = int(os.getenv("DB_POOL_MIN_CONN", "1"))
        maxconn = int(os.getenv("DB_POOL_MAX_CONN", "5"))
        _CONNECTION_POOL = psycopg2.pool.ThreadedConnectionPool(
            minconn=minconn,
            maxconn=maxconn,
            dsn=database_url,
            connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "5")),
        )
    return _CONNECTION_POOL


def _get_db_connection():
    if os.getenv("DISABLE_DB_POOLING", "false").lower() in {"1", "true", "yes", "on"}:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set")
        return psycopg2.connect(
            database_url,
            connect_timeout=int(os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "5")),
        ), False
    return _get_connection_pool().getconn(), True


def _release_db_connection(conn, from_pool: bool, *, close: bool = False):
    if from_pool:
        _get_connection_pool().putconn(conn, close=close)
    else:
        conn.close()

def db_execute(sql_query, params=None, fetch=None):
    """
    Arguments:
        sql_query: SQL string with %s placeholders if params
        params: tuple/list of values to safely inject (optional)
        fetch: 'one', 'all', or None (for INSERT/UPDATE/DELETE)

    Returns:
        - 'all'  → list of dicts
        - 'one'  → single dict (or None)
        - None   → rowcount (int)
    """
    if fetch not in ("all", "one", None):
        raise ValueError(f"fetch must be 'all', 'one' or None -- got {fetch}")

    conn, from_pool = _get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) #returns rows as dicts instead of tuples

    try:
        cursor.execute(sql_query, params) #psycopg2 handles params=None by itself

        if fetch == "all":
            result = cursor.fetchall()
        elif fetch == "one":
            result = cursor.fetchone()
        else:
            result = cursor.rowcount

        conn.commit()

    except Exception as e:
        conn.rollback() #to make sure failed queries dosent decrement capacity
        if from_pool:
            _release_db_connection(conn, from_pool=True, close=True)
            from_pool = False
        raise e

    finally:
        cursor.close()
        _release_db_connection(conn, from_pool)

    return result

## ========= Activity Functions ===========
def get_activities():
    query = """SELECT * FROM activities"""
    return db_execute(sql_query=query, params=None, fetch="all")


def get_activity_by_id(id):
    query = """SELECT * FROM activities WHERE id = %s"""
    params = [id]
    return db_execute(sql_query=query, params=params, fetch="one")

def get_completed_activities():
    query = """SELECT * FROM activities WHERE ended_at < NOW();"""
    return db_execute(sql_query=query, params=None, fetch="all")

def get_upcoming_activities():
    query = """SELECT * FROM activities WHERE started_at > NOW();"""
    return db_execute(sql_query=query, params=None, fetch="all")

def get_ongoing_activities():
    query = """
        SELECT * FROM activities 
        WHERE started_at <= NOW()
        AND ended_at >= NOW();
    """
    return db_execute(sql_query=query, params=None, fetch="all")

def create_activity(data: dict):
    for col in data.keys():
        if col not in ALLOWED_COLUMNS_ACTIVITIES:
            raise ValueError(f'Invalid column: {col}')
        
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = tuple(data.values())

    query =  f"INSERT INTO activities ({columns}) VALUES ({placeholders}) RETURNING id"
    result = db_execute(sql_query=query, params=values, fetch="one")    

    activity_id = result["id"]
    creator_id = data["created_by"]

    join_activity(activity_id, creator_id)

    return activity_id

def delete_activity(activity_id):
    query = """DELETE FROM activities WHERE id = %s"""
    result = db_execute(query, params=[activity_id], fetch=None)

    return (result == 1)

def update_activity(data: dict):
    if "id" not in data.keys():
        return False
    
    update_data = {k:v for k,v in data.items() if k != "id"}

    for col in update_data.keys():
        if col not in ALLOWED_COLUMNS_ACTIVITIES:
            return False
    
    columns = ",".join([f"{col} = %s" for col in update_data.keys()])
    values = tuple(update_data.values()) + (data["id"],)

    query = f"UPDATE activities SET {columns} WHERE id = %s"
    updated = db_execute(sql_query=query, params=values, fetch=None)

    return (updated == 1)

def get_owned (user_id: int):
    """get Public activities created by user_id"""
    query = """SELECT * FROM activities WHERE created_by = %s"""
    return db_execute(sql_query=query, params=[user_id], fetch="all")


def get_joined (user_id: int):
    """get Public activities attended by user_id"""
    query = """SELECT activities.* FROM activities 
                JOIN participants ON participants.activity_id = activities.id
                WHERE participants.user_id = %s"""
    return db_execute(sql_query=query, params=[user_id], fetch="all")

## ========= Participants Functions ===========
def get_participant(activity_id, user_id):
    query = """SELECT * FROM participants where activity_id = %s AND user_id = %s"""
    params = [activity_id, user_id]
    return db_execute(sql_query=query, params=params, fetch="one")
    

def get_participants(activity_id):
    query = """SELECT users.id, users.name, users.email, participants.attendance_status, participants.attendance_reason, participants.attendance_marked_at, participants.attendance_marked_by
               FROM participants 
               JOIN users ON users.id = participants.user_id
               WHERE participants.activity_id = %s"""
    return db_execute(sql_query=query, params=[activity_id], fetch="all")

def join_activity(activity_id, user_id):
    query = """INSERT INTO participants (user_id, activity_id) VALUES (%s, %s)"""
    joined = db_execute(sql_query=query, params=[user_id, activity_id], fetch=None)
    
    return (joined == 1)

def leave_activity(activity_id, user_id):
    query = """DELETE FROM participants WHERE user_id = %s AND activity_id = %s"""
    left = db_execute(sql_query=query, params=[user_id, activity_id], fetch=None)
    
    return (left == 1)

def delete_participant_activity(activity_id):
    query = """DELETE FROM participants WHERE activity_id = %s"""
    left = db_execute(sql_query=query, params=[activity_id], fetch=None)
    
    return (left >= 0)

def delete_participant_user(user_id):
    query = """DELETE FROM participants WHERE user_id = %s"""
    left = db_execute(sql_query=query, params=[user_id], fetch=None)
    
    return (left == 1)

def update_participant_attendance(activity_id, user_id, status, reason, marked_by):
    query = """UPDATE participants
        SET attendance_status = %s, attendance_reason = %s, attendance_marked_at = NOW(), attendance_marked_by = %s
        WHERE activity_id = %s AND user_id = %s;"""
    params = [status, reason, marked_by, activity_id, user_id]

    rowcount = db_execute(query, params, fetch=None)

    return (rowcount == 1)

def get_due_activity_reminders(hours_before=24):
    query = """
        SELECT
            participants.user_id,
            participants.activity_id,
            users.name AS user_name,
            users.email AS user_email,
            activities.title,
            activities.venue,
            activities.started_at
        FROM participants
        JOIN users ON users.id = participants.user_id
        JOIN activities ON activities.id = participants.activity_id
        WHERE participants.reminder_sent_at IS NULL
        AND activities.started_at > NOW()
        AND activities.started_at <= NOW() + (%s * INTERVAL '1 hour')
    """
    return db_execute(sql_query=query, params=[hours_before], fetch="all")

def mark_activity_reminder_sent(activity_id, user_id):
    query = """
        UPDATE participants
        SET reminder_sent_at = NOW()
        WHERE activity_id = %s AND user_id = %s AND reminder_sent_at IS NULL
    """
    result = db_execute(sql_query=query, params=[activity_id, user_id], fetch=None)
    return result == 1

## ========= User Functions ===========

def get_user_by_email (email: str):
    query = """SELECT * FROM users WHERE email = %s"""
    params = [email]
    return db_execute(sql_query=query, params=params, fetch="one")

def get_user_by_id (user_id: int):
    query = """SELECT * FROM users WHERE id = %s"""
    params = [user_id]
    return db_execute(sql_query=query, params=params, fetch="one")

def create_user(data: dict):
    for col in data.keys():
        if col not in ALLOWED_COLUMNS_USERS:
            raise ValueError(f'Invalid column: {col}')
        
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = tuple(data.values())

    query = f"INSERT INTO users ({columns}) VALUES ({placeholders}) RETURNING id"
    result = db_execute(sql_query=query, params=values, fetch="one")

    return result["id"]

def update_user (data: dict):
    if "id" not in data.keys():
        return False
    
    update_data = {k:v for k,v in data.items() if k != "id"}

    for col in update_data.keys():
        if col not in ALLOWED_COLUMNS_USERS:
            return False
    
    columns = ",".join([f"{col} = %s" for col in update_data.keys()])
    values = tuple(update_data.values()) + (data["id"],)

    query = f"UPDATE users SET {columns} WHERE id = %s"
    updated = db_execute(sql_query=query, params=values, fetch=None)

    return (updated == 1)

def delete_user (user_id):
    query = """DELETE FROM users WHERE id = %s"""
    result = db_execute(query, params=[user_id], fetch=None)

    return (result == 1)

## ========= Verification Token Functions ===========

def create_verification_token(data: dict):
    for col in data.keys():
        if col not in ALLOWED_COLUMNS_VERIFICATION_TOKENS:
            raise ValueError(f'Invalid column: {col}')
        
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = tuple(data.values())

    query =  f"INSERT INTO verification_tokens ({columns}) VALUES ({placeholders})"
    result = db_execute(sql_query=query, params=values, fetch=None)

    return (result == 1)
    

def verify_token(token: str, type: str) -> dict | None:
    query = """SELECT * FROM verification_tokens WHERE token = %s AND type = %s"""
    result = db_execute(sql_query=query, params=[token, type], fetch="one")

    if result is None:
        return None

    if result["expiry"] < datetime.now(timezone.utc):
        return None

    return result

def invalidate_token(token: str):
    query = """DELETE FROM verification_tokens WHERE token = %s"""
    result = db_execute(sql_query=query, params=[token], fetch=None)
    
    if result == 0:
        return False
    
    # Clear all tokens that are invalid
    query = """DELETE FROM verification_tokens WHERE expiry < NOW()"""
    result = db_execute(sql_query=query, params=None, fetch=None)

    return (result >= 1)

def delete_verification_tokens_for_user(user_id):
    query = """DELETE FROM verification_tokens WHERE user_id = %s"""
    deleted = db_execute(sql_query=query, params=[user_id], fetch=None)

    return (deleted >= 0)


def insert_security_audit_log(data: dict) -> bool:
    for col in data.keys():
        if col not in ALLOWED_COLUMNS_SECURITY_AUDIT_LOGS:
            raise ValueError(f"Invalid column: {col}")

    payload = dict(data)
    if "request_metadata" in payload:
        payload["request_metadata"] = psycopg2.extras.Json(
            payload["request_metadata"],
            dumps=lambda value: json.dumps(value, default=str),
        )

    columns = ", ".join(payload.keys())
    placeholders = ", ".join(["%s"] * len(payload))
    values = tuple(payload.values())
    table_name = _get_security_audit_log_table()

    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    inserted = db_execute(sql_query=query, params=values, fetch=None)
    return inserted == 1
