#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from drawskills.layout_postprocess import (
    apply_layout_postprocess,
    estimate_text_box as _layout_estimate_text_box,
    expected_text_angle_deg,
    font_size_for_node as _layout_font_size_for_node,
    infer_container_memberships,
    padding_x as _layout_padding_x,
    padding_y as _layout_padding_y,
)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def _resolve(base: Path, raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = (base / path).resolve()
    return path


def _request_json(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout_s: float = 60.0,
) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _download_file(url: str, target: Path, token: str | None = None, timeout_s: float = 120.0) -> None:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=timeout_s) as resp:
        target.write_bytes(resp.read())


def _shape_type(raw: str | None) -> str:
    shape = (raw or "rectangle").strip().lower()
    if shape in {"rectangle", "rect", "rounded_rectangle", "rounded-rectangle", "container", "label"}:
        return "Rectangle"
    if shape in {"circle", "ellipse", "oval"}:
        return "Circle"
    if shape == "line":
        return "Line"
    return "Rectangle"


def _rgb(value: Any) -> list[int] | None:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 3:
        raise SystemExit(f"Expected RGB list of length 3, got: {value!r}")
    return [int(value[0]), int(value[1]), int(value[2])]


def _font_size_for_node(node: dict[str, Any], text_policy: dict[str, Any]) -> float | None:
    return _layout_font_size_for_node(node, text_policy)


def _padding_x(node: dict[str, Any]) -> float:
    return _layout_padding_x(node)


def _padding_y(node: dict[str, Any]) -> float:
    return _layout_padding_y(node)


def _estimate_text_box(node: dict[str, Any], text_policy: dict[str, Any]) -> tuple[float, float]:
    return _layout_estimate_text_box(node, text_policy)


def _apply_text_box_coupling(drawdsl: dict[str, Any]) -> None:
    apply_layout_postprocess(drawdsl)


def _is_label_node(node: dict[str, Any]) -> bool:
    return str(node.get("shape", "")).lower() == "label"


def _normalize_node_styles(drawdsl: dict[str, Any]) -> None:
    for node in drawdsl.get("nodes", []):
        style = node.setdefault("style", {})
        if _is_label_node(node):
            style.setdefault("line_pattern", 0)
            style.setdefault("fill_pattern", 0)
            style.setdefault("shape_permeable_x", True)
            style.setdefault("shape_permeable_y", True)


def _default_edge_style(
    edge: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    from_pin: tuple[float, float],
    to_pin: tuple[float, float],
) -> dict[str, Any]:
    semantic = str(edge.get("semantic", "")).lower()
    style = dict(edge.get("style", {}))
    colored_emphasis = {"detect_link", "emphasized_downlink", "training_loss", "io_cross_stage"}
    reference_links = {"detail_panel_link", "detail_skip", "external_example", "io_external"}
    if semantic in colored_emphasis:
        default_weight = 1.35
    elif semantic in reference_links:
        default_weight = 1.0
    else:
        default_weight = 1.15
    src = nodes_by_id[str(edge["from"])]
    dst = nodes_by_id[str(edge["to"])]
    dx = float(dst["x"]) - float(src["x"])
    dy = float(dst["y"]) - float(src["y"])

    if "line_weight_pt" not in style:
        style["line_weight_pt"] = default_weight
    else:
        style["line_weight_pt"] = max(float(style["line_weight_pt"]), default_weight)

    if semantic in {"detail_panel_link", "detail_skip"}:
        style.setdefault("end_arrow", 0)
        style.setdefault("end_arrow_size", 0)
    else:
        style.setdefault("end_arrow", 13)
        style.setdefault("end_arrow_size", 2)

    if semantic in reference_links and "line_pattern" not in style:
        style["line_pattern"] = 2
    if semantic in colored_emphasis and "line_rgb" not in style:
        style["line_rgb"] = [243, 88, 24]
    elif semantic in reference_links and "line_rgb" not in style:
        style["line_rgb"] = [130, 130, 130]
    elif "line_rgb" not in style:
        style["line_rgb"] = [35, 35, 35]

    route_intent = _resolve_route_intent(edge, nodes_by_id, from_pin, to_pin)
    if route_intent == "curved":
        style.setdefault("shape_route_style", 16)
        style.setdefault("con_line_route_ext", 2)
    elif route_intent == "orthogonal":
        style.setdefault("shape_route_style", 2)
        style.setdefault("con_line_route_ext", 1)
    elif route_intent in {"straight", "straight_horizontal", "straight_vertical"}:
        style.setdefault("shape_route_style", 2)
        style.setdefault("con_line_route_ext", 1)
    else:
        style.setdefault("shape_route_style", 2)
        style.setdefault("con_line_route_ext", 2 if semantic == "detail_skip" else 1)

    return style


