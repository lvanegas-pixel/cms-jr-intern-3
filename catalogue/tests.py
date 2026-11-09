from django.contrib.auth.models import User, Group

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Project, Asset
from .serializers import AssetSerializer


class CMSTestCase(APITestCase):

    def setUp(self):

        # Crear grupos
        self.admin_group = Group.objects.create(
            name='administradores'
        )

        self.commercial_group = Group.objects.create(
            name='comerciales'
        )

        # Crear administrador
        self.admin = User.objects.create_user(
            username='admin',
            password='123456'
        )

        self.admin.groups.add(self.admin_group)

        # Crear comerciales
        self.commercial1 = User.objects.create_user(
            username='commercial1',
            password='123456'
        )

        self.commercial1.groups.add(self.commercial_group)

        self.commercial2 = User.objects.create_user(
            username='commercial2',
            password='123456'
        )

        self.commercial2.groups.add(self.commercial_group)

        # Crear proyectos
        self.project1 = Project.objects.create(
            name='Proyecto uno',
            owner=self.commercial1
        )

        self.project2 = Project.objects.create(
            name='Proyecto dos',
            owner=self.commercial2
        )

        # Crear Assets
        self.asset1 = Asset.objects.create(
            project=self.project1,
            name='Imagen principal',
            asset_type='IMAGE'
        )

        self.asset2 = Asset.objects.create(
            project=self.project2,
            name='Video principal',
            asset_type='VIDEO'
        )

    # =====================================
    # TEST PROJECTS
    # =====================================

    def test_admin_can_see_all_projects(self):

        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/projects/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_commercial_can_only_see_own_projects(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.get('/api/projects/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]['id'],
            self.project1.id
        )

    def test_commercial_cannot_access_foreign_project(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.get(
            f'/api/projects/{self.project2.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_commercial_creates_project_with_own_owner(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.post(
            '/api/projects/',
            {'name': 'Nuevo proyecto'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        project = Project.objects.get(name='Nuevo proyecto')

        self.assertEqual(project.owner, self.commercial1)

    # =====================================
    # TEST ASSETS
    # =====================================

    def test_admin_can_see_all_assets(self):

        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/assets/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_commercial_can_only_see_own_assets(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.get('/api/assets/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(
            response.data[0]['id'],
            self.asset1.id
        )

    def test_commercial_cannot_create_asset_in_foreign_project(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.post(
            '/api/assets/',
            {
                'project': self.project2.id,
                'name': 'Asset ajeno',
                'asset_type': 'IMAGE',
                'is_public': False
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_commercial_can_create_asset_in_own_project(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.post(
            '/api/assets/',
            {
                'project': self.project1.id,
                'name': 'Nueva imagen',
                'asset_type': 'IMAGE',
                'is_public': False
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_commercial_cannot_create_asset_without_project(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.post(
            '/api/assets/',
            {
                'name': 'Nueva imagen',
                'asset_type': 'IMAGE',
                'is_public': False
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_commercial_cannot_update_foreign_asset(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.patch(
            f'/api/assets/{self.asset2.id}/',
            {'name': 'Nombre modificado'},
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

    def test_commercial_cannot_delete_foreign_asset(self):

        self.client.force_authenticate(user=self.commercial1)

        response = self.client.delete(
            f'/api/assets/{self.asset2.id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )

        self.assertTrue(
            Asset.objects.filter(pk=self.asset2.pk).exists()
        )

    # =====================================
    # TEST MODEL_3D BUSINESS RULE
    # =====================================

    def test_project_cannot_have_two_model_3d_assets(self):

        Asset.objects.create(
            project=self.project1,
            name='Modelo 3D principal',
            asset_type='MODEL_3D'
        )

        serializer = AssetSerializer(data={
            'project': self.project1.id,
            'name': 'Segundo modelo',
            'asset_type': 'MODEL_3D',
            'is_public': False
        })

        self.assertFalse(serializer.is_valid())

        self.assertIn('asset_type', serializer.errors)

    def test_project_can_have_multiple_images(self):

        Asset.objects.create(
            project=self.project1,
            name='Primera imagen',
            asset_type='IMAGE'
        )

        Asset.objects.create(
            project=self.project1,
            name='Segunda imagen',
            asset_type='IMAGE'
        )

        self.assertEqual(
            Asset.objects.filter(
                project=self.project1,
                asset_type='IMAGE'
            ).count(),
            3
        )

    def test_can_update_existing_model_3d(self):

        asset = Asset.objects.create(
            project=self.project1,
            name='Modelo original',
            asset_type='MODEL_3D'
        )

        serializer = AssetSerializer(
            instance=asset,
            data={
                'project': self.project1.id,
                'name': 'Modelo actualizado',
                'asset_type': 'MODEL_3D',
                'is_public': False
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)

    # =====================================
    # TEST AUTHENTICATION
    # =====================================

    def test_unauthenticated_user_cannot_access_projects(self):

        self.client.force_authenticate(user=None)

        response = self.client.get('/api/projects/')

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_unauthenticated_user_cannot_access_assets(self):

        self.client.force_authenticate(user=None)

        response = self.client.get('/api/assets/')

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_cannot_add_second_model_3d_via_api(self):
        """
        Verifica a través del endpoint HTTP de la API que no se pueda
        crear un segundo Asset de tipo MODEL_3D en el mismo proyecto.
        """
        self.client.force_authenticate(user=self.commercial1)

        # 1. Crear el primer MODEL_3D exitosamente
        response_first = self.client.post(
            '/api/assets/',
            {
                'project': self.project1.id,
                'name': 'Primer Modelo 3D',
                'asset_type': 'MODEL_3D',
                'is_public': False
            },
            format='json'
        )
        self.assertEqual(response_first.status_code, status.HTTP_201_CREATED)

        # 2. Intentar crear un segundo MODEL_3D en el mismo proyecto (debe fallar)
        response_second = self.client.post(
            '/api/assets/',
            {
                'project': self.project1.id,
                'name': 'Segundo Modelo 3D',
                'asset_type': 'MODEL_3D',
                'is_public': False
            },
            format='json'
        )

        self.assertEqual(response_second.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('asset_type', response_second.data)

    def test_cannot_add_second_model_3d_via_nested_endpoint(self):
        """
        Verifica que  /api/projects/{id}/assets/ rechace el segundo MODEL_3D.
        """
        self.client.force_authenticate(user=self.commercial1)

        # Crear el primer MODEL_3D
        Asset.objects.create(
            project=self.project1,
            name='Modelo 3D Existente',
            asset_type='MODEL_3D'
        )

        # Intentar añadir un segundo MODEL_3D a través de la ruta anidada
        response = self.client.post(
            f'/api/projects/{self.project1.id}/assets/',
            {
                'name': 'Segundo Modelo 3D Anidado',
                'asset_type': 'MODEL_3D',
                'is_public': False
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('asset_type', response.data)

