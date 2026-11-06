from django.apps import AppConfig


class CatalogueConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'catalogue'

    def ready(self) -> None:
        from .signals import connect_audit_signals

        connect_audit_signals()
