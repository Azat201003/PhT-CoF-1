import os
import sqlite3
from datetime import datetime, timedelta

def init_db_if_not_exists(path: str):
    if os.path.isfile(path):
        return
    try:
        with sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as connection:
            cursor = connection.cursor()

            cursor.execute("""
                DROP TABLE IF EXISTS habits;
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    habit_id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_useful BOOlEAN
                );
            """)

            cursor.execute("""
                DROP TABLE IF EXISTS done;
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS done (
                    done_id INTEGER PRIMARY KEY,
                    time TIMESTAMP,
                    habit_id INTEGER,
                    FOREIGN KEY (habit_id) REFERENCES habits (habit_id)
                );
            """)

            habits_data = [
                ('workout', True),
                ('nail-biting', False)
            ]
            cursor.executemany("INSERT INTO habits (name, is_useful) VALUES (?, ?)", habits_data)
            
            done_data = [
                (datetime.now(), 1),
                (datetime.now()-timedelta(minutes=9), 1),
                (datetime.now()-timedelta(minutes=5), 2)
            ]
            cursor.executemany("INSERT INTO done (time, habit_id) VALUES (?, ?)", done_data)
            
            cursor.execute("SELECT * FROM done")
            results = cursor.fetchall()

            for row in results:
                print(*row)
    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")


