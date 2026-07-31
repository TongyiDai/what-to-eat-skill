#!/usr/bin/env python3
"""Check local dependencies and state paths without making recommendations."""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import shutil
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state-dir", default=os.environ.get("WHAT_TO_EAT_HOME", "~/.codex/state/what-to-eat"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    skill_root = Path(__file__).resolve().parent.parent
    state_dir = Path(args.state_dir).expanduser()
    compile_ok = True
    try:
        py_compile.compile(str(skill_root / "scripts" / "meal_memory.py"), doraise=True)
    except py_compile.PyCompileError:
        compile_ok = False
    scheduler = "host-provided automation"
    result = {
        "ok": compile_ok,
        "skill_root": str(skill_root),
        "required": {"python3": True, "memory_script": compile_ok},
        "state": {"path": str(state_dir), "exists": state_dir.exists(), "writable": os.access(state_dir, os.W_OK) if state_dir.exists() else None},
        "optional": {"recurring_automation": scheduler},
        "next": "run snapshot with the intended --state-dir" if compile_ok else "repair meal_memory.py before use",
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        for key, value in result.items():
            print(f"{key}={json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else value}")
    return 0 if compile_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
