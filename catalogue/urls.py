from rest_framework.routers import DefaultRouter
from .views import CatalogViewSet

router = DefaultRouter()

router.register(r'projects', CatalogViewSet, basename='project')

urlpatterns = router.urls