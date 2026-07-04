#!/usr/bin/env python3
"""Validate skills against the Agent Skills spec (agentskills.io/specification)
plus this repo's own limits. Standard library only."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_BODY_LINES = 500
errors = []


def err(path, msg):
    errors.append(f"{path}: {msg}")


skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
if not skill_dirs:
    err("skills/", "no skill directories found")

for d in skill_dirs:
    md = d / "SKILL.md"
    if not md.exists():
        err(d, "missing SKILL.md")
        continue
    text = md.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        err(md, "missing YAML frontmatter")
        continue
    fm, body = m.groups()

    def field(key):
        fm_match = re.search(rf"^{key}: (.+)$", fm, re.M)
        return fm_match.group(1).strip() if fm_match else None

    name = field("name")
    if not name:
        err(md, "missing required field: name")
    else:
        if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
            err(md, f"invalid name {name!r} (1-64 chars, lowercase alphanumerics, single hyphens)")
        if name != d.name:
            err(md, f"name {name!r} does not match directory {d.name!r}")

    desc = field("description")
    if not desc:
        err(md, "missing required field: description")
    elif len(desc) > 1024:
        err(md, f"description is {len(desc)} chars; spec maximum is 1024")

    compat = field("compatibility")
    if compat and len(compat) > 500:
        err(md, f"compatibility is {len(compat)} chars; spec maximum is 500")

    body_lines = body.count("\n") + 1
    if body_lines > MAX_BODY_LINES:
        err(md, f"body is {body_lines} lines; keep under {MAX_BODY_LINES}")

    for ref in re.findall(r"\]\((?!https?://|#|mailto:)([^)\s]+?)(?:#[^)]*)?\)", body):
        if not (d / ref).exists():
            err(md, f"broken relative link: {ref}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"OK: {len(skill_dirs)} skill(s) valid")
