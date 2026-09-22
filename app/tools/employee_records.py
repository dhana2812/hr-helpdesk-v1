import sqlite3

from app.config import settings
from app.security.authorization import authorize_employee_access


def get_leave_balance(
    authenticated_user_id: str,
    requested_employee_id: str,
    leave_type: str,
) -> dict:
    """
    Deterministically retrieve an employee's leave balance.

    Authorization is enforced by the backend before employee
    data is returned.
    """

    try:
        authorize_employee_access(
            authenticated_user_id,
            requested_employee_id,
        )
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
        }

    allowed_leave_types = {
        "casual": "casual_leave",
        "sick": "sick_leave",
    }

    if leave_type not in allowed_leave_types:
        return {
            "success": False,
            "error": f"Unsupported leave type: {leave_type}",
        }

    connection = sqlite3.connect(settings.employee_db_path)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT employee_id, employee_name, casual_leave, sick_leave
            FROM employees
            WHERE employee_id = ?
            """,
            (requested_employee_id,),
        )

        employee = cursor.fetchone()

        if employee is None:
            return {
                "success": False,
                "error": "Employee not found.",
            }

        database_column = allowed_leave_types[leave_type]
        balance = employee[database_column]

        return {
            "success": True,
            "employee_id": employee["employee_id"],
            "employee_name": employee["employee_name"],
            "leave_type": leave_type,
            "balance": balance,
        }

    finally:
        connection.close()