from rest_framework.permissions import BasePermission

from rest_framework.permissions import BasePermission
from .models import Project , Asset


# Clase principal
class PermissionAccess(BasePermission):

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        is_admin = user.groups.filter(name='administradores').exists()
        is_commercial = user.groups.filter(name='comerciales').exists()

        return is_admin or is_commercial


class ProjectPermission(PermissionAccess):

    def permission_access_project(self, request):

        user = request.user

        if user.groups.filter(name='administradores').exists():
            return Project.objects.all()

        return Project.objects.filter(owner=user)


class AssetPermission(PermissionAccess):

    def permission_access_asset(self, request):

        user = request.user

        if user.groups.filter(name='administradores').exists():
            return Asset.objects.all()

        return Asset.objects.filter(project__owner=user)