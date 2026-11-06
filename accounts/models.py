from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a CMS role.

    The role drives what a user can see and modify inside the catalogue.
    Superusers are always treated as admins, regardless of their role.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        COMMERCIAL = "commercial", "Commercial"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.COMMERCIAL,
    )

    @property
    def is_admin(self) -> bool:
        """Return True when the user can act on every project."""
        return self.is_staff or self.role == self.Role.ADMIN
