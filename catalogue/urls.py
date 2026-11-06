from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import AssetViewSet, ProjectViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")

project_assets = AssetViewSet.as_view({"get": "list", "post": "create"})
project_asset_detail = AssetViewSet.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path(
        "projects/<int:project_pk>/assets/",
        project_assets,
        name="project-assets",
    ),
    path(
        "projects/<int:project_pk>/assets/<int:pk>/",
        project_asset_detail,
        name="project-asset-detail",
    ),
] + router.urls
