from rest_framework.permissions import BasePermission

from .models import Project


class IsProjectOwnerOrAdmin(BasePermission):
    """Rule 2: admins reach every project, commercials only their own."""

    message = "You do not have permission to access this project."

    def has_object_permission(self, request, view, obj) -> bool:
        project = obj if isinstance(obj, Project) else obj.project
        return request.user.is_admin or project.owner_id == request.user.pk


class CanManageProjectAssets(BasePermission):
    """Rule 3: nobody can manage assets outside their own projects."""

    message = "You cannot manage assets of a project that is not yours."

    def has_permission(self, request, view) -> bool:
        project_pk = view.kwargs.get("project_pk")
        if project_pk is None:
            return True

        try:
            project = Project.objects.get(pk=project_pk)
        except (Project.DoesNotExist, TypeError, ValueError):
            return True

        return request.user.is_admin or project.owner_id == request.user.pk
