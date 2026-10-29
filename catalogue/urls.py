from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatalogueViewSet

router = DefaultRouter()
router.register(r'catalogue', CatalogueViewSet, basename='catalogue')

urlpatterns = [
    path('', include(router.urls)),
]