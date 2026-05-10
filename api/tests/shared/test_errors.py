from http import HTTPStatus

from babytroc.shared.errors import TooManyRequestsError


def test_too_many_requests_error_status_429():
    err = TooManyRequestsError("RATE_LIMITED")
    assert err.status_code == HTTPStatus.TOO_MANY_REQUESTS
    assert err.message == "RATE_LIMITED"


def test_too_many_requests_error_passes_headers():
    err = TooManyRequestsError("RATE_LIMITED", headers={"Retry-After": "60"})
    assert err.headers == {"Retry-After": "60"}
