import hashlib
import secrets
from sqlalchemy.orm import Session
from app.models.user import User


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with a salt.

    Args:
        password: Plain text password

    Returns:
        Hashed password with salt
    """
    salt = secrets.token_hex(32)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: Plain text password to verify
        password_hash: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        salt, hash_value = password_hash.split("$")
        password_check = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_check == hash_value
    except (ValueError, AttributeError):
        return False


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    full_name: str = None,
    is_admin: bool = False,
) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        username: Unique username
        email: Unique email address
        password: Plain text password
        full_name: Optional full name
        is_admin: Whether user is an admin

    Returns:
        Created User object

    Raises:
        ValueError: If username or email already exists
    """
    # Check if username exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise ValueError(f"Username '{username}' already exists")

    # Check if email exists
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise ValueError(f"Email '{email}' already exists")

    # Create new user
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_admin=is_admin,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_username(db: Session, username: str) -> User:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def update_user(
    db: Session,
    user_id: int,
    **kwargs,
) -> User:
    """
    Update user fields.

    Args:
        db: Database session
        user_id: ID of user to update
        **kwargs: Fields to update

    Returns:
        Updated User object

    Raises:
        ValueError: If user not found
    """
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")

    # Update allowed fields
    allowed_fields = {"email", "full_name", "is_active", "is_admin"}
    for key, value in kwargs.items():
        if key in allowed_fields:
            setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> User:
    """Deactivate a user."""
    return update_user(db, user_id, is_active=False)


def activate_user(db: Session, user_id: int) -> User:
    """Activate a user."""
    return update_user(db, user_id, is_active=True)


def promote_to_admin(db: Session, user_id: int) -> User:
    """Promote a user to admin."""
    return update_user(db, user_id, is_admin=True)


def demote_from_admin(db: Session, user_id: int) -> User:
    """Demote a user from admin."""
    return update_user(db, user_id, is_admin=False)


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_admin: bool = None,
    is_active: bool = None,
) -> tuple[list[User], int]:
    """
    List users with optional filtering.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum records to return
        is_admin: Filter by admin status
        is_active: Filter by active status

    Returns:
        Tuple of (users, total count)
    """
    query = db.query(User)

    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total
