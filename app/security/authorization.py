class AuthorizationError(Exception):
    """Raised when a user attempts to access another employee's data."""


def authorize_employee_access(
    authenticated_user_id: str,
    requested_employee_id: str,
) -> None:
    """
    Allow access only when the requested employee ID matches
    the authenticated user's employee ID.
    """

    if authenticated_user_id != requested_employee_id:
        raise AuthorizationError(
            "Access denied: employees can only access their own records."
        )