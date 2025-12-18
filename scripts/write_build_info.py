#!/usr/bin/env python3
"""
Generate build_info.json for showing exact build version/timestamp in UI.

This is intended to be run during build (before PyInstaller).
The file is not meant to be committed.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime


def _run(cmd: list[str]) -> str | None:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
        return out.strip()
    except Exception:
        return None


def main() -> int:
    project_root = os.getcwd()
    tag = _run(["git", "describe", "--tags", "--always"])
    commit = _run(["git", "rev-parse", "--short", "HEAD"])

    data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "git_tag": tag or "unknown",
        "git_commit": commit or "unknown",
    }

    out_path = os.path.join(project_root, "build_info.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


