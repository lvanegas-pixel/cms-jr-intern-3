import pytest

from catalogue.models import Asset, AuditLog, Project

pytestmark = pytest.mark.django_db


def test_project_creation_is_audited(api_client, commercial_user):
    api_client.force_authenticate(commercial_user)

    response = api_client.post(
        "/api/v1/projects/", {"name": "Audited project"}, format="json"
    )

    assert response.status_code == 201
    log = AuditLog.objects.get(action=AuditLog.Action.CREATE)
    assert log.user == commercial_user
    assert log.username == commercial_user.username
    assert log.object_type == "Project"
    assert log.object_id == response.data["id"]
    assert log.object_repr == "Audited project"
    assert log.changes["after"]["name"] == "Audited project"


def test_project_update_records_the_changed_fields(
    api_client, commercial_user
):
    project = Project.objects.create(name="Old name", owner=commercial_user)
    AuditLog.objects.all().delete()

    api_client.force_authenticate(commercial_user)
    response = api_client.patch(
        f"/api/v1/projects/{project.id}/",
        {"name": "New name"},
        format="json",
    )

    assert response.status_code == 200
    log = AuditLog.objects.get(action=AuditLog.Action.UPDATE)
    assert log.user == commercial_user
    assert log.object_type == "Project"
    assert log.object_id == project.id
    assert log.changes["name"] == {"from": "Old name", "to": "New name"}


def test_asset_delete_keeps_the_audit_trace(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)
    asset = Asset.objects.create(
        project=project,
        name="Main asset",
        asset_type=Asset.AssetType.IMAGE,
    )
    AuditLog.objects.all().delete()

    api_client.force_authenticate(commercial_user)
    response = api_client.delete(
        f"/api/v1/projects/{project.id}/assets/{asset.id}/"
    )

    assert response.status_code == 204
    assert not Asset.objects.filter(pk=asset.pk).exists()
    log = AuditLog.objects.get(
        action=AuditLog.Action.DELETE,
        object_type="Asset",
        object_id=asset.pk,
    )
    assert log.user == commercial_user
    assert log.object_repr == "Main asset"
    assert log.changes["before"]["name"] == "Main asset"


def test_deleting_a_project_also_audits_its_assets(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)
    asset = Asset.objects.create(
        project=project,
        name="Nested asset",
        asset_type=Asset.AssetType.VIDEO,
    )
    AuditLog.objects.all().delete()

    api_client.force_authenticate(commercial_user)
    response = api_client.delete(f"/api/v1/projects/{project.id}/")

    assert response.status_code == 204
    actions = set(
        AuditLog.objects.filter(action=AuditLog.Action.DELETE).values_list(
            "object_type", "object_id"
        )
    )
    assert ("Project", project.id) in actions
    assert ("Asset", asset.id) in actions


def test_audit_captures_the_user_of_token_authenticated_requests(
    api_client, commercial_user
):
    from rest_framework.authtoken.models import Token

    token = Token.objects.get(user=commercial_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    response = api_client.post(
        "/api/v1/projects/", {"name": "Token project"}, format="json"
    )

    assert response.status_code == 201
    log = AuditLog.objects.get(action=AuditLog.Action.CREATE)
    assert log.user == commercial_user
