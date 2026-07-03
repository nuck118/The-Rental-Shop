from pathlib import Path

from markupsafe import Markup
from sqladmin import Admin, ModelView, BaseView, expose
from sqladmin.filters import AllUniqueStringValuesFilter, BooleanFilter
from wtforms import PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, Length, Optional

from app.admin_auth import AdminAuthenticationBackend
from app.admin_helpers import (
    HARDWARE_STATUSES,
    action_badge,
    apply_password_from_form,
    boolean_badge,
    format_change_history,
    model_snapshot,
    safe_snapshot,
    status_badge,
    validate_password_field,
    validate_unique_email,
    validate_unique_username,
    write_audit_log,
)
from app.core.database import engine, SessionLocal
from sqlalchemy import func
from app.models.audit_log import AuditLog
from app.models.hardware import HardwareAsset, DataQuarantine
from app.models.user import User

TEMPLATES_DIR = str(Path(__file__).parent / "templates")

USER_AUDIT_FIELDS = [
    "username",
    "email",
    "full_name",
    "is_active",
    "is_admin",
]

HARDWARE_AUDIT_FIELDS = [
    "name",
    "brand",
    "purchase_date",
    "status",
    "assigned_to",
    "notes",
]


class UserAdmin(ModelView, model=User):
    """Admin view for user account management."""

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    _bulk_actions = True

    column_list = [
        User.id,
        User.username,
        User.email,
        User.full_name,
        User.is_active,
        User.is_admin,
        User.created_at,
    ]
    column_details_list = [
        User.id,
        User.username,
        User.email,
        User.full_name,
        User.is_active,
        User.is_admin,
        User.created_at,
        User.updated_at,
    ]
    column_searchable_list = [User.username, User.email, User.full_name]
    column_sortable_list = [User.id, User.username, User.email, User.created_at]
    column_default_sort = [(User.created_at, True)]
    column_labels = {
        User.username: "Username",
        User.email: "Email",
        User.full_name: "Full Name",
        User.is_active: "Status",
        User.is_admin: "Role",
        User.created_at: "Created",
        User.updated_at: "Last Updated",
    }
    column_formatters = {
        User.is_active: lambda model, _: boolean_badge(model.is_active, "Active", "Inactive"),
        User.is_admin: lambda model, _: boolean_badge(model.is_admin, "Admin", "User"),
    }
    column_filters = [
        BooleanFilter(User.is_active, title="Status"),
        BooleanFilter(User.is_admin, title="Role"),
    ]

    form_columns = [
        User.username,
        User.email,
        User.full_name,
        User.is_active,
        User.is_admin,
    ]
    can_edit = True
    can_delete = True
    can_view_details = True
    column_actions = []
    form_args = {
        "username": {
            "label": "Username",
            "description": "3–50 characters. Letters, numbers, and underscores only.",
            "validators": [validate_unique_username],
        },
        "email": {
            "label": "Email Address",
            "description": "Must be a valid, unique email address.",
            "validators": [validate_unique_email],
        },
        "full_name": {
            "label": "Full Name",
            "validators": [
                Optional(),
                Length(max=255, message="Full name cannot exceed 255 characters."),
            ],
        },
        "is_active": {
            "label": "Active Account",
            "description": "Inactive users cannot sign in.",
        },
        "is_admin": {
            "label": "Administrator",
            "description": "Administrators can access this admin panel.",
        },
    }
    form_widget_args = {
        "username": {"placeholder": "e.g. jane_doe"},
        "email": {"placeholder": "e.g. jane@example.com"},
        "full_name": {"placeholder": "e.g. Jane Doe"},
    }

    page_size = 25
    page_size_options = [10, 25, 50, 100]
    create_template = "sqladmin/user_create.html"
    edit_template = "sqladmin/user_edit.html"

    async def scaffold_form(self, rules=None):
        form_class = await super().scaffold_form(rules)
        form_class.password = PasswordField(
            "Password",
            validators=[validate_password_field],
            render_kw={
                "placeholder": "Minimum 8 characters",
                "autocomplete": "new-password",
            },
        )
        return form_class

    async def on_model_change(self, data, model, is_created, request):
        if not is_created and model is not None:
            request.state.audit_old_values = model_snapshot(model, USER_AUDIT_FIELDS)
        apply_password_from_form(data, is_created)

    async def after_model_change(self, data, model, is_created, request):
        old_values = getattr(request.state, "audit_old_values", None)
        new_values = safe_snapshot(data)
        action = "CREATE" if is_created else "UPDATE"
        username = getattr(model, "username", data.get("username", "unknown"))
        write_audit_log(
            request,
            action=action,
            table_name="user",
            record_id=model.id,
            old_values=old_values,
            new_values=new_values,
            description=f"User '{username}' was {action.lower()}d",
        )

    async def on_model_delete(self, model, request):
        request.state.audit_old_values = model_snapshot(model, USER_AUDIT_FIELDS)
        request.state.audit_record_id = model.id
        request.state.audit_description = f"User '{model.username}' was deleted"

    async def after_model_delete(self, model, request):
        write_audit_log(
            request,
            action="DELETE",
            table_name="user",
            record_id=getattr(request.state, "audit_record_id", model.id),
            old_values=getattr(request.state, "audit_old_values", None),
            new_values=None,
            description=getattr(
                request.state,
                "audit_description",
                f"User '{model.username}' was deleted",
            ),
        )


