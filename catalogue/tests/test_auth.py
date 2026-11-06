import pytest
from rest_framework.authtoken.models import Token

pytestmark = pytest.mark.django_db


def test_token_is_created_for_new_users(commercial_user):
    assert Token.objects.filter(user=commercial_user).exists()


def test_token_authentication_grants_access(api_client, commercial_user):
    token = Token.objects.get(user=commercial_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    response = api_client.get("/api/v1/projects/")

    assert response.status_code == 200


def test_invalid_token_is_rejected(api_client):
    api_client.credentials(HTTP_AUTHORIZATION="Token not-a-real-token")

    response = api_client.get("/api/v1/projects/")

    assert response.status_code == 401


def test_user_can_obtain_a_token(api_client, commercial_user):
    response = api_client.post(
        "/api/v1/login/",
        {"username": commercial_user.username, "password": "password"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["token"] == Token.objects.get(user=commercial_user).key
