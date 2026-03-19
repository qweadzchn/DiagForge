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
    parser = argparse.ArgumentParser(description="Validate and normalize a png2vsdx draw job config.")
    parser.add_argument("--config", default="Setup/draw-job.local.json", help="Path to job config JSON")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config_dir = config_path.parent
    repo_root = config_dir.parent

    config = _load_json(config_path)
    _require(config, "job_name", "task", "paths", "bridge", "execution")
    _require(config["task"], "input_png", "final_vsdx_name")
    _require(config["paths"], "input_dir", "preview_dir", "final_vsdx_dir")
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

    input_dir = _resolve(config_dir, config["paths"]["input_dir"])
    preview_root = _resolve(config_dir, config["paths"]["preview_dir"])
    final_vsdx_dir = _resolve(config_dir, config["paths"]["final_vsdx_dir"])

    input_path = (input_dir / config["task"]["input_png"]).resolve()
    final_vsdx_path = (final_vsdx_dir / config["task"]["final_vsdx_name"]).resolve()
    preview_dir = (preview_root / config["job_name"]).resolve()

    input_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)
    final_vsdx_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.is_file():
        raise SystemExit(
            "Input PNG not found. "
            f"Expected {input_path}. Put the image under InputPNG/ and update task.input_png."
        )

    token_env = config["bridge"]["token_env"]
    token = os.environ.get(token_env)
    probe = _probe_bridge(config["bridge"]["base_url"].rstrip("/"), token)

    summary = {
        "repo_root": str(repo_root),
        "config_path": str(config_path),
        "job_name": config["job_name"],
        "input_png": str(input_path),
        "preview_dir": str(preview_dir),
        "final_vsdx": str(final_vsdx_path),
        "execution": config["execution"],
        "bridge": probe,
    }

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
