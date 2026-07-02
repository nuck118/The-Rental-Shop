import os
from piccolo.engine.sqlite import SQLiteEngine
from piccolo.conf.apps import AppRegistry

DB = SQLiteEngine(path=os.getenv("DATABASE_URL", "rental_shop.db"))

APP_REGISTRY = AppRegistry(
    apps=[
        "app.piccolo_app",
        "piccolo_admin.piccolo_app",
        "piccolo_api.session_auth.piccolo_app",
    ]
)
