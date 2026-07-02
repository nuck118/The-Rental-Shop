import json
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_audit(
    db: Session,
    user_id: int,
    action: str,
    table_name: str,
    record_id: int,
    old_values: Optional[Dict[str, Any]] = None,
    new_values: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """
    Log an audit entry for a user action.

    Args:
        db: Database session
        user_id: ID of the user performing the action
        action: Type of action (CREATE, UPDATE, DELETE)
        table_name: Name of the table affected
        record_id: ID of the affected record
        old_values: Dictionary of old values (for UPDATE/DELETE)
        new_values: Dictionary of new values (for CREATE/UPDATE)
        description: Human-readable description of the action
        ip_address: IP address of the user
        user_agent: User agent string

    Returns:
        Created AuditLog entry
    """
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_values=json.dumps(old_values) if old_values else None,
        new_values=json.dumps(new_values) if new_values else None,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow(),
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def get_user_audit_history(
    db: Session,
    user_id: int,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    """
    Get audit history for a specific user.

    Args:
        db: Database session
        user_id: ID of the user
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        Tuple of (audit logs, total count)
    """
    query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs, total


def get_table_audit_history(
    db: Session,
    table_name: str,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    """
    Get audit history for a specific table.

    Args:
        db: Database session
        table_name: Name of the table
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        Tuple of (audit logs, total count)
    """
    query = db.query(AuditLog).filter(AuditLog.table_name == table_name)
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs, total


def get_record_audit_history(
    db: Session,
    table_name: str,
    record_id: int,
    limit: int = 100,
    offset: int = 0,
) -> tuple[list[AuditLog], int]:
    """
    Get audit history for a specific record.

    Args:
        db: Database session
        table_name: Name of the table
        record_id: ID of the record
        limit: Maximum number of records to return
        offset: Number of records to skip

    Returns:
        Tuple of (audit logs, total count)
    """
    query = db.query(AuditLog).filter(
        (AuditLog.table_name == table_name) & (AuditLog.record_id == record_id)
    )
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs, total
