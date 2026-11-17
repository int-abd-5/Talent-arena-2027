"""Check public repository boundaries and links in the participant instructions."""

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def check(root: Path) -> list[str]:
    """Return actionable problems with checked-in and staged paths and entry files."""
    problems = []
    if (root / "AGENTS.md").read_bytes() != (root / "CLAUDE.md").read_bytes():
        problems.append("The two repository entry files differ.")
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).split(b"\0")
    asset_extensions = {".mp4", ".mov", ".zip", ".xml", ".csv", ".npz", ".npy", ".parquet"}
    for entry in filter(None, tracked):
        path = Path(entry.decode())
        if (
            path.parts[0] in {"data", "outputs"}
            or path.suffix.lower() in asset_extensions
            or path.name.lower().endswith("_atd.txt")
        ):
            problems.append(f"Keep generated output and data out of Git: {path}")

    for name in ("README.md", "TECHNICAL_REPORT.md", "app/CONSTRAINTS.md"):
        owner = root / name
        if not owner.exists():
            continue
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", owner.read_text(encoding="utf-8")):
            link = urlsplit(target.strip("<>"))
            if link.path and not link.scheme and not link.netloc:
                if not (owner.parent / unquote(link.path)).exists():
                    problems.append(f"Broken local link in {name}: {target}")
    return problems


if __name__ == "__main__":
    issues = check(Path(__file__).resolve().parents[2])
    if issues:
        sys.exit("\n".join(issues))
    print("Repository entry files, data boundaries, and local links checked.")
