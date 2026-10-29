from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Catalogue(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='catalogues'
    )
