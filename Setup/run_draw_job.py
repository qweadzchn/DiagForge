#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Config not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def _require(data: dict[str, Any], *keys: str) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        raise SystemExit(f"Missing required keys: {', '.join(missing)}")


def _resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def _write_json_if_missing(path: Path, payload: dict[str, Any]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _http_json(method: str, url: str, payload: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _probe_bridge(base_url: str, token: str | None) -> dict[str, Any]:
    out: dict[str, Any] = {"base_url": base_url, "token_env_present": bool(token)}

    try:
        out["health"] = _http_json("GET", f"{base_url}/health")
    except Exception as exc:
        out["health_error"] = str(exc)
        return out

    try:
        out["ping_visio"] = _http_json("POST", f"{base_url}/ping_visio", {}, token)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        out["ping_visio_error"] = f"HTTP {exc.code}: {detail}"
    except Exception as exc:
        out["ping_visio_error"] = str(exc)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate and bootstrap a DrawForge draw job workspace.")
    parser.add_argument("--config", default="Setup/draw-job.local.json", help="Path to job config JSON")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config_dir = config_path.parent
    repo_root = config_dir.parent

    config = _load_json(config_path)
    _require(config, "job_name", "task", "paths", "bridge", "execution")
    _require(config["task"], "input_png", "final_vsdx_name")
    _require(config["paths"], "input_dir", "preview_dir", "final_vsdx_dir", "workspace_root")
    _require(config["bridge"], "base_url", "token_env")
    _require(
        config["execution"],
        "max_rounds",
        "save_intermediate_vsdx",
        "export_preview_each_round",
        "clear_session_after_round",
        "record_lessons_each_round",
        "keep_final_vsdx",
    )

    run_mode = str(config.get("run_mode", "operation"))
    if run_mode not in {"development", "operation"}:
        raise SystemExit("run_mode must be 'development' or 'operation'")

    input_dir = _resolve(config_dir, config["paths"]["input_dir"])
    preview_root = _resolve(config_dir, config["paths"]["preview_dir"])
    final_vsdx_dir = _resolve(config_dir, config["paths"]["final_vsdx_dir"])
    workspace_root = _resolve(config_dir, config["paths"]["workspace_root"])

    input_path = (input_dir / config["task"]["input_png"]).resolve()
    final_vsdx_path = (final_vsdx_dir / config["task"]["final_vsdx_name"]).resolve()
    preview_dir = (preview_root / config["job_name"]).resolve()
    workspace_dir = (workspace_root / config["job_name"]).resolve()
    reviews_dir = (workspace_dir / "reviews").resolve()
    analysis_path = (workspace_dir / "analysis.json").resolve()
    plan_path = (workspace_dir / "plan.json").resolve()
    drawdsl_path = (workspace_dir / "drawdsl.json").resolve()
    run_summary_path = (workspace_dir / "run-summary.json").resolve()

    task_goal = str(config["task"].get("goal") or config["task"].get("description") or "")
    diagram_hint = str(config["task"].get("diagram_hint") or "")
    normalized_execution = {
        **config["execution"],
        "stop_when_satisfied": bool(config["execution"].get("stop_when_satisfied", True)),
        "write_round_review_each_round": bool(config["execution"].get("write_round_review_each_round", True)),
    }

    input_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)
    final_vsdx_dir.mkdir(parents=True, exist_ok=True)
    reviews_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.is_file():
        raise SystemExit(
            "Input PNG not found. "
            f"Expected {input_path}. Put the image under InputReference/ and update task.input_png."
        )

    _write_json_if_missing(
        analysis_path,
        {
            "job_name": config["job_name"],
            "input_png": str(input_path),
            "task_goal": task_goal,
            "diagram_hint": diagram_hint,
            "diagram_family": "unknown",
            "flow_direction": "unknown",
            "regions": [],
            "elements": [],
            "style_observations": [],
            "layout_risks": [],
            "open_questions": [],
            "recommended_drawskills": [],
            "recommended_visioskills": [],
            "next_step": "plannerskills: analyze the source figure before writing plan.json",
        },
    )
    _write_json_if_missing(
        plan_path,
        {
            "job_name": config["job_name"],
            "goal": task_goal,
            "selected_drawskills": [],
            "selected_visioskills": [],
            "drawing_strategy": [],
            "layout_constraints": [],
            "style_constraints": [],
            "round_objectives": [],
            "handoff_to_drawskills": [],
            "handoff_to_visioskills": [],
        },
    )
    _write_json_if_missing(
        drawdsl_path,
        {
            "version": "0.1",
            "skill_id": "",
            "canvas": {"unit": "in"},
            "nodes": [],
            "edges": [],
        },
    )

    token_env = config["bridge"]["token_env"]
    token = os.environ.get(token_env)
    probe = _probe_bridge(config["bridge"]["base_url"].rstrip("/"), token)

    summary = {
        "repo_root": str(repo_root),
        "config_path": str(config_path),
        "run_mode": run_mode,
        "job_name": config["job_name"],
        "input_png": str(input_path),
        "task_goal": task_goal,
        "diagram_hint": diagram_hint,
        "preview_dir": str(preview_dir),
        "final_vsdx": str(final_vsdx_path),
        "workspace": {
            "dir": str(workspace_dir),
            "analysis_json": str(analysis_path),
            "plan_json": str(plan_path),
            "drawdsl_json": str(drawdsl_path),
            "reviews_dir": str(reviews_dir),
            "run_summary_json": str(run_summary_path),
        },
        "execution": normalized_execution,
        "workflow": {
            "layer_order": ["Setup", "plannerskills", "drawskills", "visioskills", "learningskills"],
            "artifact_chain": [
                "run-summary.json",
                "analysis.json",
                "plan.json",
                "drawdsl.json",
                "preview PNG / final VSDX",
                "reviews/round-*.json",
                "agent/skills/learningskills/lessons/*.md",
            ],
        },
        "bridge": probe,
    }

    run_summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if "health_error" in probe:
        raise SystemExit("Bridge health check failed.")
    if "ping_visio_error" in probe:
        raise SystemExit("Visio preflight failed. Fix token/runtime before drawing.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
