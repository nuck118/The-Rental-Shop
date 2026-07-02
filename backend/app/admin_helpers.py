"""Shared helpers for the SQLAdmin panel."""

from __future__ import annotations

import json
import re
from typing import Any

from markupsafe import Markup
from starlette.requests import Request
from wtforms.validators import ValidationError

from app.core.audit import log_audit
from app.core.database import SessionLocal
from app.core.user import hash_password
from app.models.user import User

HARDWARE_STATUSES = [
    ("Available", "Available"),
    ("In Use", "In Use"),
    ("Repair", "Repair"),
    ("Unknown", "Unknown"),
]

SENSITIVE_FIELDS = frozenset({"password", "password_hash"})

# Bootstrap 5 semantic colour tokens for each status
STATUS_STYLES = {
    "Available": ("success", "✓"),
    "In Use":    ("primary", "●"),
    "Repair":    ("warning", "⚠"),
    "Unknown":   ("secondary", "?"),
}

ACTION_STYLES = {
    "CREATE": "success",
    "UPDATE": "primary",
    "DELETE": "danger",
}


def status_badge(status: str | None) -> Markup:
    """Render a hardware status as an editorial outlined badge."""
    label = status or "Unknown"
    colour, icon = STATUS_STYLES.get(label, STATUS_STYLES["Unknown"])
    return Markup(
        f"<span class='border border-{colour} text-{colour} rounded-0 px-2 py-1 text-uppercase'"
        f" style='font-size:0.7rem;font-weight:700;letter-spacing:0.05em;'>"
        f"{icon} {label}</span>"
    )


def action_badge(action: str | None) -> Markup:
    """Render an audit action as an editorial outlined badge."""
    label = action or "UNKNOWN"
    colour = ACTION_STYLES.get(label, "secondary")
    return Markup(
        f"<span class='border border-{colour} text-{colour} rounded-0 px-2 py-1 text-uppercase'"
        f" style='font-size:0.7rem;font-weight:700;letter-spacing:0.05em;'>"
        f"{label}</span>"
    )


def boolean_badge(value: bool, true_label: str, false_label: str) -> Markup:
    """Render a boolean value as an editorial outlined badge."""
    if value:
        return Markup(
            f"<span class='border border-success text-success rounded-0 px-2 py-1 text-uppercase'"
            f" style='font-size:0.7rem;font-weight:700;letter-spacing:0.05em;'>✓ {true_label}</span>"
        )
    return Markup(
        f"<span class='border border-secondary text-secondary rounded-0 px-2 py-1 text-uppercase'"
        f" style='font-size:0.7rem;font-weight:700;letter-spacing:0.05em;'>✗ {false_label}</span>"
    )


