"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from pathlib import Path

from django.contrib import admin
from django.urls import include, path
from django.views.static import serve
from rest_framework.authtoken.views import obtain_auth_token

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/login/", obtain_auth_token, name="api-v1-login"),
    path("api/v2/login/", obtain_auth_token, name="api-v2-login"),
    path("api/v1/", include("catalogue.urls")),
    path("api/v2/", include("catalogue.urls_v2")),
    path("frontend/<path:path>", serve, {"document_root": FRONTEND_DIR}),
    path("", serve, {"path": "index.html", "document_root": FRONTEND_DIR}),
]
