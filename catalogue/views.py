from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from catalogue.models import Project , Asset
from catalogue.permissions import ProjectPermission
from catalogue.serializers import ProjectSerializer , AssetSerializer
from rest_framework import filters, viewsets

class CatalogViewSet(viewsets.ModelViewSet):

    serializer_class = ProjectSerializer
    permission_classes = [ProjectPermission]

    def get_queryset(self):
        permission = ProjectPermission()
        return permission.permission_access_project(self.request)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(
        detail=True,
        methods=['get' ,'post'],
        url_path='assets'
    )
    def assets(self, request, pk=None):
        project = self.get_object()

        if request.method == 'GET':

            assets = Asset.objects.filter(project=project)

            serializer = AssetSerializer(assets, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':

            data = request.data.copy()
            data['project'] = project.pk

            serializer = AssetSerializer(data=data)

            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )