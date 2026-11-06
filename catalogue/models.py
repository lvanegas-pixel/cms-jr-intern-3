from django.conf import settings
from django.db import models


class Project(models.Model):
    """A project of the content catalogue."""

    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class Asset(models.Model):
    """A content element that belongs to a project."""

    class AssetType(models.TextChoices):
        MODEL_3D = "MODEL_3D", "3D model"
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    is_public = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        return self.name


class AuditLog(models.Model):
    """Immutable trace of create, update and delete actions.

    The audited object is referenced by type and id instead of a foreign key
    so the trace survives when the object is deleted.
    """

    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    username = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=10, choices=Action.choices)
    object_type = models.CharField(max_length=50)
    object_id = models.PositiveBigIntegerField()
    object_repr = models.CharField(max_length=255, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["object_type", "object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.object_type}#{self.object_id}"
