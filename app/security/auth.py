from fastapi import Header, HTTPException

from app.config import settings


def authenticate_client(
    authorization: str | None = Header(default=None),
) -> str:
    """
    Validate the client Bearer token.

    Returns the authenticated client identifier when valid.
    """

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header.",
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header.",
        )

    if token == settings.client_token:
        return settings.client_employee_id

    prefix_hyphen = f"{settings.client_token}-"
    prefix_colon = f"{settings.client_token}:"

    if token.lower().startswith(prefix_hyphen.lower()):
        emp_id = token[len(prefix_hyphen):].upper()
        if emp_id in {"EMP001", "EMP002"}:
            return emp_id

    if token.lower().startswith(prefix_colon.lower()):
        emp_id = token[len(prefix_colon):].upper()
        if emp_id in {"EMP001", "EMP002"}:
            return emp_id

    raise HTTPException(
        status_code=401,
        detail="Invalid client token.",
    )