import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

ALLOWED_COLUMNS_ACTIVITIES = ["title", "description", "date", "started_at", "created_by", "ended_at", "venue"]
ALLOWED_COLUMNS_PARTICIPANTS = ["user_id", "activity_id"]
ALLOWED_COLUMNS_USERS = ["name", "email", "password", "user_class", "verified"]
ALLOWED_COLUMNS_VERIFICATION_TOKENS = ["user_id", "token", "expiry", "type"]

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
    
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
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
        raise e

    finally:
        cursor.close()
        conn.close()

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
    query = """SELECT * FROM activities WHERE ended_at < NOW()"""
    return db_execute(sql_query=query, params=None, fetch="all")

def get_upcoming_activities():
    query = """SELECT * FROM activities WHERE started_at > NOW()"""
    return db_execute(sql_query=query, params=None, fetch="all")

def create_activity(data: dict):
    for col in data.keys():
        if col not in ALLOWED_COLUMNS_ACTIVITIES:
            raise ValueError(f'Invalid column: {col}')
        
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = tuple(data.values())

    query =  f"INSERT INTO activities ({columns}) VALUES ({placeholders})"
    result = db_execute(sql_query=query, params=values, fetch=None)

    return (result == 1)

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
    """get all activities created by user_id"""
    query = """SELECT * FROM activities WHERE created_by = %s"""
    return db_execute(sql_query=query, params=[user_id], fetch="all")


def get_joined (user_id: int):
    """get all activities attended by user_id"""
    query = """SELECT activities.* FROM activities 
                JOIN participants ON participants.activity_id = activities.id
                WHERE participants.user_id = %s"""
    return db_execute(sql_query=query, params=[user_id], fetch="all")

## ========= Participants Functions ===========

def get_participants(activity_id):
    query = """SELECT * FROM participants WHERE id = %s"""
    params = [activity_id]
    return db_execute(sql_query=query, params=params, fetch="one")

def join_activity(user_id, activity_id):
    query = """INSERT INTO participants (user_id, activity_id) VALUES (%s, %s)"""
    joined = db_execute(sql_query=query, params=[user_id, activity_id], fetch=None)
    
    return (joined == 1)

def leave_activity(user_id, activity_id):
    query = """DELETE FROM participants WHERE user_id = %s AND activity_id = %s"""
    left = db_execute(sql_query=query, params=[user_id, activity_id], fetch=None)
    
    return (left == 1)

def delete_participant_activity(activity_id):
    query = """DELETE FROM participants WHERE activity_id = %s"""
    left = db_execute(sql_query=query, params=[activity_id], fetch=None)
    
    return (left == 1)

def delete_participant_user(user_id):
    query = """DELETE FROM participants WHERE user_id = %s"""
    left = db_execute(sql_query=query, params=[user_id], fetch=None)
    
    return (left == 1)

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

    return (result == 1)

