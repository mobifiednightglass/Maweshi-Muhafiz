"""
User data validation — standalone, reusable by any route or service layer.

Provides two validators:

* ``validate_signup_data(data)`` — full validation for registration.
* ``validate_login_data(data)``  — lightweight presence check for login.

Both return a list of human-readable error strings; an empty list means
the data is valid.
"""
# server-side validation for user data (signup and login)
import re

# ---------------------------------------------------------------------------
# Field constraints
# ---------------------------------------------------------------------------
MAX_NAME_LENGTH = 100
MAX_EMAIL_LENGTH = 254  # RFC 5321 maximum
MIN_PASSWORD_LENGTH = 8

# Simple but practical email regex — not exhaustive, catches common mistakes
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


# ---------------------------------------------------------------------------
# Signup validation
# ---------------------------------------------------------------------------

def validate_signup_data(data: dict) -> list[str]:
    """Validate a signup payload.

    Checks:
    * ``name``     — required, non-empty string, max length.
    * ``email``    — required, valid email format, max length.
    * ``password`` — required, minimum 8 characters.

    Returns a list of error messages.  Empty list == data is valid.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Request body must be a JSON object."]

    # --- name -------------------------------------------------------------
    name = data.get("name")
    if name is None or (isinstance(name, str) and not name.strip()):
        errors.append("'name' is required.")
    elif not isinstance(name, str):
        errors.append("'name' must be a string.")
    elif len(name) > MAX_NAME_LENGTH:
        errors.append(f"'name' must be at most {MAX_NAME_LENGTH} characters long.")

    # --- email ------------------------------------------------------------
    email = data.get("email")
    if email is None or (isinstance(email, str) and not email.strip()):
        errors.append("'email' is required.")
    elif not isinstance(email, str):
        errors.append("'email' must be a string.")
    elif len(email) > MAX_EMAIL_LENGTH:
        errors.append(f"'email' must be at most {MAX_EMAIL_LENGTH} characters long.")
    elif not _EMAIL_RE.match(email.strip()):
        errors.append("'email' must be a valid email address.")

    # --- password ---------------------------------------------------------
    password = data.get("password")
    if password is None or (isinstance(password, str) and not password):
        errors.append("'password' is required.")
    elif not isinstance(password, str):
        errors.append("'password' must be a string.")
    elif len(password) < MIN_PASSWORD_LENGTH:
        errors.append(
            f"'password' must be at least {MIN_PASSWORD_LENGTH} characters long."
        )

    return errors


# ---------------------------------------------------------------------------
# Login validation
# ---------------------------------------------------------------------------

def validate_login_data(data: dict) -> list[str]:
    """Validate a login payload.

    Only checks that ``email`` and ``password`` are present and non-empty.
    No format or length constraints are applied here.

    Returns a list of error messages.  Empty list == data is valid.
    """
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["Request body must be a JSON object."]

    email = data.get("email")
    if email is None or (isinstance(email, str) and not email.strip()):
        errors.append("'email' is required.")

    password = data.get("password")
    if password is None or (isinstance(password, str) and not password):
        errors.append("'password' is required.")

    return errors
