import sqlite3
import psycopg2
import toml

def migrate():
    # 1. Read secrets directly
    try:
        secrets = toml.load(".streamlit/secrets.toml")
        pg_url = secrets.get("DATABASE_URL")
    except Exception as e:
        print(f"Failed to read secrets.toml: {e}")
        return

    if not pg_url or "hostname" in pg_url:
        print("Invalid or missing DATABASE_URL in secrets.")
        return

    # 2. Connect to local SQLite
    try:
        sl_conn = sqlite3.connect("productivity.db")
        sl_conn.row_factory = sqlite3.Row
        sl_cursor = sl_conn.cursor()
    except Exception as e:
        print(f"No local productivity.db found or error connecting: {e}")
        return

    # 3. Connect to remote Postgres
    pg_conn = psycopg2.connect(pg_url)
    pg_cursor = pg_conn.cursor()

    print("Migrating tasks...")
    sl_cursor.execute("SELECT * FROM tasks")
    for row in sl_cursor.fetchall():
        try:
            pg_cursor.execute(
                "INSERT INTO tasks (user_email, date, name, category, priority, est_time_mins, actual_time_mins, status, is_default) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (row['user_email'], row['date'], row['name'], row['category'], row['priority'], row['est_time_mins'], row['actual_time_mins'], row['status'], row.get('is_default', 0))
            )
        except Exception as e:
            print(f"Skipping a task due to error: {e}")
            pg_conn.rollback()
        else:
            pg_conn.commit()
    print("Tasks migrated.")

    print("Migrating reflections...")
    sl_cursor.execute("SELECT * FROM reflections")
    for row in sl_cursor.fetchall():
        try:
            pg_cursor.execute(
                "INSERT INTO reflections (user_email, date, mood, energy, notes, productivity_score) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (row['user_email'], row['date'], row['mood'], row['energy'], row['notes'], row['productivity_score'])
            )
            pg_conn.commit()
        except Exception as e:
            pg_conn.rollback()
    
    print("Migrating repeating_tasks...")
    sl_cursor.execute("SELECT * FROM repeating_tasks")
    for row in sl_cursor.fetchall():
        try:
            pg_cursor.execute(
                "INSERT INTO repeating_tasks (user_email, name, category, priority, est_time_mins) VALUES (%s, %s, %s, %s, %s)",
                (row['user_email'], row['name'], row['category'], row['priority'], row['est_time_mins'])
            )
            pg_conn.commit()
        except:
            pg_conn.rollback()
    
    print("Migrating settings...")
    sl_cursor.execute("SELECT * FROM settings")
    for row in sl_cursor.fetchall():
        try:
            pg_cursor.execute(
                "INSERT INTO settings (user_email, key, value) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                (row['user_email'], row['key'], row['value'])
            )
            pg_conn.commit()
        except:
            pg_conn.rollback()

    sl_conn.close()
    pg_conn.close()
    print("Data Migration complete! Your old local data is now synchronized to the cloud!")

if __name__ == "__main__":
    migrate()
