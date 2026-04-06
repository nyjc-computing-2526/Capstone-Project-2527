import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

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
            conn.commit()
            result = cursor.rowcount

    except Exception as e:
        conn.rollback() #to make sure failed queries dosent decrement capacity
        raise e

    finally:
        cursor.close()
        conn.close()

    return result


def get_activities():
    query = """SELECT * FROM activities"""
    return db_execute(sql_query=query, params=None, fetch="all")


def get_activity_by_id(id):
    query = """SELECT * FROM activities WHERE id = %s"""
    params = (id,)
    return db_execute(sql_query=query, params=params, fetch="one")


def create_activity(data: dict):
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    values = tuple(data.values())

    query =  f"INSERT INTO activities ({columns}) VALUES ({placeholders}) RETURNING id"
    return db_execute(sql_query=query, params=values, fetch="one")["id"]