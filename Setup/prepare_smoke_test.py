#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Config not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def _resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def _require(data: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise SystemExit(f"Missing required keys: {', '.join(missing)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a clean runtime workspace for a canonical DrawForge smoke test.")
    parser.add_argument("--config", required=True, help="Path to a smoke-test config JSON")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing runtime smoke-test workspace")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config_dir = config_path.parent
    config = _load_json(config_path)

    _require(config, "job_name", "task", "paths", "smoke_test")
    _require(config["task"], "input_png", "final_vsdx_name")
    _require(config["paths"], "input_dir", "preview_dir", "final_vsdx_dir", "workspace_root")
    _require(config["smoke_test"], "source_job")

    source_job = str(config["smoke_test"]["source_job"])
    source_workspace = (REPO_ROOT / "Setup" / "jobs" / source_job).resolve()
    if not source_workspace.is_dir():
        raise SystemExit(f"Source benchmark workspace not found: {source_workspace}")

    input_dir = _resolve(config_dir, config["paths"]["input_dir"])
    workspace_root = _resolve(config_dir, config["paths"]["workspace_root"])
    preview_dir = (_resolve(config_dir, config["paths"]["preview_dir"]) / config["job_name"]).resolve()
    final_vsdx = (_resolve(config_dir, config["paths"]["final_vsdx_dir"]) / config["task"]["final_vsdx_name"]).resolve()
    target_workspace = (workspace_root / config["job_name"]).resolve()

    input_png = (input_dir / config["task"]["input_png"]).resolve()
    if not input_png.is_file():
        raise SystemExit(f"Input PNG not found: {input_png}")

    required_files = ["analysis.json", "plan.json", "drawdsl.json"]
    missing = [name for name in required_files if not (source_workspace / name).is_file()]
    if missing:
        raise SystemExit(f"Source benchmark workspace is missing: {', '.join(missing)}")

    if target_workspace.exists():
        if not args.force:
            raise SystemExit(
                f"Target workspace already exists: {target_workspace}\n"
                "Re-run with --force to replace it."
            )
        shutil.rmtree(target_workspace)

    target_workspace.mkdir(parents=True, exist_ok=True)
    (target_workspace / "reviews").mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)
    final_vsdx.parent.mkdir(parents=True, exist_ok=True)

    for name in required_files:
        shutil.copy2(source_workspace / name, target_workspace / name)

    summary = {
        "config_path": str(config_path),
        "source_job": source_job,
        "input_png": str(input_png),
        "target_workspace": str(target_workspace),
        "preview_dir": str(preview_dir),
        "final_vsdx": str(final_vsdx),
        "next_steps": [
            f"python Setup\\run_draw_job.py --config {args.config}",
            f"python Setup\\execute_drawdsl.py --config {args.config} --round 1 --save-final",
        ],
        "expected_outputs": [
            str(preview_dir / "round-01.png"),
            str(final_vsdx),
        ],
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
