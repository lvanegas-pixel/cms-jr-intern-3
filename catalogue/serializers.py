from rest_framework import serializers

from .models import Asset, Project


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for catalogue projects."""

    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "owner", "owner_username", "created_at"]
        read_only_fields = ["owner", "owner_username", "created_at"]
        extra_kwargs = {
            "name": {"min_length": 3},
        }


class AssetSerializer(serializers.ModelSerializer):
    """Serializer for project assets.

    The project always comes from the nested URL, never from the request body.
    Rule 1 lives here: a project can only own one MODEL_3D asset.
    """

    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Asset
        fields = ["id", "project", "name", "asset_type", "is_public"]

    def validate(self, attrs: dict) -> dict:
        project = self.context.get("project", getattr(self.instance, "project", None))
        asset_type = attrs.get("asset_type", getattr(self.instance, "asset_type", None))

        if asset_type != Asset.AssetType.MODEL_3D:
            return attrs

        duplicates = Asset.objects.filter(
            project=project,
            asset_type=Asset.AssetType.MODEL_3D,
        )
        if self.instance is not None:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if duplicates.exists():
            raise serializers.ValidationError(
                {"asset_type": "This project already has a MODEL_3D asset."}
            )

        return attrs
