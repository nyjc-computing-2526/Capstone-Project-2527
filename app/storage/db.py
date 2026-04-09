import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

ALLOWED_COLUMNS = ["id", "name", "description", "date", "created_by", "student", "participants"]

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

def get_owned (user_id: int):
    pass

def get_joined (user_id: int):
    pass

def create_activity(data: dict):
    for col in data.keys():
        if col not in ALLOWED_COLUMNS:
            raise ValueError(f'Invalid column: {col}')
        
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = tuple(data.values())

    query =  f"INSERT INTO activities ({columns}) VALUES ({placeholders}) RETURNING id"
    result = db_execute(sql_query=query, params=values, fetch="one")

    if result == 0:
        raise ValueError("Activity was unable to be created")
    else:
        return result["id"]

def delete_activity(activity_id):
    query = """DELETE FROM activities WHERE id = %s"""
    result = db_execute(query, params=[activity_id])

    if result == 0:
        return False
    else:
        return True

def update_activity(data: dict):
    if "id" not in data.keys():
        return False
    
    update_data = {k:v for k,v in data.items() if k != "id"}

    for col in update_data.keys():
        if col not in ALLOWED_COLUMNS:
            return False
    
    columns = ",".join([f"{col} = %s" for col in update_data.keys()])
    values = tuple(update_data.values()) + (data["id"],)

    query = f"UPDATE SET activities SET {columns} WHERE id = %s"
    updated = db_execute(sql_query=query, params=values, fetch=None)

    if updated == 0:
        return False
    
    return True

def join_acitivity(activity_id, user_id):
    pass


## ========= User Functions ===========

def create_user (data: dict):
    pass

def update_user (data: dict):
    pass

def delete_user (user_id):
    pass

def get_user_by_email (email: str):
    pass

def get_user_by_id (user_id: str):
    pass
