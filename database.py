import json
from pathlib import Path

import mysql.connector


CREDENTIALS_PATH = Path(__file__).with_name("credentials.json")

with CREDENTIALS_PATH.open(encoding="utf-8") as credentials_file:
    credentials = json.load(credentials_file)

db = mysql.connector.connect(**credentials)


def get_messages():
    cursor = db.cursor()

    cursor.execute("""
        SELECT ID, title, msg, msg_time, last_updated
        FROM msg
        ORDER BY ID
    """)

    rows = cursor.fetchall()
    cursor.close()

    return rows

def create_message(title, msg):
    cursor = db.cursor()
    cursor.execute("""INSERT INTO msg (title, msg) VALUES (%s, %s)""", (title, msg))
    db.commit()
    cursor.close()

def delete_message(id):
    cursor = db.cursor()
    cursor.execute("""DELETE FROM msg WHERE ID = %s""", (id,))
    db.commit()
    cursor.close()

def update_message(id, title, msg):
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE msg
        SET title = %s,
            msg = %s,
            last_updated = CURRENT_TIMESTAMP
        WHERE ID = %s
        """,
        (title, msg, id)
    )



    db.commit()
    cursor.close()
