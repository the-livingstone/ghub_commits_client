import re
from typing import Any
import httpx

REPO_RE = re.compile(r"(?P<host>github\.com/)?(?P<owner>[\w|-]+)/(?P<repo>[\w|-]+)")
ENDPOINT = 'https://api.github.com/repos/{}/{}/commits'
PER_PAGE = 100

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

def fetch_commits(owner: str, name: str, limit: int):
    url = ENDPOINT.format(owner, name)
    commits: list[dict] = []
    page = 1
    with httpx.Client(timeout=30) as client:
        while len(commits) < limit:
            response = client.get(url, params={"page": page, "per_page": PER_PAGE})
            batch = response.json()
            if not batch:
                break
            for item in batch:
                commits.append(normalize(item))
                if len(commits) >= limit:
                    break
            page += 1

    return commits