import os
import sqlite3
from typing import Any, List, Optional, Tuple

APPDATA = os.getenv("APPDATA") or os.path.expanduser("~/.config")
DB_DIR = os.path.join(APPDATA, "WorkBuddy")
DB_PATH = os.path.join(DB_DIR, "workbuddy.db")

if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)


def get_connection() -> sqlite3.Connection:
    """Get a connection to the persistent WorkBuddy database."""
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Initialize the database tables if they do not exist."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                remind_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_done INTEGER DEFAULT 0
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                shown_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


init_db()


# Reminder functions
def add_reminder(message: str, remind_at: str) -> int:
    """Add a new reminder. Returns the reminder ID."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO reminders (message, remind_at) VALUES (?, ?)",
            (message, remind_at),
        )
        conn.commit()
        return c.lastrowid


def get_pending_reminders() -> List[Tuple[int, str, str]]:
    """Get all pending (not done) reminders."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, message, remind_at FROM reminders WHERE is_done = 0 ORDER BY remind_at ASC"
        )
        return c.fetchall()


def mark_reminder_done(reminder_id: int) -> None:
    """Mark a reminder as done."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE reminders SET is_done = 1 WHERE id = ?", (reminder_id,))
        conn.commit()


def get_all_reminders() -> list[tuple[int, str, str, int]]:
    """Get all reminders, including completed ones, with status."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, message, remind_at, is_done FROM reminders ORDER BY remind_at ASC"
        )
        return c.fetchall()


def update_reminder(reminder_id: int, new_message: str, new_remind_at: str) -> None:
    """Update the message and/or time of a reminder."""
    print(
        f"[Storage] update_reminder called with id={reminder_id}, new_message={new_message}, new_remind_at={new_remind_at}"
    )
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE reminders SET message = ?, remind_at = ? WHERE id = ?",
            (new_message, new_remind_at, reminder_id),
        )
        print(f"[Storage] update_reminder rows affected: {c.rowcount}")
        conn.commit()
        # Fetch and print the updated row for verification
        c.execute(
            "SELECT id, message, remind_at FROM reminders WHERE id = ?", (reminder_id,)
        )
        updated = c.fetchone()
        print(f"[Storage] update_reminder row after update: {updated}")


def get_all_reminders_with_status() -> list[dict]:
    """Get all reminders with their status as a string."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, message, remind_at, is_done FROM reminders ORDER BY remind_at ASC"
        )
        rows = c.fetchall()
        return [
            {
                "id": row[0],
                "message": row[1],
                "remind_at": row[2],
                "status": "Pending" if row[3] == 0 else "Done",
            }
            for row in rows
        ]


# Notes functions
def add_note(content: str) -> int:
    """Add a new note. Returns the note ID."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("INSERT INTO notes (content) VALUES (?)", (content,))
        conn.commit()
        return c.lastrowid


def get_notes() -> List[Tuple[int, str, str]]:
    """Get all notes."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT id, content, created_at FROM notes ORDER BY created_at DESC")
        return c.fetchall()


# Notification history functions
def add_notification(title: str, message: str) -> int:
    """Add a notification to the history. Returns the notification ID."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO notifications (title, message) VALUES (?, ?)",
            (title, message),
        )
        conn.commit()
        return c.lastrowid


def get_notifications() -> List[Tuple[int, str, str, str]]:
    """Get all notifications from history."""
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, title, message, shown_at FROM notifications ORDER BY shown_at DESC"
        )
        return c.fetchall()
