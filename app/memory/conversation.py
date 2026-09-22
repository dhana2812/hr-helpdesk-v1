import sqlite3
from datetime import datetime, timezone

from app.config import settings


def _get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_memory_database() -> None:
    """
    Create the persistent conversation table if it does not already exist.
    """

    connection = _get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def _normalize_message(message: str) -> str:
    """
    Normalize message text for duplicate detection.

    This is intentionally conservative:
    - removes leading/trailing whitespace
    - collapses repeated whitespace
    - performs case-insensitive comparison

    It does not modify the actual stored message.
    """

    return " ".join(message.strip().split()).casefold()


def filter_messages(
    messages: list[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Remove empty and redundant conversation messages.

    Duplicate detection is based on:
    - role
    - normalized message content

    The original ordering is preserved.

    The returned records contain both:
    - message: the original storage-compatible field
    - content: a compatibility field for chat-style consumers
    """

    filtered_messages: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for message in messages:
        role = message.get("role", "")

        content = message.get("message")

        if content is None:
            content = message.get("content", "")

        if not isinstance(role, str):
            continue

        if not isinstance(content, str) or not content.strip():
            continue

        duplicate_key = (
            role,
            _normalize_message(content),
        )

        if duplicate_key in seen:
            continue

        seen.add(duplicate_key)

        filtered_messages.append(
            {
                "role": role,
                "message": content,
                "content": content,
            }
        )

    return filtered_messages


def _is_duplicate_message(
    connection: sqlite3.Connection,
    *,
    conversation_id: str,
    user_id: str,
    role: str,
    message: str,
) -> bool:
    """
    Check whether the same message already exists in the conversation.

    Duplicate detection is scoped to:
    - conversation_id
    - user_id
    - role
    - normalized message text
    """

    normalized_message = _normalize_message(message)

    rows = connection.execute(
        """
        SELECT message
        FROM conversation_messages
        WHERE conversation_id = ?
          AND user_id = ?
          AND role = ?
        ORDER BY id
        """,
        (
            conversation_id,
            user_id,
            role,
        ),
    ).fetchall()

    for row in rows:
        if _normalize_message(row["message"]) == normalized_message:
            return True

    return False


def save_message(
    *,
    conversation_id: str,
    user_id: str,
    role: str,
    message: str,
) -> bool:
    """
    Persist a conversation message.

    Returns:
        True  -> message was stored
        False -> message was detected as a duplicate and was not stored
    """

    if not message or not message.strip():
        return False

    initialize_memory_database()

    connection = _get_connection()

    try:
        if _is_duplicate_message(
            connection,
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            message=message,
        ):
            return False

        connection.execute(
            """
            INSERT INTO conversation_messages (
                conversation_id,
                user_id,
                role,
                message,
                timestamp
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                user_id,
                role,
                message,
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        connection.commit()
        return True

    finally:
        connection.close()


def load_recent_messages(
    *,
    conversation_id: str,
    user_id: str,
    limit: int = 20,
) -> list[dict[str, str]]:
    """
    Load recent conversation messages for the authenticated user.

    Duplicate messages are filtered again during retrieval as a
    defense-in-depth measure.

    Both `message` and `content` are returned for compatibility
    with existing application consumers.
    """

    initialize_memory_database()

    connection = _get_connection()

    try:
        rows = connection.execute(
            """
            SELECT role, message
            FROM conversation_messages
            WHERE conversation_id = ?
              AND user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                conversation_id,
                user_id,
                limit,
            ),
        ).fetchall()

    finally:
        connection.close()

    rows = list(reversed(rows))

    messages: list[dict[str, str]] = []

    for row in rows:
        message_text = row["message"]

        messages.append(
            {
                "role": row["role"],
                "message": message_text,
                "content": message_text,
            }
        )

    return filter_messages(messages)