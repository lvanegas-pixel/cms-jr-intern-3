from django.contrib import admin

# Register your models here.

from catalogue.models import Project, Asset


admin.site.register(Project)
admin.site.register(Asset)