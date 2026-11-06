from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """Default pagination with a client-controlled page size."""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100