def _parse_json_values(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return {"value": raw}
    if isinstance(parsed, dict):
        return parsed
    return {"value": parsed}


def format_change_history(old_values: str | None, new_values: str | None) -> Markup:
    """Render old/new audit values as a readable change table."""
    old_data = _parse_json_values(old_values)
    new_data = _parse_json_values(new_values)
    all_keys = sorted(set(old_data) | set(new_data))

    if not all_keys:
        return Markup("<p class='admin-muted'>No field changes recorded.</p>")

    rows: list[str] = []
    for key in all_keys:
        old_value = old_data.get(key, "—")
        new_value = new_data.get(key, "—")
        changed = old_value != new_value
        row_class = "admin-change-row admin-change-row--changed" if changed else "admin-change-row"
        rows.append(
            "<tr class='{row_class}'>"
            "<th scope='row'>{key}</th>"
            "<td>{old_value}</td>"
            "<td>{new_value}</td>"
            "</tr>".format(
                row_class=row_class,
                key=_escape(str(key)),
                old_value=_escape(str(old_value)),
                new_value=_escape(str(new_value)),
            )
        )

    table = (
        "<div class='admin-change-table-wrap'>"
        "<table class='admin-change-table'>"
        "<thead><tr><th>Field</th><th>Previous</th><th>Current</th></tr></thead>"
        "<tbody>{rows}</tbody>"
        "</table></div>"
    ).format(rows="".join(rows))
    return Markup(table)


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def safe_snapshot(data: dict[str, Any] | None) -> dict[str, str] | None:
    """Build an audit-safe snapshot, excluding sensitive fields."""
    if not data:
        return None
    snapshot: dict[str, str] = {}
    for key, value in data.items():
        if key in SENSITIVE_FIELDS:
            continue
        if value is None or value == "":
            continue
        snapshot[key] = str(value)
    return snapshot or None


def model_snapshot(model: Any, fields: list[str]) -> dict[str, str]:
    """Capture selected model attributes for audit logging."""
    snapshot: dict[str, str] = {}
    for field in fields:
        if field in SENSITIVE_FIELDS:
            continue
        value = getattr(model, field, None)
        if value is None or value == "":
            continue
        snapshot[field] = str(value)
    return snapshot


def get_admin_user_id(request: Request) -> int:
    user_id = getattr(request.state, "admin_user_id", None)
    return user_id or 1


def get_request_meta(request: Request) -> tuple[str | None, str | None]:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


def write_audit_log(
    request: Request,
    *,
    action: str,
    table_name: str,
    record_id: int,
    old_values: dict[str, str] | None = None,
    new_values: dict[str, str] | None = None,
    description: str | None = None,
) -> None:
    """Persist an audit log entry using the shared audit helper."""
    db = SessionLocal()
    try:
        ip_address, user_agent = get_request_meta(request)
        log_audit(
            db=db,
            user_id=get_admin_user_id(request),
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    finally:
        db.close()


def apply_password_from_form(data: dict[str, Any], is_create: bool) -> None:
    """Move plain-text password from form data into password_hash."""
    password = data.pop("password", None)
    if password:
        data["password_hash"] = hash_password(password)
        return
    if not is_create:
        data.pop("password_hash", None)


def validate_unique_username(form: Any, field: Any) -> None:
    """Ensure username is unique and correctly formatted."""
    username = (field.data or "").strip()
    if not username:
        raise ValidationError("Username is required.")

    if len(username) < 3 or len(username) > 50:
        raise ValidationError("Username must be between 3 and 50 characters.")

    if not re.fullmatch(r"[a-zA-Z0-9_]+", username):
        raise ValidationError(
            "Username may only contain letters, numbers, and underscores."
        )

    db = SessionLocal()
    try:
        query = db.query(User).filter(User.username == username)
        model = getattr(form, "_obj", None)
        if model is not None and getattr(model, "id", None):
            query = query.filter(User.id != model.id)
        if query.first():
            raise ValidationError(
                f"The username '{username}' is already taken. Please choose another."
            )
    finally:
        db.close()


def validate_unique_email(form: Any, field: Any) -> None:
    """Ensure email is unique and correctly formatted."""
    email = (field.data or "").strip()
    if not email:
        raise ValidationError("Email address is required.")

    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValidationError(
            "Please enter a valid email address (for example, user@example.com)."
        )

    db = SessionLocal()
    try:
        query = db.query(User).filter(User.email == email)
        model = getattr(form, "_obj", None)
        if model is not None and getattr(model, "id", None):
            query = query.filter(User.id != model.id)
        if query.first():
            raise ValidationError(
                f"The email '{email}' is already registered. Please use another."
            )
    finally:
        db.close()


def validate_password_field(form: Any, field: Any) -> None:
    """Validate password on create and optional password change on edit."""
    password = field.data or ""
    model = getattr(form, "_obj", None)
    is_edit = model is not None and getattr(model, "id", None)

    if not password:
        if is_edit:
            return
        raise ValidationError("Password is required when creating a new user.")

    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    if password.isdigit():
        raise ValidationError("Password cannot contain only numbers.")
