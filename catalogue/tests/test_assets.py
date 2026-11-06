import pytest

from catalogue.models import Asset, Project

pytestmark = pytest.mark.django_db


def _assets_url(project: Project) -> str:
    return f"/api/v1/projects/{project.id}/assets/"


def _asset_payload(asset_type: str = Asset.AssetType.IMAGE) -> dict:
    return {"name": "An asset", "asset_type": asset_type}


def test_project_can_only_have_one_model_3d(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)
    Asset.objects.create(
        project=project,
        name="Main model",
        asset_type=Asset.AssetType.MODEL_3D,
    )

    api_client.force_authenticate(commercial_user)
    response = api_client.post(
        _assets_url(project),
        _asset_payload(Asset.AssetType.MODEL_3D),
        format="json",
    )

    assert response.status_code == 400
    assert "asset_type" in response.data


def test_project_can_have_many_non_model_3d_assets(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)

    api_client.force_authenticate(commercial_user)
    first = api_client.post(
        _assets_url(project), _asset_payload(Asset.AssetType.IMAGE), format="json"
    )
    second = api_client.post(
        _assets_url(project), _asset_payload(Asset.AssetType.VIDEO), format="json"
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.data["project"] == project.id


def test_commercial_cannot_create_asset_in_foreign_project(
    api_client, commercial_user, other_commercial_user
):
    foreign = Project.objects.create(name="Foreign project", owner=other_commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.post(
        _assets_url(foreign),
        _asset_payload(Asset.AssetType.IMAGE),
        format="json",
    )

    assert response.status_code == 403
    assert Asset.objects.count() == 0


def test_commercial_cannot_list_foreign_project_assets(
    api_client, commercial_user, other_commercial_user
):
    foreign = Project.objects.create(name="Foreign project", owner=other_commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.get(_assets_url(foreign))

    assert response.status_code == 403


def test_commercial_can_create_asset_in_own_project(api_client, commercial_user):
    own = Project.objects.create(name="Own project", owner=commercial_user)

    api_client.force_authenticate(commercial_user)
    response = api_client.post(
        _assets_url(own), _asset_payload(Asset.AssetType.IMAGE), format="json"
    )

    assert response.status_code == 201
    assert Asset.objects.filter(project=own).exists()


def test_admin_can_create_asset_in_any_project(
    api_client, admin_user, commercial_user
):
    project = Project.objects.create(name="Project", owner=commercial_user)

    api_client.force_authenticate(admin_user)
    response = api_client.post(
        _assets_url(project),
        _asset_payload(Asset.AssetType.MODEL_3D),
        format="json",
    )

    assert response.status_code == 201


def test_list_returns_only_the_project_assets(api_client, commercial_user):
    own = Project.objects.create(name="Own project", owner=commercial_user)
    other = Project.objects.create(name="Other project", owner=commercial_user)
    own_asset = Asset.objects.create(
        project=own, name="Own asset", asset_type=Asset.AssetType.IMAGE
    )
    Asset.objects.create(
        project=other, name="Other asset", asset_type=Asset.AssetType.VIDEO
    )

    api_client.force_authenticate(commercial_user)
    response = api_client.get(_assets_url(own))

    assert response.status_code == 200
    assert [asset["id"] for asset in response.data["results"]] == [own_asset.id]


def test_asset_detail_can_be_retrieved_and_updated(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)
    asset = Asset.objects.create(
        project=project, name="Asset", asset_type=Asset.AssetType.IMAGE
    )
    url = f"{_assets_url(project)}{asset.id}/"

    api_client.force_authenticate(commercial_user)
    retrieved = api_client.get(url)
    updated = api_client.patch(url, {"name": "Renamed"}, format="json")

    assert retrieved.status_code == 200
    assert updated.status_code == 200
    assert updated.data["name"] == "Renamed"


def test_asset_list_can_be_filtered_by_asset_type(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)
    image = Asset.objects.create(
        project=project, name="Image", asset_type=Asset.AssetType.IMAGE
    )
    Asset.objects.create(
        project=project, name="Model", asset_type=Asset.AssetType.MODEL_3D
    )

    api_client.force_authenticate(commercial_user)
    url = f"{_assets_url(project)}?asset_type=IMAGE"
    response = api_client.get(url, format="json")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == image.id


def test_asset_list_can_be_filtered_by_name(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)
    Asset.objects.create(project=project, name="Red cube", asset_type=Asset.AssetType.IMAGE)
    Asset.objects.create(project=project, name="Blue sphere", asset_type=Asset.AssetType.IMAGE)

    api_client.force_authenticate(commercial_user)
    url = f"{_assets_url(project)}?name=cube"
    response = api_client.get(url, format="json")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["name"] == "Red cube"


def test_asset_list_can_be_filtered_by_is_public(api_client, commercial_user):
    project = Project.objects.create(name="Project", owner=commercial_user)
    public = Asset.objects.create(
        project=project, name="Public", asset_type=Asset.AssetType.IMAGE, is_public=True
    )
    Asset.objects.create(
        project=project, name="Private", asset_type=Asset.AssetType.IMAGE, is_public=False
    )

    api_client.force_authenticate(commercial_user)
    url = f"{_assets_url(project)}?is_public=true"
    response = api_client.get(url, format="json")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == public.id


def test_commercial_can_delete_asset_of_own_project(api_client, commercial_user):
    project = Project.objects.create(name="Own project", owner=commercial_user)
    asset = Asset.objects.create(
        project=project, name="Asset", asset_type=Asset.AssetType.IMAGE
    )

    api_client.force_authenticate(commercial_user)
    response = api_client.delete(f"{_assets_url(project)}{asset.id}/")

    assert response.status_code == 204
    assert not Asset.objects.filter(pk=asset.pk).exists()


def test_commercial_cannot_delete_asset_of_foreign_project(
    api_client, commercial_user, other_commercial_user
):
    foreign = Project.objects.create(name="Foreign project", owner=other_commercial_user)
    asset = Asset.objects.create(
        project=foreign, name="Asset", asset_type=Asset.AssetType.IMAGE
    )

    api_client.force_authenticate(commercial_user)
    response = api_client.delete(f"{_assets_url(foreign)}{asset.id}/")

    assert response.status_code == 403
    assert Asset.objects.filter(pk=asset.pk).exists()


def test_admin_can_delete_asset_of_any_project(
    api_client, admin_user, commercial_user
):
    project = Project.objects.create(name="Project", owner=commercial_user)
    asset = Asset.objects.create(
        project=project, name="Asset", asset_type=Asset.AssetType.VIDEO
    )

    api_client.force_authenticate(admin_user)
    response = api_client.delete(f"{_assets_url(project)}{asset.id}/")

    assert response.status_code == 204
    assert not Asset.objects.filter(pk=asset.pk).exists()
