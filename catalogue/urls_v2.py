from django.urls import path

from .views_v2 import AssetViewSetV2, ProjectViewSetV2

project_list = ProjectViewSetV2.as_view({"get": "list", "post": "create"})
project_detail = ProjectViewSetV2.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

project_assets = AssetViewSetV2.as_view({"get": "list", "post": "create"})
project_asset_detail = AssetViewSetV2.as_view(
    {
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy",
    }
)

urlpatterns = [
    path("projects/", project_list, name="v2-project-list"),
    path("projects/<int:pk>/", project_detail, name="v2-project-detail"),
    path(
        "projects/<int:project_pk>/assets/",
        project_assets,
        name="v2-project-assets",
    ),
    path(
        "projects/<int:project_pk>/assets/<int:pk>/",
        project_asset_detail,
        name="v2-project-asset-detail",
    ),
]
