import argparse
import json
import sys

from client import fetch_commits, parse_repo


def main():
    parser = argparse.ArgumentParser(
        description="Fetch GitHub commits as normalized JSON."
    )
    parser.add_argument("--repo", "-r", required=True, help="owner/repo or GitHub URL")
    parser.add_argument(
        "--limit", "-n", type=int, default=100, help="How many commits to fetch"
    )
    parser.add_argument("--output", "-o", help="Optional output file")
    args = parser.parse_args()

    if args.limit < 1:
        print("limit must be >= 1", file=sys.stderr)
        return 2

    try:
        owner, name = parse_repo(args.repo)
    except ValueError as e:
        print(e, file=sys.stderr)
        return 2

    try:
        commits = fetch_commits(owner, name, args.limit)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    text = json.dumps(commits, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
