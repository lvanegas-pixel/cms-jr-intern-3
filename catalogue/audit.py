"""Helpers to expose the current request to audit signals."""

from contextvars import ContextVar, Token
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any
from uuid import UUID

from django.db.models import Model

_current_request: ContextVar[Any] = ContextVar(
    "catalogue_current_request", default=None
)


def set_current_request(request: Any) -> Token:
    """Store the active request for the current execution context."""
    return _current_request.set(request)


def reset_current_request(token: Token) -> None:
    """Restore the previous context once the request is finished."""
    _current_request.reset(token)


def get_current_request() -> Any:
    """Return the request being handled, if any."""
    return _current_request.get()


def json_safe(value: Any) -> Any:
    """Convert model field values into JSON serialisable values."""
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def snapshot(instance: Model) -> dict[str, Any]:
    """Return a JSON-friendly snapshot of all concrete model fields."""
    return {
        field.name: json_safe(field.value_from_object(instance))
        for field in instance._meta.fields
    }
