import sqlite3
import uuid
from datetime import datetime, timezone

from app.config import settings


def initialize_tickets_database() -> None:
    """
    Ensure the support tickets table exists in the database.
    """
    connection = sqlite3.connect(settings.database_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS support_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL UNIQUE,
                user_id TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                summary TEXT NOT NULL,
                requires_human_review INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def create_ticket(
    authenticated_user_id: str,
    category: str,
    priority: str,
    summary: str,
    requires_human_review: bool = True,
) -> dict:
    """
    Deterministically log an HR / IT support ticket into the database.
    """
    initialize_tickets_database()
    ticket_id = f"TICK-{uuid.uuid4().hex[:8].upper()}"
    created_at = datetime.now(timezone.utc).isoformat()

    connection = sqlite3.connect(settings.database_path)
    try:
        connection.execute(
            """
            INSERT INTO support_tickets (
                ticket_id,
                user_id,
                category,
                priority,
                summary,
                requires_human_review,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                authenticated_user_id,
                category,
                priority,
                summary,
                1 if requires_human_review else 0,
                "created",
                created_at,
            ),
        )
        connection.commit()

        return {
            "success": True,
            "ticket_id": ticket_id,
            "category": category,
            "priority": priority,
            "summary": summary,
            "requires_human_review": requires_human_review,
            "status": "created",
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }
    finally:
        connection.close()
