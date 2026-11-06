import django_filters

from .models import Asset, Project


class ProjectFilter(django_filters.FilterSet):
    """Filterset for the Project list endpoint.

    - ``name`` : case-insensitive partial match.
    - ``owner`` : exact match on the owning user id.
    - ``created_at`` : range (before/after) on creation date.
    """

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    owner = django_filters.NumberFilter(field_name="owner_id")
    created_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Project
        fields = ["name", "owner", "created_at"]


class AssetFilter(django_filters.FilterSet):
    """Filterset for the Asset list endpoint.

    - ``name`` : case-insensitive partial match.
    - ``asset_type`` : exact match (MODEL_3D / IMAGE / VIDEO).
    - ``is_public`` : exact boolean match.
    - ``project`` : exact match on project id.
    """

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    asset_type = django_filters.ChoiceFilter(choices=Asset.AssetType.choices)
    is_public = django_filters.BooleanFilter()
    project = django_filters.NumberFilter(field_name="project_id")

    class Meta:
        model = Asset
        fields = ["name", "asset_type", "is_public", "project"]
