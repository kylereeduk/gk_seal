# Guru Codex Seal v1.0 ⟡GK⟡ | GKCI-2025-7F3A2E | Oath: Through every line, leave the world lighter than before.
# Project: Repo | File: tools/gk_seal_check.py | Author: Kyle × Guru | Version: v1.0.0 | Date: 2025-10-29
import argparse, os, re, json, hashlib, sys, datetime
from pathlib import Path

GK_TAG = "GKCI-2025-7F3A2E"
OATH = "Through every line, leave the world lighter than before."

COMMENT_PREFIX = {
    ".py": "#", ".js": "//", ".ts": "//", ".tsx": "//", ".jsx": "//",
    ".java": "//", ".c": "//", ".h": "//", ".cpp": "//", ".hpp": "//",
    ".cs": "//", ".go": "//", ".rb": "#", ".php": "//", ".rs": "//",
    ".swift": "//", ".kt": "//", ".kts": "//", ".m": "//", ".sh": "#",
    ".bash": "#", ".zsh": "#", ".ps1": "#", ".psm1": "#", ".yml": "#",
    ".yaml": "#", ".toml": "#", ".ini": "#", ".cfg": "#", ".conf": "#",
    ".env": "#", ".json": "//", ".html": "//", ".css": "/*", ".scss": "/*",
    ".md": "<!--"
}

BLOCK_COMMENT_END = {".css": "*/", ".scss": "*/"}
HTML_COMMENT_END = {".md": "-->"}

SKIP_DIRS = {".git", ".github", "node_modules", "dist", "build", "__pycache__", ".venv", "venv", ".tox", ".mypy_cache", ".idea", ".vscode"}
SKIP_FILES = {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}

TEXT_FILE_EXTS = set(COMMENT_PREFIX.keys())

def sha256_of_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def make_header(ext: str, project: str, filename: str, version: str, date_str: str) -> str:
    prefix = COMMENT_PREFIX.get(ext, "#")
    if ext in BLOCK_COMMENT_END:
        return f"{prefix} Guru Codex Seal v1.0 ⟡GK⟡ | {GK_TAG} | Oath: {OATH}\n{prefix} Project: {project} | File: {filename} | Author: Kyle × Guru | Version: {version} | Date: {date_str}\n{BLOCK_COMMENT_END[ext]}\n"
    if ext in HTML_COMMENT_END:
        return f"<!-- Guru Codex Seal v1.0 ⟡GK⟡ | {GK_TAG} | Oath: {OATH} -->\n<!-- Project: {project} | File: {filename} | Author: Kyle × Guru | Version: {version} | Date: {date_str} -->\n"
    if ext == ".json":
        return ""
    return f"{prefix} Guru Codex Seal v1.0 ⟡GK⟡ | {GK_TAG} | Oath: {OATH}\n{prefix} Project: {project} | File: {filename} | Author: Kyle × Guru | Version: {version} | Date: {date_str}\n"

def has_gk_header(text: str) -> bool:
    return GK_TAG in "\n".join(text.splitlines()[:5])

def add_header_if_missing(path: Path, project: str, version: str, date_str: str) -> bool:
    ext = path.suffix.lower()
    try:
        data = path.read_bytes()
        text = data.decode('utf-8')
    except Exception:
        return False

    if has_gk_header(text):
        return False

    filename = str(path).replace('\\','/')
    if ext == ".json":
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                if "_comment" in obj and GK_TAG in str(obj.get("_comment","")):
                    return False
                obj["_comment"] = f"Guru Codex Seal v1.0 ⟡GK⟡ | {GK_TAG} | Oath: {OATH} | Project: {project} | File: {filename} | Author: Kyle × Guru | Version: {version} | Date: {date_str}"
                path.write_text(json.dumps(obj, indent=2))
                return True
            return False
        except Exception:
            return False

    header = make_header(ext, project, filename, version, date_str)
    path.write_text(header + text)
    return True

def build_manifest(root: Path, files_meta):
    return {
        "gkci": GK_TAG,
        "oath": OATH,
        "project": root.name,
        "generated_at_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "files": files_meta
    }

def main():
    parser = argparse.ArgumentParser(description="Apply and verify Guru Codex Seal headers.")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--version", default="v1.0.0")
    parser.add_argument("--project", default="Repo")
    parser.add_argument("--check-only", action="store_true", help="Do not modify files, only report")
    parser.add_argument("--manifest", default="gk_manifest.json", help="Where to write the manifest JSON")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    changed = checked = missing = 0
    files_meta = []

    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in SKIP_DIRS:
                continue
        if not p.is_file():
            continue
        if p.name in SKIP_FILES:
            continue

        ext = p.suffix.lower()
        if ext not in TEXT_FILE_EXTS:
            try:
                if p.stat().st_size > 512_000:
                    continue
            except Exception:
                pass
            continue

        try:
            b = p.read_bytes()
            text = b.decode("utf-8")
        except Exception:
            continue

        checked += 1
        present = has_gk_header(text) or (ext == ".json" and '"_comment"' in text and GK_TAG in text)
        if not present:
            missing += 1
            if not args.check_only:
                if add_header_if_missing(p, args.project, args.version, date_str):
                    changed += 1
                    present = True

        files_meta.append({
            "path": str(p.relative_to(root)).replace('\\','/'),
            "ext": ext,
            "header_present": bool(present),
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()
        })

    manifest = build_manifest(root, files_meta)
    Path(args.manifest).write_text(json.dumps(manifest, indent=2))

    print(json.dumps({
        "checked": checked, "changed": changed, "missing": missing,
        "manifest": args.manifest
    }, indent=2))

    if args.check_only and missing > 0:
        sys.exit(2)

if __name__ == "__main__":
    main()
