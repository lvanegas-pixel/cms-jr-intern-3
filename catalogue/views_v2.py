
from .filters import AssetFilter, ProjectFilter
from .serializers_v2 import AssetSerializerV2, ProjectSerializerV2
from .views import AssetViewSet, ProjectViewSet


class ProjectViewSetV2(ProjectViewSet):
    """V2 project ViewSet.

    Same business rules and scoping as v1, different serializer shape
    (carries an ``api_version`` field) to demonstrate a real version
    boundary.
    """

    serializer_class = ProjectSerializerV2
    filterset_class = ProjectFilter


class AssetViewSetV2(AssetViewSet):
    """V2 asset ViewSet.

    Same business rules and scoping as v1, different serializer shape
    (carries an ``api_version`` field).
    """

    serializer_class = AssetSerializerV2
    filterset_class = AssetFilter
