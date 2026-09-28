import re
from typing import Any
import httpx
import time
from tenacity import RetryCallState, retry, retry_if_exception_type, stop_after_attempt

REPO_RE = re.compile(r"(?P<host>github\.com/)?(?P<owner>[\w|-]+)/(?P<repo>[\w|-]+)")
ENDPOINT = 'https://api.github.com/repos/{}/{}/commits'
PER_PAGE = 100

class RateLimited(Exception):
    def __init__(self, reset_at: int):
        self.reset_at = reset_at

def parse_repo(value: str) -> tuple[str, str]:
    repo = REPO_RE.search(value)
    if not repo:
        raise ValueError("Use owner/repo or https://github.com/owner/repo")
    return repo.group('owner'), repo.group('repo')

def normalize(payload: dict[str, Any]) -> dict[str, str]:
    author = (payload.get("commit") or {}).get("author") or {}
    return {
        "sha": payload.get("sha", ""),
        "author_name": author.get("name") or "",
        "author_email": author.get("email") or "",
        "date": author.get("date") or "",
        "message": (payload.get("commit") or {}).get("message") or "",
    }

def _wait(retry_state: RetryCallState) -> float:
    exc = retry_state.outcome.exception() if retry_state.outcome else None
    if isinstance(exc, RateLimited):
        return max(0.0, exc.reset_at - time.time()) + 1.0
    return 1.0

@retry(
    retry=retry_if_exception_type((RateLimited, httpx.TransportError)),
    wait=_wait,
    stop=stop_after_attempt(3),
    reraise=True,
)
def _get_page(client: httpx.Client, url: str, page: int, per_page: int) -> list[dict]:
    response = client.get(url, params={"page": page, "per_page": PER_PAGE})
    if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
        reset = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        raise RateLimited(reset)
    response.raise_for_status()
    return response.json()


def fetch_commits(owner: str, name: str, limit: int):
    url = ENDPOINT.format(owner, name)
    commits: list[dict] = []
    page = 1
    with httpx.Client(timeout=30) as client:
        while len(commits) < limit:
            batch = _get_page(client, url, page, PER_PAGE)
            if not batch:
                break
            for item in batch:
                commits.append(normalize(item))
                if len(commits) >= limit:
                    break
            page += 1

    return commits