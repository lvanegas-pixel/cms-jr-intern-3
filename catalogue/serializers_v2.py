from rest_framework import serializers

from .serializers import AssetSerializer, ProjectSerializer


class ProjectSerializerV2(ProjectSerializer):
    """V2 project serializer.

    Adds an ``api_version`` read-only field so clients can tell which
    version of the API served the response.
    """

    api_version = serializers.CharField(read_only=True, default="v2")

    class Meta(ProjectSerializer.Meta):
        fields = [
            "id",
            "name",
            "owner",
            "owner_username",
            "created_at",
            "api_version",
        ]


class AssetSerializerV2(AssetSerializer):
    """V2 asset serializer.

    Adds an ``api_version`` read-only field.
    """

    api_version = serializers.CharField(read_only=True, default="v2")

    class Meta(AssetSerializer.Meta):
        fields = ["id", "project", "name", "asset_type", "is_public", "api_version"]
