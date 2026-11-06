from django.http import HttpRequest, HttpResponse

from .audit import reset_current_request, set_current_request


class CurrentUserMiddleware:
    """Expose the active request to model signals during a request.

    Signals read ``request.user`` when they fire, so the user resolved later by
    DRF's token authentication is also available. This keeps audit logic out of
    the views.
    """

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        token = set_current_request(request)
        try:
            return self.get_response(request)
        finally:
            reset_current_request(token)
