from rest_framework.permissions import BasePermission

from .models import Project


class PermissionAccess(BasePermission):
    """
    Clase principal.
    Comprueba que el usuario esté autenticado
    y pertenezca a un grupo autorizado.
    """

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        is_admin = user.groups.filter(
            name='administradores'
        ).exists()

        is_commercial = user.groups.filter(
            name='comerciales'
        ).exists()

        return is_admin or is_commercial

    def is_admin(self, user):

        return user.groups.filter(
            name='administradores'
        ).exists()

    def is_commercial(self, user):

        return user.groups.filter(
            name='comerciales'
        ).exists()


class ProjectPermission(PermissionAccess):
    """
    Controla el acceso a los proyectos.

    Administradores: pueden acceder a todos.
    Comerciales: solamente a sus proyectos.
    """

    def has_object_permission(self, request, view, obj):

        if self.is_admin(request.user):
            return True

        if self.is_commercial(request.user):
            return obj.owner == request.user

        return False


class AssetPermission(PermissionAccess):
    """
    Controla el acceso a los Assets.

    Administradores: pueden acceder a todos.
    Comerciales: solamente pueden acceder a Assets
    pertenecientes a sus propios proyectos.
    """

    def has_permission(self, request, view):

        if not super().has_permission(request, view):
            return False

        # Los administradores pueden acceder a todos los Assets.
        if self.is_admin(request.user):
            return True

        # Comprobamos el proyecto enviado al crear o modificar un Asset.
        if request.method in ['POST', 'PUT', 'PATCH']:

            project_id = request.data.get('project')

            if project_id:

                project = Project.objects.filter(
                    pk=project_id
                ).first()

                # Si el proyecto existe, comprobamos su propietario.
                if project and project.owner != request.user:
                    return False

        return True

    def has_object_permission(self, request, view, obj):

        if self.is_admin(request.user):
            return True

        if self.is_commercial(request.user):
            return obj.project.owner == request.user

        return False