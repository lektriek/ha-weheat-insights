#!/usr/bin/env python3
"""Prepare a release, or print a version's release notes.

    scripts/release.py 1.2.0          set the version everywhere, date the
                                      changelog, commit "Release 1.2.0" and
                                      tag v1.2.0
    scripts/release.py 1.3.0-beta.1   the same, as a pre-release
    scripts/release.py --notes 1.2.0  print that version's changelog section
                                      (used by .github/workflows/release.yml)

The version is set in custom_components/*/manifest.json and, when present, in
pyproject.toml and frontend/package.json with its lock file. Nothing is pushed;
the script prints the push command. Pushing the tag starts the Release
workflow, which publishes the GitHub release that HACS offers.

This file is kept identical in ha-weheat-control and ha-weheat-insights.
"""

from __future__ import annotations

import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = ROOT / "CHANGELOG.md"
PYPROJECT = ROOT / "pyproject.toml"
PACKAGE_JSONS = [ROOT / "frontend" / "package.json", ROOT / "frontend" / "package-lock.json"]
VERSION = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?$")
HEADING = re.compile(r"^## \[([^\]]+)\]", re.MULTILINE)
UNRELEASED_LINK = re.compile(r"^\[Unreleased\]: \S+/compare/(\S+)\.\.\.HEAD$", re.MULTILINE)


def fail(message: str) -> None:
    sys.exit(f"error: {message}")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def manifest_path() -> Path:
    manifests = sorted(ROOT.glob("custom_components/*/manifest.json"))
    if len(manifests) != 1:
        fail("expected exactly one custom_components/*/manifest.json")
    return manifests[0]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def sort_key(version: str) -> tuple:
    major, minor, patch, pre = VERSION.match(version).groups()
    # A final release sorts after its own pre-releases.
    return (int(major), int(minor), int(patch), pre is None, pre or "")


def section(text: str, name: str) -> str | None:
    """Return the body of the "## [name]" section, or None if there is none."""
    headings = list(HEADING.finditer(text))
    for index, heading in enumerate(headings):
        if heading.group(1) == name:
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            body = text[heading.end() : end]
            # Drop the rest of the heading line and the link references at the end.
            body = body.split("\n", 1)[1] if "\n" in body else ""
            body = re.sub(r"^\[[^\]]+\]: \S+$", "", body, flags=re.MULTILINE)
            return body.strip()
    return None


def notes(version: str) -> None:
    text = CHANGELOG.read_text()
    body = section(text, version)
    if not body:
        fail(f"CHANGELOG.md has no notes for {version}")
    link = re.search(rf"^\[{re.escape(version)}\]: (\S+)$", text, re.MULTILINE)
    print(body + (f"\n\n**Full changes**: {link.group(1)}" if link else ""))


def set_version(version: str) -> list[Path]:
    """Write the version to every file that carries it; return those files."""
    manifest = manifest_path()
    data = read_json(manifest)
    data["version"] = version
    write_json(manifest, data)
    changed = [manifest]

    if PYPROJECT.exists():
        text = PYPROJECT.read_text()
        new, count = re.subn(r'(?m)^version = "[^"]*"$', f'version = "{version}"', text, count=1)
        if count:
            PYPROJECT.write_text(new)
            changed.append(PYPROJECT)

    for path in PACKAGE_JSONS:
        if path.exists():
            data = read_json(path)
            data["version"] = version
            if "" in data.get("packages", {}):
                data["packages"][""]["version"] = version
            write_json(path, data)
            changed.append(path)
    return changed


def release(version: str) -> None:
    if not VERSION.match(version):
        fail(f"{version} is not a version like 1.2.3 or 1.2.3-beta.1")
    if git("status", "--porcelain", "--untracked-files=no"):
        fail("commit or stash your changes first")
    tag = f"v{version}"
    if git("tag", "--list", tag):
        fail(f"tag {tag} already exists")

    manifest = read_json(manifest_path())
    current = manifest["version"]
    if sort_key(version) <= sort_key(current):
        fail(f"{version} is not newer than the current version {current}")
    repo_url = manifest["documentation"].rstrip("/")

    text = CHANGELOG.read_text()
    if not section(text, "Unreleased"):
        fail("the Unreleased section of CHANGELOG.md is empty; describe the changes first")
    link = UNRELEASED_LINK.search(text)
    if not link:
        fail("CHANGELOG.md has no [Unreleased] compare link")

    today = datetime.date.today().isoformat()
    text = text.replace("## [Unreleased]", f"## [Unreleased]\n\n## [{version}] - {today}", 1)
    text = UNRELEASED_LINK.sub(
        f"[Unreleased]: {repo_url}/compare/{tag}...HEAD\n[{version}]: {repo_url}/compare/{link.group(1)}...{tag}",
        text,
        count=1,
    )
    CHANGELOG.write_text(text)
    changed = [CHANGELOG, *set_version(version)]

    git("add", *map(str, changed))
    git("commit", "--quiet", "-m", f"Release {version}")
    git("tag", "--annotate", tag, "-m", f"Release {version}")
    try:
        upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        remote, target = upstream.split("/", 1)
    except subprocess.CalledProcessError:
        remote, target = "origin", "main"
    print(f"Committed and tagged {tag}. Check the commit, then publish with:\n")
    print(f"    git push --atomic {remote} HEAD:{target} {tag}")


def main(args: list[str]) -> None:
    if len(args) == 2 and args[0] == "--notes":
        notes(args[1])
    elif len(args) == 1 and not args[0].startswith("-"):
        release(args[0])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
