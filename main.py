

from pprint import pp
from client import fetch_commits, parse_repo


GITHUB_REPO = 'https://github.com/torvalds/linux.git'
LIMIT = 100


def main():
    owner, name = parse_repo(GITHUB_REPO)
    commits = fetch_commits(owner, name, LIMIT)
    pp(commits)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())