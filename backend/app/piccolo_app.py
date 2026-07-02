from piccolo.conf.apps import AppConfig, table_finder

APP_CONFIG = AppConfig(
    app_name="app",
    migrations_folder_path="migrations",
    table_classes=table_finder(modules=["app.models"], exclude_imported=True),
)
