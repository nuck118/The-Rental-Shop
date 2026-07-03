from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import settings

# Create SQLite Cloud engine
# SQLite Cloud uses its own library, so we need to create a custom connection
if settings.database_url.startswith("sqlitecloud://"):
    # Import sqlitecloud
    import sqlitecloud
    
    # Create a wrapper class to make sqlitecloud compatible with SQLAlchemy
    class SQLiteCloudConnection:
        """Wrapper for sqlitecloud connection to make it compatible with SQLAlchemy."""
        
        def __init__(self, db_url):
            self._conn = sqlitecloud.connect(db_url)
        
        def __getattr__(self, name):
            """Proxy all other attributes to the underlying connection."""
            # Block unsupported methods
            if name == 'create_function':
                def noop(*args, **kwargs):
                    pass
                return noop
            return getattr(self._conn, name)
        
        def close(self):
            """Close the connection."""
            try:
                self._conn.close()
            except Exception:
                pass
        
        def commit(self):
            """Commit the transaction."""
            try:
                self._conn.commit()
            except Exception:
                pass
        
        def rollback(self):
            """Rollback the transaction. Suppress errors since sqlitecloud
            may not support rollback in all states (e.g. after read-only ops)."""
            try:
                self._conn.rollback()
            except Exception:
                pass
    
    # Create a connection creator function for SQLite Cloud
    def create_sqlitecloud_connection():
        """Create a sqlitecloud connection using the configured URL."""
        return SQLiteCloudConnection(settings.database_url)
    
    # Use SQLite dialect with a custom connection creator
    engine = create_engine(
        "sqlite:///:memory:",  # Dummy URL, we'll override the connection
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        creator=create_sqlitecloud_connection,
    )
else:
    # Local SQLite connection (fallback)
    engine = create_engine(
        f"sqlite:///{settings.database_url}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()


def get_db():
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
