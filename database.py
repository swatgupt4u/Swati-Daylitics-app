import psycopg2
from psycopg2 import pool
import streamlit as st

@st.cache_resource
def get_pool():
    try:
        url = st.secrets["DATABASE_URL"]
    except KeyError:
        st.error("Missing DATABASE_URL in .streamlit/secrets.toml!")
        st.stop()
    return psycopg2.pool.SimpleConnectionPool(1, 20, url)

def init_db():
    db_pool = get_pool()
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()

        # Create tasks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_email TEXT,
            date TEXT,
            name TEXT,
            category TEXT,
            priority TEXT,
            est_time_mins INTEGER,
            actual_time_mins INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            is_default INTEGER DEFAULT 0
        )
        ''')

        # Create repeating_tasks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS repeating_tasks (
            id SERIAL PRIMARY KEY,
            user_email TEXT,
            name TEXT,
            category TEXT,
            priority TEXT,
            est_time_mins INTEGER
        )
        ''')

        # Create settings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            user_email TEXT,
            key TEXT,
            value TEXT,
            PRIMARY KEY (user_email, key)
        )
        ''')

        # Create reflections table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reflections (
            user_email TEXT,
            date TEXT,
            mood INTEGER,
            energy INTEGER,
            notes TEXT,
            productivity_score REAL,
            PRIMARY KEY (user_email, date)
        )
        ''')

        conn.commit()
    except Exception as e:
        print(f"Database Initialization Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        db_pool.putconn(conn)
