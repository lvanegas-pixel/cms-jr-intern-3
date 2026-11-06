"""Signal handlers that keep the audit trail in sync with the models."""

from typing import Any

from django.db.models.signals import post_save, pre_delete, pre_save

from .audit import get_current_request, snapshot
from .models import Asset, AuditLog, Project


def _acting_user() -> Any:
    request = get_current_request()
    user = getattr(request, "user", None) if request is not None else None
    if user is not None and getattr(user, "is_authenticated", False):
        return user
    return None


def _record(instance: Any, action: str, changes: dict) -> None:
    user = _acting_user()
    AuditLog.objects.create(
        user=user,
        username=getattr(user, "username", "") if user else "",
        action=action,
        object_type=instance.__class__.__name__,
        object_id=instance.pk,
        object_repr=str(instance)[:255],
        changes=changes,
    )


def _handle_pre_save(sender, instance: Any, **kwargs: Any) -> None:
    if instance.pk is None:
        return
    previous = sender.objects.filter(pk=instance.pk).first()
    if previous is not None:
        instance._audit_previous = snapshot(previous)


def _handle_post_save(sender, instance: Any, created: bool, **kwargs: Any) -> None:
    if created:
        _record(instance, AuditLog.Action.CREATE, {"after": snapshot(instance)})
        return

    previous = getattr(instance, "_audit_previous", None)
    if previous is None:
        return

    current = snapshot(instance)
    changes = {
        field: {"from": previous.get(field), "to": current.get(field)}
        for field in current
        if previous.get(field) != current.get(field)
    }
    if changes:
        _record(instance, AuditLog.Action.UPDATE, changes)


def _handle_pre_delete(sender, instance: Any, **kwargs: Any) -> None:
    _record(instance, AuditLog.Action.DELETE, {"before": snapshot(instance)})


def connect_audit_signals() -> None:
    """Attach the audit handlers to every audited model exactly once."""
    for model in (Project, Asset):
        name = model.__name__
        pre_save.connect(
            _handle_pre_save,
            sender=model,
            dispatch_uid=f"audit_pre_save_{name}",
        )
        post_save.connect(
            _handle_post_save,
            sender=model,
            dispatch_uid=f"audit_post_save_{name}",
        )
        pre_delete.connect(
            _handle_pre_delete,
            sender=model,
            dispatch_uid=f"audit_pre_delete_{name}",
        )
