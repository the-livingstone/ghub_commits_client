# GitHub commits client
_start datetime: 2026-09-28T16:04:02 UTC_


Fetches commits from a public repository via the GitHub REST API, paginates results, handles rate limits, and outputs a normalized JSON list.


## Dependencies

- Python 3.11+
- httpx
- tenacity

## Quickstart

```bash
cd github_commits_client
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

## How to use

```bash
# Print commits to stdout (JSON array)
python main.py --repo torvalds/linux --limit 250

# Shorthand
python main.py -r https://github.com/torvalds/linux -n 50

# Write to a file
python main.py -r owner/repo -n 100 -o commits.json
```

| Option | Description |
|--------|-------------|
| `--repo`, `-r` | `owner/repo` or a `https://github.com/owner/repo` URL |
| `--limit`, `-n` | Number of commits to fetch (default: 100) |
| `--output`, `-o` | Optional path for JSON output; otherwise stdout |

Each commit is normalized to:

`sha`, `author_name`, `author_email`, `date`, `message` (from git `commit.author`, not the GitHub user profile).

Without authentication, GitHub allows about 60 requests/hour. On rate limit (`403` with `X-RateLimit-Remaining: 0`), the client waits until `X-RateLimit-Reset` and retries.

## What else could be done

**Authentication** — Read a `GITHUB_TOKEN` (or `--token`) and send `Authorization: Bearer …` to raise the primary rate limit.

**Project layout** — Split `main.py` / `client.py` into a small package: a `cli` module (argparse only), a `GitHubCommitsClient` class (HTTP, pagination, retries), and `Commit` dataclasses for the normalized shape instead of plain dicts.

**Logging** — Use `logging` module: INFO for page number and total fetched, WARNING when sleeping for rate limit, DEBUG for retry attempts.

**Output shape / field picker** — Now a fixed flat schema is exported. A configurable projector would let callers choose paths from the raw API object (dot notation), e.g. `sha`, `commit.message`, `commit.author.name`, `commit.author.email`, `author.login` for the GitHub user when present. CLI examples: `--fields sha,commit.message,author.name,author.email` or a small JSON/YAML map that builds nested output (`author: { name, email }`) instead of `author_name` / `author_email`. Trade-off: flexible for integrations, but more UX work (aliases, docs for GitHub’s nested `commit` vs top-level `author`) than a single hard-coded normalize function.
