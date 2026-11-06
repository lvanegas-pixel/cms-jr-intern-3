import pytest
from rest_framework.test import APIClient

from accounts.models import User


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_user(
        username="admin",
        password="password",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def commercial_user(db) -> User:
    return User.objects.create_user(
        username="commercial",
        password="password",
        role=User.Role.COMMERCIAL,
    )


@pytest.fixture
def other_commercial_user(db) -> User:
    return User.objects.create_user(
        username="other",
        password="password",
        role=User.Role.COMMERCIAL,
    )
