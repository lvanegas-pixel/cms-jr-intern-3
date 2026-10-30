# Create your models here.
from django.db import models

from django.core.validators import MinLengthValidator
from django.contrib.auth.models import AbstractUser

from django.conf import settings

class Project(models.Model):

    name = models.TextField(
        null=False,
        blank=False,
        validators=[MinLengthValidator(3)]
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name




class Asset(models.Model):

    ASSET_TYPE_CHOICES = [
        ('MODEL_3D', 'Modelo 3D'),
        ('IMAGE', 'Imagen'),
        ('VIDEO', 'Vídeo'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='assets'
    )

    name = models.TextField(
        null=False,
        blank=False,
        validators=[MinLengthValidator(3)]
    )

    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPE_CHOICES
    )

    is_public = models.BooleanField(default=False)

    def __str__(self):
        return self.name
