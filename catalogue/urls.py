from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, AssetViewSet

router = DefaultRouter()
router.register(r'projects',ProjectViewSet,basename='project')
router.register(r'assets',AssetViewSet,basename='asset')

urlpatterns = [
    path('', include(router.urls)),
]