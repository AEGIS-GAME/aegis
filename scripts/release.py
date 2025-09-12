"""
Custom script to copy the trash google software (release-please).

DO NOT RUN THIS MANUALLY!!!!!! The workflow will run this when PRs are merged.
"""
# ruff: noqa: S603, S607, PLW1510

import datetime
import json
import subprocess
from pathlib import Path
from typing import cast

import toml
from git import Commit, GitCommandError, Repo
from semver import VersionInfo

PACKAGES = {
    "client": {
        "file": "client/package.json",
        "tag_prefix": "client-v",
        "type": "npm",
        "path": "client",
    },
    "aegis": {
        "file": "pyproject.toml",
        "tag_prefix": "aegis-v",
        "type": "pypi",
        "path": ".",
    },
}


def get_last_tag(repo: Repo, prefix: str) -> str | None:
    """Get the most recent tag."""
    tags = [t.name for t in repo.tags if t.name.startswith(prefix)]
    if not tags:
        return None
    tags.sort(key=lambda x: VersionInfo.parse(x[len(prefix) :]))
    return tags[-1]


def collect_commits_by_package(
    repo: Repo, last_tag: str | None, path_filter: str
) -> list[Commit]:
    """Get the commits from the last tag to HEAD."""
    if last_tag:
        commits = list(repo.iter_commits(f"{last_tag}..HEAD", paths=path_filter))
    else:
        commits = list(repo.iter_commits("HEAD", paths=path_filter))
    return [c for c in commits if "release" not in str(c.message.lower())]


def has_breaking_change(msg: str) -> bool:
    """Return True if commit has BREAKING CHANGE or '!' before the colon."""
    if "BREAKING CHANGE" in msg:
        return True
    header = msg.split(":", 1)[0]
    return "!" in header


def detect_bump(messages: list[str]) -> str | None:
    """Detect bump version."""
    bump = None
    for msg in messages:
        if has_breaking_change(msg):
            return "major"
        if msg.startswith("feat"):
            bump = "minor"
        elif msg.startswith("fix") and bump != "minor":
            bump = "patch"
    return bump


def bump_version(current: str, bump: str) -> str:
    """Bump sem version."""
    v = VersionInfo.parse(current)
    if bump == "major":
        return str(v.bump_major())
    if bump == "minor":
        return str(v.bump_minor())
    return str(v.bump_patch())


def update_version(pkg: str, new_version: str) -> None:
    """Update version in package specific file."""
    path = Path(PACKAGES[pkg]["file"])
    if pkg == "client":
        with path.open() as f:
            data = json.load(f)  # pyright: ignore[reportAny]
        data["version"] = new_version
        with path.open("w") as f:
            json.dump(data, f, indent=2)
            _ = f.write("\n")
    else:
        data = toml.load(path)
        data["project"]["version"] = new_version
        with path.open("w") as f:
            _ = toml.dump(data, f)


def build_package_section(pkg: str, messages: list[str], version: str) -> str:
    """Build a changelog section for a single package."""
    features: list[str] = []
    fixes: list[str] = []
    breaking: list[str] = []
    others: list[str] = []

    for msg in messages:
        header_line = msg.splitlines()[0].strip()
        header = header_line.split(":", 1)[0]

        if "BREAKING CHANGE" in header_line or "!" in header:
            breaking.append(f"- {header_line}")
        elif header_line.startswith("feat"):
            features.append(f"- {header_line}")
        elif header_line.startswith("fix"):
            fixes.append(f"- {header_line}")
        else:
            others.append(f"- {header_line}")

    sections: list[str] = []
    if breaking:
        sections.append("### 💥 Breaking Changes\n" + "\n".join(breaking))
    if features:
        sections.append("### ✨ Features\n" + "\n".join(features))
    if fixes:
        sections.append("### 🐛 Fixes\n" + "\n".join(fixes))
    if others:
        sections.append("### 📝 Other\n" + "\n".join(others))

    section_text = "\n\n".join(sections) if sections else "No notable changes."

    # Wrap in collapsible
    return f"<details>\n  <summary>{pkg} v{version}</summary>\n\n{section_text}\n</details>"


def build_changelog(
    all_commit_messages: dict[str, list[str]], new_versions: dict[str, str]
) -> dict[str, str]:
    """
    Build changelogs for all packages and update their versions.

    Returns a dict mapping each package name to its changelog string.
    """
    changelogs: dict[str, str] = {}

    for pkg, messages in all_commit_messages.items():
        if not messages or pkg not in new_versions:
            continue

        update_version(pkg, new_versions[pkg])

        changelogs[pkg] = build_package_section(pkg, messages, new_versions[pkg])

    return changelogs