class HardwareAssetAdmin(ModelView, model=HardwareAsset):
    """Admin view for hardware inventory management."""

    name = "Hardware Asset"
    name_plural = "Hardware Assets"
    icon = "fa-solid fa-laptop"
    _bulk_actions = True

    column_list = [
        HardwareAsset.id,
        HardwareAsset.name,
        HardwareAsset.brand,
        HardwareAsset.status,
        HardwareAsset.assigned_to,
        HardwareAsset.repair_flagged,
    ]
    column_details_list = [
        HardwareAsset.id,
        HardwareAsset.name,
        HardwareAsset.brand,
        HardwareAsset.purchase_date,
        HardwareAsset.status,
        HardwareAsset.assigned_to,
        HardwareAsset.notes,
        HardwareAsset.repair_flagged,
    ]
    column_searchable_list = [
        HardwareAsset.name,
        HardwareAsset.brand,
        HardwareAsset.assigned_to,
    ]
    column_sortable_list = [
        HardwareAsset.id,
        HardwareAsset.name,
        HardwareAsset.brand,
        HardwareAsset.status,
        HardwareAsset.repair_flagged,
    ]
    column_default_sort = [(HardwareAsset.name, False)]
    column_labels = {
        HardwareAsset.name: "Device Name",
        HardwareAsset.brand: "Brand",
        HardwareAsset.purchase_date: "Purchase Date",
        HardwareAsset.status: "Status",
        HardwareAsset.assigned_to: "Assigned To",
        HardwareAsset.notes: "Notes",
        HardwareAsset.repair_flagged: "Repair Flag",
    }
    column_formatters = {
        HardwareAsset.status: lambda model, _: status_badge(model.status),
        HardwareAsset.repair_flagged: lambda model, _: Markup(
            f"<span class='border border-danger text-danger rounded-0 px-2 py-1 text-uppercase'"
            f" style='font-size:0.7rem;font-weight:700;letter-spacing:0.05em;'>⚠ Flagged</span>"
        ) if model.repair_flagged else Markup("<span class='text-secondary' style='font-size:0.85rem;'>—</span>"),
    }
    column_formatters_detail = {
        HardwareAsset.status: lambda model, _: status_badge(model.status),
    }
    column_filters = [
        AllUniqueStringValuesFilter(HardwareAsset.status, title="Status"),
        AllUniqueStringValuesFilter(HardwareAsset.brand, title="Brand"),
        BooleanFilter(HardwareAsset.repair_flagged, title="Repair Flagged"),
    ]

    form_columns = [
        HardwareAsset.name,
        HardwareAsset.brand,
        HardwareAsset.purchase_date,
        HardwareAsset.status,
        HardwareAsset.assigned_to,
        HardwareAsset.notes,
    ]
    form_overrides = {
        "status": SelectField,
        "name": StringField,
        "brand": StringField,
        "assigned_to": StringField,
    }
    form_args = {
        "name": {
            "label": "Device Name",
            "validators": [
                DataRequired(message="Device name is required."),
                Length(max=255, message="Device name cannot exceed 255 characters."),
            ],
        },
        "brand": {
            "label": "Brand",
            "validators": [
                DataRequired(message="Brand is required."),
                Length(max=100, message="Brand cannot exceed 100 characters."),
            ],
        },
        "status": {
            "label": "Status",
            "choices": HARDWARE_STATUSES,
            "validators": [DataRequired(message="Please select a status.")],
        },
        "assigned_to": {
            "label": "Assigned To",
            "validators": [
                Optional(),
                Length(max=255, message="Assigned to cannot exceed 255 characters."),
            ],
        },
        "notes": {
            "label": "Notes",
            "validators": [Optional()],
        },
    }
    form_widget_args = {
        "name": {"placeholder": "e.g. MacBook Pro 14"},
        "brand": {"placeholder": "e.g. Apple"},
        "assigned_to": {"placeholder": "e.g. Jane Doe"},
        "notes": {"placeholder": "Optional maintenance or assignment notes"},
    }

    page_size = 25
    page_size_options = [10, 25, 50, 100]

    async def on_model_change(self, data, model, is_created, request):
        if not is_created and model is not None:
            request.state.audit_old_values = model_snapshot(model, HARDWARE_AUDIT_FIELDS)

    async def after_model_change(self, data, model, is_created, request):
        old_values = getattr(request.state, "audit_old_values", None)
        new_values = safe_snapshot(data)
        action = "CREATE" if is_created else "UPDATE"
        asset_name = getattr(model, "name", data.get("name", "unknown"))
        write_audit_log(
            request,
            action=action,
            table_name="hardware_asset",
            record_id=model.id,
            old_values=old_values,
            new_values=new_values,
            description=f"Hardware asset '{asset_name}' was {action.lower()}d",
        )

    async def on_model_delete(self, model, request):
        request.state.audit_old_values = model_snapshot(model, HARDWARE_AUDIT_FIELDS)
        request.state.audit_record_id = model.id
        request.state.audit_description = f"Hardware asset '{model.name}' was deleted"

    async def after_model_delete(self, model, request):
        write_audit_log(
            request,
            action="DELETE",
            table_name="hardware_asset",
            record_id=getattr(request.state, "audit_record_id", model.id),
            old_values=getattr(request.state, "audit_old_values", None),
            new_values=None,
            description=getattr(
                request.state,
                "audit_description",
                f"Hardware asset '{model.name}' was deleted",
            ),
        )


