# Import libraries
import sqlite3
from datetime import datetime

DB_NAME = "t1d_alerts.db" 

#function to create the necessary tables in the database if they do not already exist

def create_tables():
    # Connect to the database - creates the file if it does not exist
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    # Table 1 - exercise sessions imported from calendar
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exercise_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            alert_time TEXT,
            imported_at TEXT
        )
    ''')

    # Table 2 - alert log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            alert_type TEXT,
            sent_at TEXT,
            acknowledged INTEGER DEFAULT 0
        )
    ''')

    # Table 3 - glucose readings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS glucose_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            glucose_level INTEGER,
            classification TEXT,
            recorded_at TEXT
        )
    ''')

    sql_connection.commit()
    sql_connection.close()


def session_exists(title, start_time):
    # Connect to database
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    # Search for a session with the same title and start time
    cursor.execute('''
        SELECT id FROM exercise_sessions
        WHERE title = ? AND start_time = ?
    ''', (title, start_time))

    result = cursor.fetchone()
    sql_connection.close()

    # If result is not None, the session already exists
    return result is not None

def save_session(title, start_time, end_time, alert_time):
    # Check for duplicate before saving
    if session_exists(title, str(start_time)):
        print(f"  Skipping duplicate: {title} at {start_time}")
        return False

    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    cursor.execute('''
        INSERT INTO exercise_sessions 
        (title, start_time, end_time, alert_time, imported_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        title,
        str(start_time),
        str(end_time),
        str(alert_time),
        str(datetime.now())
    ))

    sql_connection.commit()
    sql_connection.close()
    return True

def save_glucose(session_id, glucose_level, classification):
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    cursor.execute('''
        INSERT INTO glucose_readings
        (session_id, glucose_level, classification, recorded_at)
        VALUES (?, ?, ?, ?)
    ''', (
        session_id,
        glucose_level,
        classification,
        str(datetime.now())
    ))

    sql_connection.commit()
    sql_connection.close()

def save_alert(session_id, alert_type):
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    cursor.execute('''
        INSERT INTO alert_log
        (session_id, alert_type, sent_at, acknowledged)
        VALUES (?, ?, ?, ?)
    ''', (
        session_id,
        alert_type,
        str(datetime.now()),
        0
    ))

    sql_connection.commit()
    sql_connection.close()

def get_all_sessions():
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    cursor.execute('''
        SELECT id, title, start_time, end_time, alert_time, imported_at
        FROM exercise_sessions
        ORDER BY start_time ASC
    ''')

    rows = cursor.fetchall()
    sql_connection.close()
    return rows


def get_pending_alerts():
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    # Find sessions whose alert time has passed and have not been alerted yet
    cursor.execute('''
        SELECT id, title, start_time, alert_time
        FROM exercise_sessions
        WHERE alert_time <= ?
        AND id NOT IN (SELECT session_id FROM alert_log)
    ''', (str(datetime.now()),))

    rows = cursor.fetchall()
    sql_connection.close()
    return rows


def get_glucose_readings():
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    cursor.execute('''
        SELECT id, session_id, glucose_level, classification, recorded_at
        FROM glucose_readings
        ORDER BY recorded_at DESC
    ''')

    rows = cursor.fetchall()
    sql_connection.close()
    return rows

def save_settings(child_name, has_cgm, alert_lead_minutes):
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    # Create settings table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            child_name TEXT,
            has_cgm INTEGER,
            alert_lead_minutes INTEGER
        )
    ''')

    # Delete existing settings and insert new ones
    cursor.execute('DELETE FROM settings')
    cursor.execute('''
        INSERT INTO settings (id, child_name, has_cgm, alert_lead_minutes)
        VALUES (1, ?, ?, ?)
    ''', (child_name, int(has_cgm), alert_lead_minutes))

    sql_connection.commit()
    sql_connection.close()

def get_settings():
    sql_connection = sqlite3.connect(DB_NAME)
    cursor = sql_connection.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            child_name TEXT,
            has_cgm INTEGER,
            alert_lead_minutes INTEGER
        )
    ''')

    cursor.execute('SELECT child_name, has_cgm, alert_lead_minutes FROM settings WHERE id = 1')
    result = cursor.fetchone()
    sql_connection.close()

    # Return defaults if no settings saved yet
    if result is None:
        return {'child_name': 'Riot', 'has_cgm': False, 'alert_lead_minutes': 30}

    return {
        'child_name': result[0],
        'has_cgm': bool(result[1]),
        'alert_lead_minutes': result[2]
    }

if __name__ == '__main__':
    # Step 1 - create tables
    create_tables()
    print("Database and tables created successfully.")

    # Step 2 - save a test session
    from datetime import timedelta
    start = datetime(2026, 4, 10, 14, 0, 0)
    end = datetime(2026, 4, 10, 15, 0, 0)
    alert = start - timedelta(minutes=30)

    result = save_session('Soccer Practice', start, end, alert)
    print(f"Session saved: {result}")

    # Step 3 - test duplicate detection
    result2 = save_session('Soccer Practice', start, end, alert)
    print(f"Duplicate saved: {result2}")

    # Step 4 - save a glucose reading
    save_glucose(1, 145, 'Ideal Starting Zone')
    print("Glucose reading saved.")

    # Step 5 - save an alert
    save_alert(1, 'SMS')
    print("Alert logged.")

    # Step 6 - retrieve and display all sessions
    print("\n--- All Sessions ---")
    sessions = get_all_sessions()
    for s in sessions:
        print(f"  ID:{s[0]} | {s[1]} | Start: {s[2]} | Alert: {s[4]}")

    # Step 7 - retrieve glucose readings
    print("\n--- Glucose Readings ---")
    readings = get_glucose_readings()
    for r in readings:
        print(f"  Session:{r[1]} | Glucose: {r[2]} | {r[3]} | {r[4]}")