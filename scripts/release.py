"""Custom script to copy the trash google software (release-please)."""
# ruff: noqa: S603, S607, PLW1510

import contextlib
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
) -> str:
    """Build a combined changelog for all packages and update their versions."""
    changelog_sections: list[str] = []

    for pkg, messages in all_commit_messages.items():
        if not messages or pkg not in new_versions:
            continue

        # Update package version
        update_version(pkg, new_versions[pkg])

        # Build section
        section = build_package_section(pkg, messages, new_versions[pkg])
        changelog_sections.append(section)

    return "\n\n".join(changelog_sections)


def create_or_update_pr(changelog_body: str) -> None:
    """Create or update a single combined release PR."""
    branch = "release-branch"
    title = "chore(release): release updates"

    repo = Repo(".")
    try:
        repo.git.checkout(branch)  # pyright: ignore[reportAny]
        repo.git.pull("origin", branch)  # pyright: ignore[reportAny]
    except GitCommandError:
        repo.git.checkout("-b", branch)  # pyright: ignore[reportAny]

    # Commit changelog updates
    changelog_path = Path("CHANGELOG.md")
    _ = changelog_path.write_text(changelog_body + "\n")
    repo.git.add(A=True)  # pyright: ignore[reportAny]
    with contextlib.suppress(GitCommandError):
        repo.git.commit(m=title)  # pyright: ignore[reportAny]
    repo.git.push("origin", branch)  # pyright: ignore[reportAny]

    # Create PR if it doesn't exist
    pr_list = subprocess.run(
        ["gh", "pr", "list", "--head", branch, "--json", "number"],
        capture_output=True,
        text=True,
    )
    if "[]" in pr_list.stdout:
        _ = subprocess.run(
            [
                "gh",
                "pr",
                "create",
                "--title",
                title,
                "--body",
                changelog_body,
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

    # 1️⃣ Collect commits & detect bumps
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
    create_or_update_pr(changelog_body)
    print("[*] Release PR updated")


if __name__ == "__main__":
    main()
