from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Project, Asset
from .serializers import ProjectSerializer, AssetSerializer
from .permissions import ProjectPermission, AssetPermission


class ProjectViewSet(viewsets.ModelViewSet):

    serializer_class = ProjectSerializer
    permission_classes = [ProjectPermission]

    def get_queryset(self):

        user = self.request.user

        # Los administradores pueden ver todos los proyectos.
        if user.groups.filter(name='administradores').exists():
            return Project.objects.all()

        # Los comerciales solamente ven sus proyectos.
        return Project.objects.filter(owner=user)

    def perform_create(self, serializer):

        # El propietario será el usuario autenticado.
        serializer.save(owner=self.request.user)

    @action(
        detail=True,
        methods=['get', 'post'],
        url_path='assets'
    )
    def assets(self, request, pk=None):

        project = self.get_object()

        # GET: consultar los Assets del proyecto.
        if request.method == 'GET':

            assets = project.assets.all()

            serializer = AssetSerializer(
                assets,
                many=True
            )

            return Response(serializer.data)

        # POST: crear un Asset dentro del proyecto.
        if request.method == 'POST':

            data = request.data.copy()

            # El proyecto se obtiene de la URL,
            # no del proyecto enviado por el usuario.
            data['project'] = project.pk

            serializer = AssetSerializer(data=data)

            serializer.is_valid(raise_exception=True)

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )


class AssetViewSet(viewsets.ModelViewSet):

    serializer_class = AssetSerializer

    permission_classes = [AssetPermission]

    def get_queryset(self):

        user = self.request.user

        # Los administradores pueden ver todos los Assets.
        if user.groups.filter(name='administradores').exists():
            return Asset.objects.all()

        # Los comerciales solamente ven Assets
        # pertenecientes a sus proyectos.
        return Asset.objects.filter(
            project__owner=user
        )