from rest_framework import serializers

from .models import Project, Asset


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')

    def validate_name(self, value):

        if not value or not value.strip():
            raise serializers.ValidationError(
                "El nombre del proyecto es obligatorio."
            )

        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre del proyecto debe tener al menos 3 caracteres."
            )

        return value


class AssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Asset
        fields = '__all__'

    def validate_name(self, value):

        if not value or not value.strip():
            raise serializers.ValidationError(
                "El nombre del asset es obligatorio."
            )

        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "El nombre del asset debe tener al menos 3 caracteres."
            )

        return value

    def validate(self, attrs):

        project = attrs.get('project')
        asset_type = attrs.get('asset_type')

        # Si estamos actualizando, recuperamos los valores actuales.
        if self.instance:
            project = project or self.instance.project
            asset_type = asset_type or self.instance.asset_type

        # Solo puede existir un MODEL_3D por proyecto.
        if asset_type == 'MODEL_3D':

            existing_model = Asset.objects.filter(
                project=project,
                asset_type='MODEL_3D'
            )

            # Excluimos el propio objeto cuando se actualiza.
            if self.instance:
                existing_model = existing_model.exclude(
                    pk=self.instance.pk
                )

            if existing_model.exists():
                raise serializers.ValidationError({
                    'asset_type': (
                        'Este proyecto ya tiene un Asset de tipo MODEL_3D.'
                    )
                })

        return attrs