def create_or_update_pr(
    new_versions: dict[str, str], changelogs: dict[str, str]
) -> None:
    """Create or update a single combined release PR with per-package changelogs."""
    branch = "release-branch"
    title = f"chore(release): release v{new_versions['aegis']}"

    repo = Repo(".")
    try:
        repo.git.checkout(branch)  # pyright: ignore[reportAny]
        print(f"[*] Pulled existing branch '{branch}' from origin")
        repo.git.pull("origin", branch)  # pyright: ignore[reportAny]
    except GitCommandError:
        print(f"[!] Branch '{branch}' does not exist. Creating new branch.")
        repo.git.checkout("-b", branch)  # pyright: ignore[reportAny]

    today = datetime.datetime.now(tz=datetime.UTC).date()

    for pkg, changelog in changelogs.items():
        if pkg not in new_versions:
            continue

        header = f"## v{new_versions[pkg]} ({today})\n\n"
        if pkg == "client":
            changelog_path = Path("client/CHANGELOG.md")
        else:  # aegis
            changelog_path = Path("CHANGELOG.md")

        old_content = changelog_path.read_text()
        if old_content.startswith("# Changelog"):
            lines = old_content.splitlines(keepends=True)
            first_line = lines[0]
            rest = "".join(lines[1:])
            new_content = first_line + "\n" + header + changelog + "\n\n" + rest
        else:
            new_content = header + changelog + "\n\n" + old_content

        _ = changelog_path.write_text(new_content)
        repo.git.add(str(changelog_path))  # pyright: ignore[reportAny]

    staged_files = repo.git.diff("--cached", "--name-only")  # pyright: ignore[reportAny]
    print(f"[*] Files staged for commit:\n{staged_files}")

    repo.git.config("user.name", "github-actions[bot]")  # pyright: ignore[reportAny]
    repo.git.config("user.email", "github-actions[bot]@users.noreply.github.com")  # pyright: ignore[reportAny]

    try:
        repo.git.commit("-m", title)  # pyright: ignore[reportAny]
    except GitCommandError as e:
        print(f"[*] No changes to commit: {e}")

    repo.git.push("origin", branch)  # pyright: ignore[reportAny]

    pr_list = subprocess.run(
        ["gh", "pr", "list", "--head", branch, "--json", "number"],
        capture_output=True,
        text=True,
    )

    print(f"[*] Existing PRs: {pr_list.stdout}")

    if "[]" in pr_list.stdout:
        body = "\n\n".join(
            changelog for pkg, changelog in changelogs.items() if pkg in new_versions
        )
        _ = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                body,
                "--base",
                "main",
                "--head",
                branch,
            ],
            check=True,
        )


def main() -> None:
    """Entry point for release script."""
    repo = Repo(".")
    all_commit_messages: dict[str, list[str]] = {}
    bumps: dict[str, str] = {}

    for pkg in PACKAGES:
        print(f"[*] Checking {pkg}...")
        prefix = PACKAGES[pkg]["tag_prefix"]
        last_tag = get_last_tag(repo, prefix)

        commits = collect_commits_by_package(repo, last_tag, PACKAGES[pkg]["path"])

        if pkg == "aegis":
            commits = [
                c
                for c in commits
                if not any(
                    str(f).startswith(PACKAGES["client"]["path"]) for f in c.stats.files
                )
            ]

        messages = [str(c.message.strip()) for c in commits]
        all_commit_messages[pkg] = messages
        bump = detect_bump(messages)
        if bump:
            bumps[pkg] = bump

    if not bumps:
        print("[*] No release needed for any package")
        return

    new_versions: dict[str, str] = {}
    for pkg in PACKAGES:
        if pkg not in bumps:
            continue
        path = Path(PACKAGES[pkg]["file"])
        if pkg == "client":
            with path.open() as f:
                current = cast("str", json.load(f)["version"])
        else:
            data = toml.load(path)
            current = cast("str", data["project"]["version"])

        new_versions[pkg] = bump_version(current, bumps[pkg])

    # TODO: DELETE AFTER FIRST RELEASE
    new_versions = {"client": "2.6.0", "aegis": "2.6.0"}
    changelog_body = build_changelog(all_commit_messages, new_versions)
    create_or_update_pr(new_versions, changelog_body)
    print("[*] Release PR updated")


if __name__ == "__main__":
    main()
