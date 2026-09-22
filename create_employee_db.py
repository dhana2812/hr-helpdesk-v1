import sqlite3

from app.config import settings


def create_database():
    connection = sqlite3.connect(settings.employee_db_path)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            employee_name TEXT NOT NULL,
            casual_leave INTEGER NOT NULL,
            sick_leave INTEGER NOT NULL,
            travel_reimbursement_status TEXT NOT NULL
        )
    """)

    employees = [
        (
            "EMP001",
            "Arun Kumar",
            8,
            5,
            "Pending",
        ),
        (
            "EMP002",
            "Priya Sharma",
            12,
            4,
            "Approved",
        ),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO employees (
            employee_id,
            employee_name,
            casual_leave,
            sick_leave,
            travel_reimbursement_status
        )
        VALUES (?, ?, ?, ?, ?)
    """, employees)

    connection.commit()
    connection.close()

    print("Employee database created successfully.")
    print("Database:", settings.employee_db_path)
    print("Employees loaded: 2")


if __name__ == "__main__":
    create_database()