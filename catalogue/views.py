from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from .filters import AssetFilter, ProjectFilter
from .models import Project
from .permissions import CanManageProjectAssets, IsProjectOwnerOrAdmin
from .serializers import AssetSerializer, ProjectSerializer


class ProjectViewSet(ModelViewSet):
    """Thin CRUD for projects, scoped by the user role."""

    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwnerOrAdmin]
    filterset_class = ProjectFilter
    search_fields = ["name", "owner__username"]

    def get_queryset(self):
        queryset = Project.objects.select_related("owner")
        if self.request.user.is_admin:
            return queryset
        return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer: ProjectSerializer) -> None:
        serializer.save(owner=self.request.user)


class AssetViewSet(ModelViewSet):
    """Nested CRUD for the assets of a project.

    The project is always taken from the URL. Business rules stay in the
    serializer and the permission classes.
    """

    serializer_class = AssetSerializer
    permission_classes = [
        IsAuthenticated,
        CanManageProjectAssets,
        IsProjectOwnerOrAdmin,
    ]
    filterset_class = AssetFilter
    search_fields = ["name"]

    def get_project(self) -> Project:
        """Return the URL project, scoped to the user role."""
        if not hasattr(self, "_project"):
            queryset = Project.objects.all()
            if not self.request.user.is_admin:
                queryset = queryset.filter(owner=self.request.user)
            self._project = get_object_or_404(queryset, pk=self.kwargs["project_pk"])
        return self._project

    def get_queryset(self):
        return self.get_project().assets.all()

    def get_serializer_context(self) -> dict:
        context = super().get_serializer_context()
        context["project"] = self.get_project()
        return context

    def perform_create(self, serializer: AssetSerializer) -> None:
        serializer.save(project=self.get_project())
