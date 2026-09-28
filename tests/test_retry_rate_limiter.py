import time
import httpx

from client import _get_page


SAMPLE = [
    {
        "some_key": "some_val"
    }
]

def test_get_page_retries_after_rate_limit():
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(
                403,
                request=request,
                headers={
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + 2),
                },
            )
        return httpx.Response(200, request=request, json=SAMPLE)

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        batch = _get_page(client, 'https://github.com/owner/repo', page=1, per_page=10)

    assert attempts == 2
    assert batch == SAMPLE