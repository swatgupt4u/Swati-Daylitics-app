import psycopg2.extras
import datetime
from database import get_pool

def with_connection(func):
    """Decorator to inject a connection from the pool and handle commit/rollback."""
    def wrapper(*args, **kwargs):
        pool = get_pool()
        conn = pool.getconn()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            pool.putconn(conn)
    return wrapper

@with_connection
def add_task(cursor, user_email, date, name, category, priority, est_time_mins, is_default=0):
    cursor.execute('''
        INSERT INTO tasks (user_email, date, name, category, priority, est_time_mins, is_default)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (user_email, date, name, category, priority, est_time_mins, is_default))

@with_connection
def get_setting(cursor, user_email, key, default=None):
    cursor.execute('SELECT value FROM settings WHERE user_email = %s AND key = %s', (user_email, key))
    row = cursor.fetchone()
    return row[0] if row else default

@with_connection
def set_setting(cursor, user_email, key, value):
    cursor.execute('''
        INSERT INTO settings (user_email, key, value)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_email, key) 
        DO UPDATE SET value = EXCLUDED.value
    ''', (user_email, key, value))

@with_connection
def get_tasks_by_date(cursor, user_email, date):
    cursor.execute('''
        SELECT * FROM tasks WHERE user_email = %s AND date = %s
    ''', (user_email, date))
    return [dict(row) for row in cursor.fetchall()]

@with_connection
def update_task_status(cursor, user_email, task_id, status, actual_time_mins=0):
    cursor.execute('''
        UPDATE tasks 
        SET status = %s, actual_time_mins = %s
        WHERE id = %s AND user_email = %s
    ''', (status, actual_time_mins, task_id, user_email))

@with_connection
def update_task_details(cursor, user_email, task_id, name, category, priority, est_time_mins):
    cursor.execute('''
        UPDATE tasks 
        SET name = %s, category = %s, priority = %s, est_time_mins = %s
        WHERE id = %s AND user_email = %s
    ''', (name, category, priority, est_time_mins, task_id, user_email))

@with_connection
def delete_task(cursor, user_email, task_id):
    cursor.execute('DELETE FROM tasks WHERE id = %s AND user_email = %s', (task_id, user_email))

@with_connection
def save_reflection(cursor, user_email, date, mood, energy, notes, score):
    cursor.execute('''
        INSERT INTO reflections (user_email, date, mood, energy, notes, productivity_score)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_email, date) 
        DO UPDATE SET 
            mood = EXCLUDED.mood,
            energy = EXCLUDED.energy,
            notes = EXCLUDED.notes,
            productivity_score = EXCLUDED.productivity_score
    ''', (user_email, date, mood, energy, notes, score))

@with_connection
def get_reflection_by_date(cursor, user_email, date):
    cursor.execute('SELECT * FROM reflections WHERE user_email = %s AND date = %s', (user_email, date))
    row = cursor.fetchone()
    return dict(row) if row else None

@with_connection
def get_recent_reflections(cursor, user_email, limit_days=7):
    cursor.execute('''
        SELECT * FROM reflections 
        WHERE user_email = %s
        ORDER BY date DESC LIMIT %s
    ''', (user_email, limit_days))
    return [dict(row) for row in cursor.fetchall()]

@with_connection
def get_recent_tasks(cursor, user_email, limit_days=7):
    today = datetime.date.today()
    start_date = (today - datetime.timedelta(days=limit_days)).isoformat()
    cursor.execute('''
        SELECT * FROM tasks 
        WHERE user_email = %s AND date >= %s
        ORDER BY date DESC
    ''', (user_email, start_date))
    return [dict(row) for row in cursor.fetchall()]

@with_connection
def add_repeating_task(cursor, user_email, name, category, priority, est_time_mins):
    cursor.execute('''
        INSERT INTO repeating_tasks (user_email, name, category, priority, est_time_mins)
        VALUES (%s, %s, %s, %s, %s)
    ''', (user_email, name, category, priority, est_time_mins))

@with_connection
def get_repeating_tasks(cursor, user_email):
    cursor.execute('SELECT * FROM repeating_tasks WHERE user_email = %s', (user_email,))
    return [dict(row) for row in cursor.fetchall()]

@with_connection
def delete_repeating_task(cursor, user_email, task_id):
    cursor.execute('DELETE FROM repeating_tasks WHERE id = %s AND user_email = %s', (task_id, user_email))
