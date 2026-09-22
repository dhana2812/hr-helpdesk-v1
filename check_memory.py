import sqlite3

connection = sqlite3.connect("data/hr_helpdesk.db")

try:
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT conversation_id, user_id, role, message
        FROM conversation_messages
        WHERE conversation_id = ?
        ORDER BY id
        """,
        ("memory-demo-001",),
    )

    rows = cursor.fetchall()

    print("=" * 60)
    print("MEMORY DATABASE CHECK")
    print("=" * 60)

    for row in rows:
        print(row)

    print("=" * 60)
    print(f"Total messages: {len(rows)}")

finally:
    connection.close()