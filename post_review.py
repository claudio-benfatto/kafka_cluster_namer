"""Post a structured Review (see models.py) to a GitHub pull request as ONE review.

Findings on lines that are part of the PR diff become inline comments.
Findings on any other line (GitHub would reject them with a 422 and fail the
whole review) are listed in the review body instead, so nothing is dropped.

Usage:
    cat structured_output.json | python post_review.py --dry-run --diff-file pr.diff
    cat structured_output.json | python post_review.py --repo owner/name --pr 42

Posting goes through the `gh` CLI, which reads GH_TOKEN / GITHUB_TOKEN from the
environment (in Actions: `pull-requests: write` permission is required).
"""

import argparse
import json
import os
import re
import subprocess
import sys

from models import Finding, Review

HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def commentable_lines(diff: str) -> dict[str, set[int]]:
    """Map each file path to the set of NEW-file line numbers visible in the diff.

    Both added ('+') and context (' ') lines can receive a RIGHT-side comment;
    removed ('-') lines only exist on the old side, so they are skipped.
    """
    result: dict[str, set[int]] = {}
    current_file: str | None = None
    new_line = 0

    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            path = raw[4:].split("\t")[0]
            # "+++ /dev/null" means the file was deleted: nothing to comment on.
            current_file = path[2:] if path.startswith("b/") else None
            if current_file:
                result.setdefault(current_file, set())
            continue

        hunk = HUNK_HEADER.match(raw)
        if hunk:
            new_line = int(hunk.group(1))
            continue

        if current_file is None:
            continue
        if raw.startswith("+") or raw.startswith(" "):
            result[current_file].add(new_line)
            new_line += 1
        # '-' lines and '\ No newline at end of file' do not advance the new side.

    return result


def format_comment(finding: Finding) -> str:
    return f"**{finding.severity.upper()}**: {finding.message}"


def build_payload(review: Review, diff_lines: dict[str, set[int]]) -> dict:
    inline_comments = []
    outside_diff = []

    for finding in review.findings:
        if finding.line in diff_lines.get(finding.file, set()):
            inline_comments.append(
                {
                    "path": finding.file,
                    "line": finding.line,
                    "side": "RIGHT",  # `line` refers to the new version of the file
                    "body": format_comment(finding),
                }
            )
        else:
            outside_diff.append(finding)

    body_parts = [f"Automated review: {len(review.findings)} finding(s)."]
    if outside_diff:
        body_parts.append(
            "The following findings point at lines outside the changes in this PR, "
            "so they could not be attached inline:"
        )
        body_parts.append(
            "\n".join(f"- `{f.file}:{f.line}` {format_comment(f)}" for f in outside_diff)
        )

    payload: dict[str, object] = {"body": "\n\n".join(body_parts), "event": "COMMENT"}
    if inline_comments:
        payload["comments"] = inline_comments
    return payload


def fetch_diff(repo: str, pr: int) -> str:
    return subprocess.run(
        [
            "gh", "api", f"repos/{repo}/pulls/{pr}",
            "-H", "Accept: application/vnd.github.diff",
        ],
        check=True, capture_output=True, text=True,
    ).stdout


def post_review(repo: str, pr: int, payload: dict) -> None:
    result = subprocess.run(
        ["gh", "api", "--method", "POST", f"repos/{repo}/pulls/{pr}/reviews", "--input", "-"],
        input=json.dumps(payload), capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.exit(f"GitHub rejected the review:\n{result.stderr}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Post a structured Review to a GitHub PR as a single review")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"),
                        help="owner/name (default: $GITHUB_REPOSITORY)")
    parser.add_argument("--pr", type=int, help="pull request number")
    parser.add_argument("--diff-file", help="local unified diff, instead of fetching the PR's diff")
    parser.add_argument("--dry-run", action="store_true", help="print the payload, do not post")
    args = parser.parse_args()

    review = Review.model_validate_json(sys.stdin.read())

    if args.diff_file:
        with open(args.diff_file) as f:
            diff = f.read()
    elif args.repo and args.pr:
        diff = fetch_diff(args.repo, args.pr)
    else:
        parser.error("provide --diff-file, or both --repo and --pr, to know which lines are in the diff")

    payload = build_payload(review, commentable_lines(diff))

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return

    if not (args.repo and args.pr):
        parser.error("--repo and --pr are required to post")
    post_review(args.repo, args.pr, payload)
    print(f"Posted review with {len(payload.get('comments', []))} inline comment(s).")


if __name__ == "__main__":
    main()
