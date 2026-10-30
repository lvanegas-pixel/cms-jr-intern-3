
from django.test import TestCase

# Create your tests here.
import pytest
from django.contrib.auth.models import User, Group

from catalogue.models import Project, Asset
from catalogue.serializers import AssetSerializer


@pytest.mark.django_db
def test_project_only_one_model_3d():

    # Crear usuario
    user = User.objects.create_user(
        username='test_comercial',
        password='tpaiu_invelon'
    )

    # Crear proyecto
    project = Project.objects.create(
        name='proyecto_1_comercial',
        owner=user
    )

    # Crear primer Asset MODEL_3D
    asset = Asset.objects.create(
        project=project,
        name='modelo_3d_1',
        asset_type='MODEL_3D',
        is_public= True
    )

    assert asset.asset_type == 'MODEL_3D'

    # Intentar crear un segundo MODEL_3D
    serializer = AssetSerializer(data={
        'project': project.pk,
        'name': 'modelo_3d_2',
        'asset_type': 'MODEL_3D',
        'is_public': True
    })

    # El serializer debe rechazarlo
    assert serializer.is_valid() is False

    # Comprobar que devuelve un error en asset_type
    assert 'asset_type' in serializer.errors

    assert (
        serializer.errors['asset_type'][0]
        == 'Este proyecto ya tiene un modelo 3D.'
    )