def _rect_bounds(node: dict[str, Any]) -> tuple[float, float, float, float]:
    x = float(node["x"])
    y = float(node["y"])
    width = float(node["width"])
    height = float(node["height"])
    return x - width / 2, y - height / 2, x + width / 2, y + height / 2


def _bounds_overlap(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> tuple[float, float]:
    overlap_x = min(a[2], b[2]) - max(a[0], b[0])
    overlap_y = min(a[3], b[3]) - max(a[1], b[1])
    return max(0.0, overlap_x), max(0.0, overlap_y)


def _detect_node_overlaps(nodes: list[dict[str, Any]], tolerance: float = 0.03) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    candidates = [node for node in nodes if str(node.get("shape", "")).lower() != "container"]
    for index, left in enumerate(candidates):
        left_bounds = _rect_bounds(left)
        for right in candidates[index + 1 :]:
            overlap_x, overlap_y = _bounds_overlap(left_bounds, _rect_bounds(right))
            if overlap_x > tolerance and overlap_y > tolerance:
                findings.append(
                    {
                        "left": str(left["id"]),
                        "right": str(right["id"]),
                        "overlap_x": round(overlap_x, 3),
                        "overlap_y": round(overlap_y, 3),
                    }
                )
    return findings


def _detect_container_violations(nodes: list[dict[str, Any]], tolerance: float = 0.02) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    nodes_by_id = {str(node["id"]): node for node in nodes}
    memberships, _ = infer_container_memberships(nodes)
    for container_id, member_ids in memberships.items():
        container = nodes_by_id.get(container_id)
        if not container:
            continue
        container_bounds = _rect_bounds(container)
        for node_id in member_ids:
            node = nodes_by_id.get(node_id)
            if not node:
                continue
            if str(node.get("role", "")).lower() == "title":
                continue
            node_bounds = _rect_bounds(node)
            if (
                node_bounds[0] < container_bounds[0] - tolerance
                or node_bounds[1] < container_bounds[1] - tolerance
                or node_bounds[2] > container_bounds[2] + tolerance
                or node_bounds[3] > container_bounds[3] + tolerance
            ):
                findings.append(
                    {
                        "container": str(container["id"]),
                        "node": str(node["id"]),
                    }
                )
    return findings


def _detect_opaque_labels(nodes: list[dict[str, Any]], node_descriptions: dict[str, dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    for node in nodes:
        if not _is_label_node(node):
            continue
        described = node_descriptions.get(str(node["id"]), {})
        if str(described.get("line_pattern") or "") not in {"0", "0.0"} or str(described.get("fill_pattern") or "") not in {"0", "0.0"}:
            findings.append(str(node["id"]))
    return findings


def _expected_connector_axis(
    edge: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    from_pin: tuple[float, float],
    to_pin: tuple[float, float],
) -> str | None:
    route_intent = _resolve_route_intent(edge, nodes_by_id, from_pin, to_pin)
    if route_intent == "curved":
        return None
    if route_intent == "straight_horizontal":
        return "horizontal"
    if route_intent == "straight_vertical":
        return "vertical"
    return _axis_from_geometry(edge, nodes_by_id, from_pin, to_pin)


def _axis_from_geometry(
    edge: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    from_pin: tuple[float, float],
    to_pin: tuple[float, float],
) -> str | None:
    src = nodes_by_id[str(edge["from"])]
    dst = nodes_by_id[str(edge["to"])]
    dx = abs(float(dst["x"]) - float(src["x"]))
    dy = abs(float(dst["y"]) - float(src["y"]))
    if dx >= dy * 1.25 and abs(from_pin[1] - to_pin[1]) < 0.05:
        return "horizontal"
    if dy >= dx * 1.25 and abs(from_pin[0] - to_pin[0]) < 0.05:
        return "vertical"
    return None


def _resolve_route_intent(
    edge: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    from_pin: tuple[float, float],
    to_pin: tuple[float, float],
) -> str:
    explicit = str(edge.get("route_intent") or "").strip().lower()
    if explicit in {"auto", "straight", "straight_horizontal", "straight_vertical", "orthogonal", "curved"}:
        if explicit != "auto":
            return explicit

    semantic = str(edge.get("semantic", "")).lower()
    if semantic == "detail_skip":
        return "curved"

    axis = _axis_from_geometry(edge, nodes_by_id, from_pin, to_pin)
    if axis == "horizontal":
        return "straight_horizontal"
    if axis == "vertical":
        return "straight_vertical"
    return "orthogonal"


def _assess_edge_geometry(
    edge: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    described: dict[str, Any],
    from_pin: tuple[float, float],
    to_pin: tuple[float, float],
) -> list[str]:
    findings: list[str] = []
    expected_axis = _expected_connector_axis(edge, nodes_by_id, from_pin, to_pin)
    width = float(described.get("width") or 0.0)
    height = float(described.get("height") or 0.0)
    if expected_axis == "horizontal" and height > 0.35:
        findings.append(f"connector_height_too_large:{height:.3f}")
    if expected_axis == "vertical" and width > 0.35:
        findings.append(f"connector_width_too_large:{width:.3f}")
    semantic = str(edge.get("semantic", "")).lower()
    if semantic in {"detail_panel_link", "detail_skip"} and max(width, height) > 3.0:
        findings.append(f"reference_link_span_too_large:{width:.3f}x{height:.3f}")
    return findings


def _node_bounds(nodes: list[dict[str, Any]]) -> tuple[float, float, float, float] | None:
    if not nodes:
        return None
    min_left = min(float(node["x"]) - float(node["width"]) / 2 for node in nodes)
    min_bottom = min(float(node["y"]) - float(node["height"]) / 2 for node in nodes)
    max_right = max(float(node["x"]) + float(node["width"]) / 2 for node in nodes)
    max_top = max(float(node["y"]) + float(node["height"]) / 2 for node in nodes)
    return min_left, min_bottom, max_right, max_top


def _shift_nodes(drawdsl: dict[str, Any], shift_x: float, shift_y: float) -> None:
    nodes = drawdsl.get("nodes", [])
    if not nodes:
        return

    if shift_x == 0.0 and shift_y == 0.0:
        return

    for node in nodes:
        node["x"] = round(float(node["x"]) + shift_x, 3)
        node["y"] = round(float(node["y"]) + shift_y, 3)


def _clamp_nodes_to_page(drawdsl: dict[str, Any], page_width_in: float, page_height_in: float, margin: float = 0.2) -> None:
    bounds = _node_bounds(drawdsl.get("nodes", []))
    if bounds is None:
        return

    min_left, min_bottom, max_right, max_top = bounds

    shift_x = 0.0
    shift_y = 0.0
    if min_left < margin:
        shift_x = margin - min_left
    elif max_right > page_width_in - margin:
        shift_x = (page_width_in - margin) - max_right

    if min_bottom < margin:
        shift_y = margin - min_bottom
    elif max_top > page_height_in - margin:
        shift_y = (page_height_in - margin) - max_top

    _shift_nodes(drawdsl, shift_x, shift_y)


def _prepare_page(
    drawdsl: dict[str, Any],
    *,
    base_url: str,
    token: str,
    job_name: str,
    round_no: int,
    session_id: str,
    page_info: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    canvas = drawdsl.get("canvas", {})
    margin = float(canvas.get("page_margin_in", 0.35) or 0.35)
    auto_resize = bool(canvas.get("auto_resize_to_content", True))
    bounds = _node_bounds(drawdsl.get("nodes", []))
    if bounds is None:
        return page_info["data"], None

    min_left, min_bottom, max_right, max_top = bounds
    content_width = max_right - min_left
    content_height = max_top - min_bottom
    page_data = dict(page_info["data"])
    has_explicit_width = "page_width_in" in canvas and canvas.get("page_width_in") is not None
    has_explicit_height = "page_height_in" in canvas and canvas.get("page_height_in") is not None
    target_width = float(canvas["page_width_in"]) if has_explicit_width else float(page_data["page_width_in"])
    target_height = float(canvas["page_height_in"]) if has_explicit_height else float(page_data["page_height_in"])
    if auto_resize:
        fitted_width = content_width + 2 * margin
        fitted_height = content_height + 2 * margin
        target_width = max(target_width, fitted_width) if has_explicit_width else fitted_width
        target_height = max(target_height, fitted_height) if has_explicit_height else fitted_height

    page_setup: dict[str, Any] | None = None
    if abs(target_width - float(page_data["page_width_in"])) > 0.01 or abs(target_height - float(page_data["page_height_in"])) > 0.01:
        page_setup = _request_json(
            "POST",
            f"{base_url}/page/setup",
            payload={
                "request_id": f"{job_name}-round-{round_no:02d}-page-setup",
                "session_id": session_id,
                "page_name": canvas.get("page_name"),
                "page_width_in": round(target_width, 3),
                "page_height_in": round(target_height, 3),
            },
            token=token,
        )
        page_data = dict(page_setup["data"])

    _shift_nodes(drawdsl, margin - min_left, margin - min_bottom)
    if not auto_resize:
        _clamp_nodes_to_page(drawdsl, float(page_data["page_width_in"]), float(page_data["page_height_in"]), margin=margin)
    return page_data, page_setup


def _normalize_pin(raw: Any) -> tuple[float, float] | None:
    if not isinstance(raw, dict):
        return None
    x = raw.get("x_percent")
    y = raw.get("y_percent")
    if x is None or y is None:
        return None
    return max(0.0, min(1.0, float(x))), max(0.0, min(1.0, float(y)))


def _infer_edge_pins(edge: dict[str, Any], nodes_by_id: dict[str, dict[str, Any]]) -> tuple[tuple[float, float], tuple[float, float]]:
    explicit_from = _normalize_pin(edge.get("from_pin"))
    explicit_to = _normalize_pin(edge.get("to_pin"))
    if explicit_from and explicit_to:
        return explicit_from, explicit_to

    src = nodes_by_id[str(edge["from"])]
    dst = nodes_by_id[str(edge["to"])]
    dx = float(dst["x"]) - float(src["x"])
    dy = float(dst["y"]) - float(src["y"])
    semantic = str(edge.get("semantic", "")).lower()
    explicit_route_intent = str(edge.get("route_intent") or "").strip().lower()

    if explicit_from is None or explicit_to is None:
        if explicit_route_intent == "straight_horizontal":
            inferred_from = (1.0, 0.5) if dx >= 0 else (0.0, 0.5)
            inferred_to = (0.0, 0.5) if dx >= 0 else (1.0, 0.5)
        elif explicit_route_intent == "straight_vertical":
            inferred_from = (0.5, 1.0) if dy >= 0 else (0.5, 0.0)
            inferred_to = (0.5, 0.0) if dy >= 0 else (0.5, 1.0)
        elif abs(dx) >= abs(dy) * 1.25:
            inferred_from = (1.0, 0.5) if dx >= 0 else (0.0, 0.5)
            inferred_to = (0.0, 0.5) if dx >= 0 else (1.0, 0.5)
        elif abs(dy) >= abs(dx) * 1.25 or semantic in {"emphasized_downlink", "detect_link", "training_loss"}:
            inferred_from = (0.5, 1.0) if dy >= 0 else (0.5, 0.0)
            inferred_to = (0.5, 0.0) if dy >= 0 else (0.5, 1.0)
        elif dy < 0:
            inferred_from = (0.5, 0.0)
            inferred_to = (0.5, 1.0)
        else:
            inferred_from = (1.0, 0.5) if dx >= 0 else (0.0, 0.5)
            inferred_to = (0.0, 0.5) if dx >= 0 else (1.0, 0.5)
    else:
        inferred_from = explicit_from
        inferred_to = explicit_to

    return explicit_from or inferred_from, explicit_to or inferred_to


def _parse_measurement_pt(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text.split()[0])
    except (ValueError, IndexError):
        return None


def _normalize_angle_deg(value: float) -> float:
    normalized = value % 360.0
    if normalized > 180.0:
        normalized -= 360.0
    return normalized


def _verify_node_style(node: dict[str, Any], text_policy: dict[str, Any], described: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    style = dict(node.get("style", {}))
    expected_font = str(style.get("font_name") or text_policy.get("font_name") or "Times New Roman")
    actual_font = str(described.get("font_formula") or "")
    if expected_font.lower() not in actual_font.lower():
        mismatches.append(f"font expected {expected_font!r}, got {actual_font!r}")

    expected_size = _font_size_for_node(node, text_policy)
    actual_size = _parse_measurement_pt(described.get("font_size_pt"))
    if expected_size is not None and actual_size is not None and abs(float(expected_size) - actual_size) > 0.35:
        mismatches.append(f"font_size expected {expected_size}pt, got {actual_size}pt")

    expected_angle = expected_text_angle_deg(node, text_policy)
    actual_angle = _parse_measurement_pt(described.get("txt_angle_deg"))
    if expected_angle is not None and actual_angle is not None:
        if abs(_normalize_angle_deg(expected_angle) - _normalize_angle_deg(actual_angle)) > 2.0:
            mismatches.append(f"text_angle expected {expected_angle}deg, got {actual_angle}deg")

    if "line_weight_pt" in style:
        actual_line_weight = _parse_measurement_pt(described.get("line_weight_pt"))
        if actual_line_weight is not None and abs(float(style["line_weight_pt"]) - actual_line_weight) > 0.2:
            mismatches.append(f"line_weight expected {style['line_weight_pt']}pt, got {actual_line_weight}pt")
    if _is_label_node(node):
        if style.get("line_pattern", 0) == 0 and str(described.get("line_pattern") or "") not in {"0", "0.0"}:
            mismatches.append(f"line_pattern expected 0, got {described.get('line_pattern')!r}")
        if style.get("fill_pattern", 0) == 0 and str(described.get("fill_pattern") or "") not in {"0", "0.0"}:
            mismatches.append(f"fill_pattern expected 0, got {described.get('fill_pattern')!r}")
        if style.get("shape_permeable_x") is True and str(described.get("shape_permeable_x") or "").upper() != "TRUE":
            mismatches.append(f"shape_permeable_x expected TRUE, got {described.get('shape_permeable_x')!r}")
        if style.get("shape_permeable_y") is True and str(described.get("shape_permeable_y") or "").upper() != "TRUE":
            mismatches.append(f"shape_permeable_y expected TRUE, got {described.get('shape_permeable_y')!r}")
    return mismatches


def _verify_edge_style(style: dict[str, Any], described: dict[str, Any]) -> list[str]:
    mismatches: list[str] = []
    if "line_weight_pt" in style:
        actual_line_weight = _parse_measurement_pt(described.get("line_weight_pt"))
        if actual_line_weight is not None and abs(float(style["line_weight_pt"]) - actual_line_weight) > 0.2:
            mismatches.append(f"line_weight expected {style['line_weight_pt']}pt, got {actual_line_weight}pt")

    for key in ("begin_arrow", "end_arrow", "begin_arrow_size", "end_arrow_size", "shape_route_style", "con_line_route_ext"):
        if key in style and style[key] is not None:
            actual_value = str(described.get(key) or "")
            expected_value = str(style[key])
            if actual_value != expected_value:
                mismatches.append(f"{key} expected {expected_value}, got {actual_value!r}")
    return mismatches


def _build_colors_payload(session_id: str, shape_id: int, style: dict[str, Any]) -> dict[str, Any] | None:
    payload: dict[str, Any] = {"session_id": session_id, "shape_id": shape_id}
    applied = False

    for key in (
        "line_weight_pt",
        "line_pattern",
        "fill_pattern",
        "rounding",
        "begin_arrow",
        "end_arrow",
        "begin_arrow_size",
        "end_arrow_size",
        "shape_route_style",
        "con_line_route_ext",
        "shape_permeable_x",
        "shape_permeable_y",
    ):
        if key in style and style[key] is not None:
            payload[key] = style[key]
            applied = True

    line_rgb = _rgb(style.get("line_rgb"))
    fill_rgb = _rgb(style.get("fill_rgb"))
    if line_rgb is not None:
        payload["line_rgb"] = line_rgb
        applied = True
    if fill_rgb is not None:
        payload["fill_rgb"] = fill_rgb
        applied = True

    return payload if applied else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Execute DrawDSL against the DiagForge Visio bridge.")
    parser.add_argument("--config", default="Setup/draw-job.local.json", help="Path to draw job config JSON")
    parser.add_argument("--round", type=int, required=True, help="Round number for preview naming and review tracking")
    parser.add_argument("--save-final", action="store_true", help="Save the resulting VSDX to the configured final path")
    parser.add_argument("--visible", action="store_true", help="Open the Visio session visibly during execution")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    config_dir = config_path.parent
    config = _load_json(config_path)

    preview_root = _resolve(config_dir, config["paths"]["preview_dir"])
    final_vsdx_dir = _resolve(config_dir, config["paths"]["final_vsdx_dir"])
    workspace_root = _resolve(config_dir, config["paths"]["workspace_root"])

    job_name = str(config["job_name"])
    preview_dir = (preview_root / job_name).resolve()
    preview_dir.mkdir(parents=True, exist_ok=True)
    final_vsdx_path = (final_vsdx_dir / config["task"]["final_vsdx_name"]).resolve()
    workspace_dir = (workspace_root / job_name).resolve()
    drawdsl_path = (workspace_dir / "drawdsl.json").resolve()
    execution_log_path = (workspace_dir / "reviews" / f"round-{args.round:02d}-execution.json").resolve()

    drawdsl = _load_json(drawdsl_path)
    _normalize_node_styles(drawdsl)
    _apply_text_box_coupling(drawdsl)
    text_policy = drawdsl.get("text_policy", {})

    token_env = str(config["bridge"]["token_env"])
    token = os.environ.get(token_env)
    if not token:
        raise SystemExit(f"Environment variable {token_env} is not set")

    base_url = str(config["bridge"]["base_url"]).rstrip("/")
    _request_json("GET", f"{base_url}/health")
    _request_json("POST", f"{base_url}/ping_visio", payload={}, token=token)

    create_payload = {
        "request_id": f"{job_name}-round-{args.round:02d}-session-create",
        "visible": bool(args.visible),
    }
    session = _request_json("POST", f"{base_url}/session/create", payload=create_payload, token=token)
    session_id = str(session["session_id"])
    page_info_before = _request_json(
        "POST",
        f"{base_url}/page/info",
        payload={
            "request_id": f"{job_name}-round-{args.round:02d}-page-info",
            "session_id": session_id,
            "page_name": drawdsl.get("canvas", {}).get("page_name"),
        },
        token=token,
    )
    page_info, page_setup = _prepare_page(
        drawdsl,
        base_url=base_url,
        token=token,
        job_name=job_name,
        round_no=args.round,
        session_id=session_id,
        page_info=page_info_before,
    )

    shape_ids: dict[str, int] = {}
    created_nodes: list[dict[str, Any]] = []
    created_edges: list[dict[str, Any]] = []
    nodes_by_id = {str(node["id"]): node for node in drawdsl.get("nodes", [])}
    node_descriptions: dict[str, dict[str, Any]] = {}
    style_verification: dict[str, Any] = {
        "checked_nodes": 0,
        "checked_edges": 0,
        "mismatches": [],
    }
    geometry_quality: dict[str, Any] = {
        "edge_geometry_warnings": [],
    }

    try:
        for index, node in enumerate(drawdsl.get("nodes", []), start=1):
            node_id = str(node["id"])
            add_payload = {
                "request_id": f"{job_name}-round-{args.round:02d}-node-{index:03d}-add",
                "session_id": session_id,
                "shape_type": _shape_type(node.get("shape")),
                "x": float(node["x"]),
                "y": float(node["y"]),
                "width": float(node["width"]),
                "height": float(node["height"]),
                "text": node.get("text"),
            }
            added = _request_json("POST", f"{base_url}/shape/add", payload=add_payload, token=token)
            shape_id = int(added["data"]["shape_id"])
            shape_ids[node_id] = shape_id
            created_nodes.append({"node_id": node_id, "shape_id": shape_id})

            style = dict(node.get("style", {}))
            font_payload = {
                "request_id": f"{job_name}-round-{args.round:02d}-node-{index:03d}-font",
                "session_id": session_id,
                "shape_id": shape_id,
                "font_name": style.get("font_name") or text_policy.get("font_name") or "Times New Roman",
                "font_size_pt": _font_size_for_node(node, text_policy),
                "font_rgb": _rgb(style.get("font_rgb")) or [20, 20, 20],
                "text_direction": node.get("_resolved_text_direction") or node.get("text_direction"),
                "text_angle_deg": node.get("_resolved_text_angle_deg"),
            }
            if node.get("text") is not None:
                font_payload["text"] = node.get("text")
            _request_json("POST", f"{base_url}/shape/set_text_style", payload=font_payload, token=token)

            colors_payload = _build_colors_payload(session_id, shape_id, style)
            if colors_payload:
                colors_payload["request_id"] = f"{job_name}-round-{args.round:02d}-node-{index:03d}-style"
                _request_json("POST", f"{base_url}/shape/set_colors", payload=colors_payload, token=token)

            text_block = node.get("text_block") or node.get("_auto_text_block")
            if isinstance(text_block, dict) and text_block:
                text_block_payload = {
                    "request_id": f"{job_name}-round-{args.round:02d}-node-{index:03d}-textblock",
                    "session_id": session_id,
                    "shape_id": shape_id,
                    "txt_pin_x": text_block.get("txt_pin_x"),
                    "txt_pin_y": text_block.get("txt_pin_y"),
                    "txt_width": text_block.get("txt_width"),
                    "txt_height": text_block.get("txt_height"),
                }
                _request_json("POST", f"{base_url}/shape/set_text_block", payload=text_block_payload, token=token)

            described_node = _request_json(
                "POST",
                f"{base_url}/shape/describe",
                payload={
                    "request_id": f"{job_name}-round-{args.round:02d}-node-{index:03d}-describe",
                    "session_id": session_id,
                    "shape_id": shape_id,
                },
                token=token,
            )
            node_descriptions[node_id] = dict(described_node["data"])
            style_verification["checked_nodes"] += 1
            node_mismatches = _verify_node_style(node, text_policy, described_node["data"])
            if node_mismatches:
                style_verification["mismatches"].append(
                    {
                        "kind": "node",
                        "id": node_id,
                        "shape_id": shape_id,
                        "issues": node_mismatches,
                    }
                )

        for index, edge in enumerate(drawdsl.get("edges", []), start=1):
            from_id = str(edge["from"])
            to_id = str(edge["to"])
            from_pin, to_pin = _infer_edge_pins(edge, nodes_by_id)
            connect_payload = {
                "request_id": f"{job_name}-round-{args.round:02d}-edge-{index:03d}-add",
                "session_id": session_id,
                "from_shape_id": shape_ids[from_id],
                "to_shape_id": shape_ids[to_id],
                "from_pin_x": from_pin[0],
                "from_pin_y": from_pin[1],
                "to_pin_x": to_pin[0],
                "to_pin_y": to_pin[1],
            }
            connected = _request_json("POST", f"{base_url}/shape/connect", payload=connect_payload, token=token)
            connector_id = int(connected["data"]["connector_id"])
            created_edges.append(
                {
                    "edge_id": edge["id"],
                    "connector_id": connector_id,
                    "route_intent": _resolve_route_intent(edge, nodes_by_id, from_pin, to_pin),
                    "from_pin": {"x_percent": from_pin[0], "y_percent": from_pin[1]},
                    "to_pin": {"x_percent": to_pin[0], "y_percent": to_pin[1]},
                }
            )

            edge_style = _default_edge_style(edge, nodes_by_id, from_pin, to_pin)
            edge_colors = _build_colors_payload(session_id, connector_id, edge_style)
            if edge_colors:
                edge_colors["request_id"] = f"{job_name}-round-{args.round:02d}-edge-{index:03d}-style"
                _request_json("POST", f"{base_url}/shape/set_colors", payload=edge_colors, token=token)

            described_edge = _request_json(
                "POST",
                f"{base_url}/shape/describe",
                payload={
                    "request_id": f"{job_name}-round-{args.round:02d}-edge-{index:03d}-describe",
                    "session_id": session_id,
                    "shape_id": connector_id,
                },
                token=token,
            )
            style_verification["checked_edges"] += 1
            edge_mismatches = _verify_edge_style(edge_style, described_edge["data"])
            if edge_mismatches:
                style_verification["mismatches"].append(
                    {
                        "kind": "edge",
                        "id": edge["id"],
                        "shape_id": connector_id,
                        "issues": edge_mismatches,
                    }
                )

            edge_geometry_issues = _assess_edge_geometry(edge, nodes_by_id, described_edge["data"], from_pin, to_pin)
            if edge_geometry_issues:
                geometry_quality["edge_geometry_warnings"].append(
                    {
                        "id": str(edge["id"]),
                        "shape_id": connector_id,
                        "issues": edge_geometry_issues,
                    }
                )

        preview_file_name = f"round-{args.round:02d}.png"
        preview_path = (preview_dir / preview_file_name).resolve()
        export_payload = {
            "request_id": f"{job_name}-round-{args.round:02d}-export",
            "session_id": session_id,
            "file_name": preview_file_name,
        }
        export = _request_json("POST", f"{base_url}/session/export_png", payload=export_payload, token=token)
        download_url = f"{base_url}{export['data']['download']['url']}"
        _download_file(download_url, preview_path, token=token)

        save_result: dict[str, Any] | None = None
        if args.save_final:
            final_vsdx_dir.mkdir(parents=True, exist_ok=True)
            save_payload = {
                "request_id": f"{job_name}-round-{args.round:02d}-save-final",
                "session_id": session_id,
                "save_path": str(final_vsdx_path),
            }
            save_result = _request_json("POST", f"{base_url}/session/save", payload=save_payload, token=token)

        close_payload = {
            "request_id": f"{job_name}-round-{args.round:02d}-close",
            "session_id": session_id,
            "save": False,
        }
        try:
            close_result: dict[str, Any] | None = _request_json(
                "POST",
                f"{base_url}/session/close",
                payload=close_payload,
                token=token,
            )
        except Exception as exc:
            close_result = {"closed": False, "error": str(exc)}

        _, ambiguous_container_nodes = infer_container_memberships(drawdsl.get("nodes", []))
        quality_assessment = {
            "overlapping_nodes": _detect_node_overlaps(drawdsl.get("nodes", [])),
            "container_violations": _detect_container_violations(drawdsl.get("nodes", [])),
            "ambiguous_container_nodes": ambiguous_container_nodes,
            "opaque_labels": _detect_opaque_labels(drawdsl.get("nodes", []), node_descriptions),
            **geometry_quality,
        }

        summary = {
            "job_name": job_name,
            "round": args.round,
            "drawdsl_path": str(drawdsl_path),
            "preview_path": str(preview_path),
            "save_final": bool(args.save_final),
            "final_vsdx_path": str(final_vsdx_path) if args.save_final else None,
            "node_count": len(created_nodes),
            "edge_count": len(created_edges),
            "nodes": created_nodes,
            "edges": created_edges,
            "export": export,
            "save_result": save_result,
            "close_result": close_result,
            "page_info_before": page_info_before["data"],
            "page_info_after": page_info,
            "page_setup": page_setup["data"] if page_setup else None,
            "style_verification": style_verification,
            "quality_assessment": quality_assessment,
        }
        execution_log_path.parent.mkdir(parents=True, exist_ok=True)
        execution_log_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    except Exception:
        try:
            close_payload = {
                "request_id": f"{job_name}-round-{args.round:02d}-close-after-error",
                "session_id": session_id,
                "save": False,
            }
            _request_json("POST", f"{base_url}/session/close", payload=close_payload, token=token)
        except Exception:
            pass
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
