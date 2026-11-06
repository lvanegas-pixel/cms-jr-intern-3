import pytest

from catalogue.models import Project

pytestmark = pytest.mark.django_db


def test_commercial_only_sees_own_projects(api_client, commercial_user, other_commercial_user):
    own = Project.objects.create(name="Own project", owner=commercial_user)
    Project.objects.create(name="Foreign project", owner=other_commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.get("/api/v1/projects/")

    assert response.status_code == 200
    assert [project["id"] for project in response.data["results"]] == [own.id]


def test_admin_sees_every_project(api_client, admin_user, commercial_user, other_commercial_user):
    Project.objects.create(name="First project", owner=commercial_user)
    Project.objects.create(name="Second project", owner=other_commercial_user)

    api_client.force_authenticate(admin_user)
    response = api_client.get("/api/v1/projects/")

    assert response.status_code == 200
    assert response.data["count"] == 2
    assert len(response.data["results"]) == 2


def test_project_list_is_paginated_five_per_page(api_client, commercial_user):
    for index in range(6):
        Project.objects.create(name=f"Project {index}", owner=commercial_user)

    api_client.force_authenticate(commercial_user)
    first_page = api_client.get("/api/v1/projects/")
    second_page = api_client.get("/api/v1/projects/?page=2")

    assert first_page.data["count"] == 6
    assert len(first_page.data["results"]) == 5
    assert len(second_page.data["results"]) == 1


def test_project_name_requires_at_least_three_characters(api_client, commercial_user):
    api_client.force_authenticate(commercial_user)
    response = api_client.post("/api/v1/projects/", {"name": "ab"}, format="json")

    assert response.status_code == 400
    assert "name" in response.data


def test_commercial_cannot_retrieve_foreign_project(
    api_client, commercial_user, other_commercial_user
):
    foreign = Project.objects.create(name="Foreign project", owner=other_commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.get(f"/api/v1/projects/{foreign.id}/")

    assert response.status_code == 404


def test_created_project_is_owned_by_the_request_user(api_client, commercial_user):
    api_client.force_authenticate(commercial_user)
    response = api_client.post("/api/v1/projects/", {"name": "New project"}, format="json")

    assert response.status_code == 201
    assert Project.objects.get(pk=response.data["id"]).owner == commercial_user


def test_project_list_can_be_filtered_by_name(api_client, commercial_user):
    Project.objects.create(name="Alpha project", owner=commercial_user)
    Project.objects.create(name="Beta project", owner=commercial_user)
    Project.objects.create(name="Gamma thing", owner=commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.get("/api/v1/projects/?name=alpha", format="json")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Alpha project"


def test_project_list_can_be_filtered_by_owner(api_client, commercial_user, other_commercial_user):
    own = Project.objects.create(name="Own project", owner=commercial_user)
    Project.objects.create(name="Foreign project", owner=other_commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.get(f"/api/v1/projects/?owner={commercial_user.pk}", format="json")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == own.id


def test_commercial_can_delete_own_project(api_client, commercial_user):
    project = Project.objects.create(name="Own project", owner=commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.delete(f"/api/v1/projects/{project.id}/")

    assert response.status_code == 204
    assert not Project.objects.filter(pk=project.pk).exists()


def test_commercial_cannot_delete_foreign_project(
    api_client, commercial_user, other_commercial_user
):
    foreign = Project.objects.create(name="Foreign project", owner=other_commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.delete(f"/api/v1/projects/{foreign.id}/")

    assert response.status_code == 404
    assert Project.objects.filter(pk=foreign.pk).exists()


def test_admin_can_delete_any_project(
    api_client, admin_user, commercial_user
):
    project = Project.objects.create(name="Project", owner=commercial_user)

    api_client.force_authenticate(admin_user)
    response = api_client.delete(f"/api/v1/projects/{project.id}/")

    assert response.status_code == 204
    assert not Project.objects.filter(pk=project.pk).exists()
