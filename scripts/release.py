"""Custom script to copy the trash google software (release-please)."""
# ruff: noqa: S603, S607, PLW1510

import json
import subprocess
from pathlib import Path

import toml
from git import Commit, GitCommandError, Repo
from semver import VersionInfo
import contextlib

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
        with Path.open(path) as f:
            data = json.load(f)  # pyright: ignore[reportAny]
        data["version"] = new_version
        with Path.open(path, "w") as f:
            json.dump(data, f, indent=2)
            _ = f.write("\n")
    else:
        data = toml.load(path)
        data["project"]["version"] = new_version
        with Path.open(path, "w") as f:
            _ = toml.dump(data, f)


def build_changelog(messages: list[str]) -> str:
    """Build a changelog grouped by section."""
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

    return "\n\n".join(sections) if sections else "No notable changes."


def create_or_update_pr(pkg: str, new_version: str, changelog: str) -> None:
    """Create or update a release PR without overwriting."""
    branch = f"release/{pkg}-v{new_version}"
    title = f"chore(release): {pkg} v{new_version}"

    repo = Repo(".")
    try:
        repo.git.checkout(branch)  # pyright: ignore[reportAny]
        repo.git.pull("origin", branch)  # pyright: ignore[reportAny]
    except GitCommandError:
        repo.git.checkout("-b", branch)  # pyright: ignore[reportAny]

    update_version(pkg, new_version)
    changelog_path = Path(f"{pkg}_CHANGELOG.md")
    _ = changelog_path.write_text(changelog + "\n")

    repo.git.add(A=True)  # pyright: ignore[reportAny]
    with contextlib.suppress(GitCommandError):
        repo.git.commit(m=title)  # pyright: ignore[reportAny]

    repo.git.push("origin", branch)  # pyright: ignore[reportAny]

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
                changelog,
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
    for pkg in PACKAGES:
        print(f"[*] Checking {pkg}...")
        prefix = PACKAGES[pkg]["tag_prefix"]
        last_tag = get_last_tag(repo, prefix)
        if last_tag is None:
            print(f"[!] Could not find recent tag for {pkg}")
        commits = collect_commits_by_package(repo, last_tag, PACKAGES[pkg]["path"])
        if pkg == "aegis":
            commits = [
                c
                for c in commits
                if not any(
                    str(f).startswith(PACKAGES["client"]["path"]) for f in c.stats.files
                )
            ]
        commit_messages = [str(c.message.strip()) for c in commits]
        bump = detect_bump(commit_messages)
        if not bump:
            print(f"[*] No release needed for {pkg}")
            continue

        # TODO: remove this if check after I release first version with tag
        path = Path(PACKAGES[pkg]["file"])
        current = "2.5.5"
        if last_tag is None:
            new_version = "2.6.0"
        elif pkg == "client":
            with Path.open(path) as f:
                current = json.load(f)["version"]
        else:
            data = toml.load(path)
            current = data["project"]["version"]

        new_version = bump_version(current, bump)
        print(f"[*] {pkg}: {current} → {new_version}")
        changelog = build_changelog(commit_messages)
        create_or_update_pr(pkg, new_version, changelog)


if __name__ == "__main__":
    main()