class AuditLogAdmin(ModelView, model=AuditLog):
    """Read-only audit history for all admin changes."""

    name = "Audit Log"
    name_plural = "Audit Logs"
    icon = "fa-solid fa-history"

    column_list = [
        AuditLog.id,
        AuditLog.user_id,
        AuditLog.action,
        AuditLog.table_name,
        AuditLog.record_id,
        AuditLog.description,
        AuditLog.created_at,
    ]
    column_details_list = [
        AuditLog.id,
        AuditLog.user_id,
        AuditLog.action,
        AuditLog.table_name,
        AuditLog.record_id,
        AuditLog.description,
        AuditLog.old_values,
        AuditLog.ip_address,
        AuditLog.user_agent,
        AuditLog.created_at,
    ]
    column_searchable_list = [
        AuditLog.action,
        AuditLog.table_name,
        AuditLog.description,
    ]
    column_sortable_list = [
        AuditLog.id,
        AuditLog.user_id,
        AuditLog.action,
        AuditLog.created_at,
    ]
    column_default_sort = [(AuditLog.created_at, True)]
    column_labels = {
        AuditLog.user_id: "Changed By",
        AuditLog.action: "Action",
        AuditLog.table_name: "Table",
        AuditLog.record_id: "Record ID",
        AuditLog.old_values: "Change History",
        AuditLog.description: "Summary",
        AuditLog.ip_address: "IP Address",
        AuditLog.user_agent: "Browser",
        AuditLog.created_at: "Timestamp",
    }
    column_formatters = {
        AuditLog.user_id: lambda model, _: _resolve_username(model.user_id),
        AuditLog.action: lambda model, _: action_badge(model.action),
        AuditLog.description: lambda model, _: Markup(
            f"<span class='admin-audit-summary'>{model.description or '—'}</span>"
        ),
    }
    column_formatters_detail = {
        AuditLog.action: lambda model, _: action_badge(model.action),
        AuditLog.old_values: lambda model, _: format_change_history(
            model.old_values, model.new_values
        ),
    }

    can_create = False
    can_edit = False
    can_delete = False
    can_export = True
    can_view_details = True

    page_size = 25
    page_size_options = [10, 25, 50, 100]

    details_template = "sqladmin/audit_details.html"


