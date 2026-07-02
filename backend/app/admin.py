from sqladmin import Admin, ModelView
from sqlalchemy.orm import Session
from datetime import datetime
import json
from app.core.database import engine, SessionLocal
from app.models.hardware import HardwareAsset
from app.models.user import User
from app.models.audit_log import AuditLog
from app.admin_auth import AdminAuthenticationBackend


class UserAdmin(ModelView, model=User):
    """Admin view for User management."""

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    column_list = [User.id, User.username, User.email, User.full_name, User.is_active, User.is_admin, User.created_at]
    column_details_list = [User.id, User.username, User.email, User.full_name, User.is_active, User.is_admin, User.created_at, User.updated_at]
    column_searchable_list = [User.username, User.email, User.full_name]
    column_sortable_list = [User.id, User.username, User.email, User.created_at]
    column_formatters = {
        User.is_active: lambda m, a: "✓ Active" if m.is_active else "✗ Inactive",
        User.is_admin: lambda m, a: "✓ Admin" if m.is_admin else "✗ User",
    }
    form_columns = [User.username, User.email, User.full_name, User.password_hash, User.is_active, User.is_admin]
    form_args = {
        User.username: {"validators": []},
        User.email: {"validators": []},
        User.full_name: {"validators": []},
        User.password_hash: {"validators": []},
    }

    async def on_model_change(self, data, model, is_create, request):
        """Track changes in audit log."""
        try:
            db = SessionLocal()
            user_id = getattr(request.state, "admin_user_id", None)
            
            action = "CREATE" if is_create else "UPDATE"
            table_name = "user"
            record_id = model.id if model else data.get("id")
            
            # Log the change
            if record_id:
                audit_log = AuditLog(
                    user_id=user_id or 1,
                    action=action,
                    table_name=table_name,
                    record_id=record_id,
                    new_values=json.dumps({k: str(v) for k, v in data.items()}) if data else None,
                    description=f"User '{data.get('username', 'unknown')}' was {action.lower()}d",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
                db.add(audit_log)
                db.commit()
        except Exception as e:
            print(f"Error logging user change: {e}")
        finally:
            db.close()


class HardwareAssetAdmin(ModelView, model=HardwareAsset):
    """Admin view for Hardware Asset management."""

    name = "Hardware Asset"
    name_plural = "Hardware Assets"
    icon = "fa-solid fa-laptop"
    column_list = [HardwareAsset.id, HardwareAsset.name, HardwareAsset.brand, HardwareAsset.status, HardwareAsset.assigned_to]
    column_details_list = [HardwareAsset.id, HardwareAsset.name, HardwareAsset.brand, HardwareAsset.purchase_date, HardwareAsset.status, HardwareAsset.assigned_to, HardwareAsset.notes]
    column_searchable_list = [HardwareAsset.name, HardwareAsset.brand, HardwareAsset.assigned_to]
    column_sortable_list = [HardwareAsset.id, HardwareAsset.name, HardwareAsset.brand, HardwareAsset.status]
    column_formatters = {
        HardwareAsset.status: lambda m, a: f"<span style='color: green;'>✓ {m.status}</span>" if m.status == "Available" else f"<span style='color: orange;'>{m.status}</span>",
    }
    form_columns = [HardwareAsset.name, HardwareAsset.brand, HardwareAsset.purchase_date, HardwareAsset.status, HardwareAsset.assigned_to, HardwareAsset.notes]

    async def on_model_change(self, data, model, is_create, request):
        """Track changes in audit log."""
        try:
            db = SessionLocal()
            user_id = getattr(request.state, "admin_user_id", None)
            
            action = "CREATE" if is_create else "UPDATE"
            table_name = "hardware_asset"
            record_id = model.id if model else data.get("id")
            
            # Log the change
            if record_id:
                audit_log = AuditLog(
                    user_id=user_id or 1,
                    action=action,
                    table_name=table_name,
                    record_id=record_id,
                    new_values=json.dumps({k: str(v) for k, v in data.items()}) if data else None,
                    description=f"Hardware asset '{data.get('name', 'unknown')}' was {action.lower()}d",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
                db.add(audit_log)
                db.commit()
        except Exception as e:
            print(f"Error logging hardware change: {e}")
        finally:
            db.close()


class AuditLogAdmin(ModelView, model=AuditLog):
    """Admin view for Audit Log (read-only)."""

    name = "Audit Log"
    name_plural = "Audit Logs"
    icon = "fa-solid fa-history"
    column_list = [AuditLog.id, AuditLog.user_id, AuditLog.action, AuditLog.table_name, AuditLog.record_id, AuditLog.created_at]
    column_details_list = [AuditLog.id, AuditLog.user_id, AuditLog.action, AuditLog.table_name, AuditLog.record_id, AuditLog.old_values, AuditLog.new_values, AuditLog.description, AuditLog.ip_address, AuditLog.user_agent, AuditLog.created_at]
    column_searchable_list = [AuditLog.action, AuditLog.table_name, AuditLog.description]
    column_sortable_list = [AuditLog.id, AuditLog.user_id, AuditLog.action, AuditLog.created_at]
    column_formatters = {
        AuditLog.action: lambda m, a: f"<span style='color: blue;'>{m.action}</span>",
    }
    can_create = False
    can_edit = False
    can_delete = False
    can_export = True


def setup_admin(app):
    """Setup SQLAdmin with all model views and authentication."""
    from app.core.config import settings
    
    admin = Admin(
        app=app,
        engine=engine,
        title="The Rental Shop Admin",
        authentication_backend=AdminAuthenticationBackend(secret_key=settings.secret_key),
    )
    
    admin.add_view(UserAdmin)
    admin.add_view(HardwareAssetAdmin)
    admin.add_view(AuditLogAdmin)
    
    return admin
