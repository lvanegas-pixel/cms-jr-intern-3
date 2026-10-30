from rest_framework import serializers
from .models import Project, Asset


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')


class AssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Asset
        fields = '__all__'

    def validate(self, attrs):

        project = attrs.get(
            'project',
            getattr(self.instance, 'project', None)
        )

        asset_type = attrs.get(
            'asset_type',
            getattr(self.instance, 'asset_type', None)
        )

        # Un proyecto solo puede tener un MODEL_3D
        if asset_type == 'MODEL_3D':

            existing_model = Asset.objects.filter(
                project=project,
                asset_type='MODEL_3D'
            )

            # Excluir el propio Asset cuando estamos modificándolo
            if self.instance:
                existing_model = existing_model.exclude(
                    pk=self.instance.pk
                )

            if existing_model.exists():
                raise serializers.ValidationError({
                    'asset_type': 'Este proyecto ya tiene un modelo 3D.'
                })

        return attrs

