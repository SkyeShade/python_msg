"""Database configuration and CRUD operations for application messages."""

import json
from pathlib import Path

import mysql.connector


# Resolve the credentials file relative to this module so startup is independent
# of the application's current working directory.
CREDENTIALS_PATH = Path(__file__).with_name("credentials.json")

with CREDENTIALS_PATH.open(encoding="utf-8") as credentials_file:
    credentials = json.load(credentials_file)

# Keep one shared connection for the application's database operations.
db = mysql.connector.connect(**credentials)


def get_messages():
    """Return all messages ordered by their database ID."""
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
    """Create a message and persist it to the database."""
    cursor = db.cursor()
    cursor.execute("""INSERT INTO msg (title, msg) VALUES (%s, %s)""", (title, msg))
    db.commit()
    cursor.close()


def delete_message(id):
    """Delete the message matching the supplied database ID."""
    cursor = db.cursor()
    cursor.execute("""DELETE FROM msg WHERE ID = %s""", (id,))
    db.commit()
    cursor.close()


def update_message(id, title, msg):
    """Update a message and record the modification time."""
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