class DataQuarantineAdmin(ModelView, model=DataQuarantine):
    """Admin view for quarantined data that failed validation."""

    name = "Data Quarantine"
    name_plural = "Data Quarantine"
    icon = "fa-solid fa-triangle-exclamation"
    _bulk_actions = True

    column_list = [
        DataQuarantine.id,
        DataQuarantine.severity,
        DataQuarantine.source,
        DataQuarantine.resolved,
        DataQuarantine.created_at,
    ]
    column_details_list = [
        DataQuarantine.id,
        DataQuarantine.raw_data,
        DataQuarantine.errors,
        DataQuarantine.severity,
        DataQuarantine.source,
        DataQuarantine.resolved,
        DataQuarantine.created_at,
    ]
    column_searchable_list = [
        DataQuarantine.source,
        DataQuarantine.errors,
    ]
    column_sortable_list = [
        DataQuarantine.id,
        DataQuarantine.severity,
        DataQuarantine.source,
        DataQuarantine.resolved,
        DataQuarantine.created_at,
    ]
    column_default_sort = [(DataQuarantine.created_at, True)]
    column_labels = {
        DataQuarantine.raw_data: "Raw Data",
        DataQuarantine.errors: "Validation Errors",
        DataQuarantine.severity: "Severity",
        DataQuarantine.source: "Source",
        DataQuarantine.resolved: "Resolved",
        DataQuarantine.created_at: "Created At",
    }
    column_formatters = {
        DataQuarantine.severity: lambda model, _: Markup(
            f"<span class='border border-{'danger' if model.severity == 'critical' else 'warning'} text-{'danger' if model.severity == 'critical' else 'warning'} rounded-0 px-2 py-1 text-uppercase'"
            f" style='font-size:0.7rem;font-weight:700;letter-spacing:0.05em;'>{model.severity.upper()}</span>"
        ),
        DataQuarantine.resolved: lambda model, _: boolean_badge(model.resolved, "Resolved", "Pending"),
    }
    column_filters = [
        AllUniqueStringValuesFilter(DataQuarantine.severity, title="Severity"),
        AllUniqueStringValuesFilter(DataQuarantine.source, title="Source"),
        BooleanFilter(DataQuarantine.resolved, title="Resolved"),
    ]

    can_create = False
    can_edit = True
    can_delete = True
    can_export = True
    can_view_details = True
    column_actions = []

    page_size = 25
    page_size_options = [10, 25, 50, 100]


def _resolve_username(user_id: int) -> str:
    """Resolve a user ID to a username for display in audit logs."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.username if user else f"User #{user_id}"
    finally:
        db.close()


def get_dashboard_metrics():
    db = SessionLocal()
    try:
        users_count = db.query(func.count(User.id)).scalar() or 0
        hardware_count = db.query(func.count(HardwareAsset.id)).scalar() or 0
        available_hardware_count = db.query(func.count(HardwareAsset.id)).filter(HardwareAsset.status == 'Available').scalar() or 0
        repair_hardware_count = db.query(func.count(HardwareAsset.id)).filter(HardwareAsset.status == 'Repair').scalar() or 0
        return {
            "users_count": users_count,
            "hardware_count": hardware_count,
            "available_hardware_count": available_hardware_count,
            "repair_hardware_count": repair_hardware_count,
        }
    finally:
        db.close()

def setup_admin(app):
    """Setup SQLAdmin with all model views and authentication."""
    from app.core.config import settings

    admin = Admin(
        app=app,
        engine=engine,
        title="The Rental Shop Admin",
        templates_dir=TEMPLATES_DIR,
        authentication_backend=AdminAuthenticationBackend(secret_key=settings.secret_key),
        debug=True,
    )
    
    admin.templates.env.globals["get_dashboard_metrics"] = get_dashboard_metrics

    admin.add_view(UserAdmin)
    admin.add_view(HardwareAssetAdmin)
    admin.add_view(AuditLogAdmin)

    admin.add_view(DataQuarantineAdmin)

    return admin
