from __future__ import annotations

import re
from collections import defaultdict
from typing import Any


def is_container(node: dict[str, Any]) -> bool:
    return str(node.get("shape", "")).lower() == "container"


def is_title(node: dict[str, Any]) -> bool:
    return str(node.get("role", "")).lower() == "title"


def is_label(node: dict[str, Any]) -> bool:
    return str(node.get("shape", "")).lower() == "label"


def padding_x(node: dict[str, Any]) -> float:
    value = node.get("padding_x")
    return float(value) if value is not None else 0.10


def padding_y(node: dict[str, Any]) -> float:
    value = node.get("padding_y")
    return float(value) if value is not None else 0.08


def font_size_for_node(node: dict[str, Any], text_policy: dict[str, Any]) -> float | None:
    style = node.get("style", {})
    if "font_size_pt" in style:
        return float(style["font_size_pt"])

    role = str(node.get("role", "")).lower()
    node_id = str(node.get("id", "")).lower()
    if role == "title" or node_id.startswith("title_"):
        value = text_policy.get("title_font_size_pt")
        return float(value) if value is not None else None
    if role == "annotation":
        value = text_policy.get("annotation_font_size_pt")
        return float(value) if value is not None else None

    value = text_policy.get("body_font_size_pt")
    return float(value) if value is not None else None


def resolve_text_direction(node: dict[str, Any], text_policy: dict[str, Any]) -> str:
    explicit = str(node.get("text_direction") or "").strip().lower()
    if explicit in {"horizontal", "vertical"}:
        return explicit

    if explicit == "auto":
        return _infer_auto_text_direction(node, text_policy)

    if not bool(text_policy.get("allow_rotation", False)):
        return "horizontal"

    return _infer_auto_text_direction(node, text_policy)


def expected_text_angle_deg(node: dict[str, Any], text_policy: dict[str, Any]) -> float | None:
    if is_container(node):
        return None

    explicit = node.get("text_angle_deg")
    if explicit is not None:
        return float(explicit)

    direction = resolve_text_direction(node, text_policy)
    return 90.0 if direction == "vertical" else 0.0


def estimate_text_box(node: dict[str, Any], text_policy: dict[str, Any]) -> tuple[float, float]:
    text = str(node.get("text") or "")
    if not text.strip():
        return float(node["width"]), float(node["height"])

    font_size_pt = font_size_for_node(node, text_policy) or 12.0
    direction = resolve_text_direction(node, text_policy)
    lines = [line for line in text.splitlines()] or [text]
    max_chars = max(len(line) for line in lines) if lines else 0
    padding_in_x = padding_x(node)
    padding_in_y = padding_y(node)
    line_height_in = font_size_pt * (1.25 / 72.0)
    char_advance_in = font_size_pt * 0.0068

    if direction == "vertical":
        rotated_text = _normalize_vertical_text(text)
        rotated_chars = max(len(line) for line in rotated_text.splitlines()) if rotated_text else max_chars
        estimated_width = max(line_height_in + 2 * padding_in_x, 0.30)
        estimated_height = rotated_chars * char_advance_in + 2 * padding_in_y
    else:
        estimated_width = max_chars * char_advance_in + 2 * padding_in_x
        estimated_height = len(lines) * line_height_in + 2 * padding_in_y

    return max(float(node["width"]), estimated_width), max(float(node["height"]), estimated_height)


def infer_container_memberships(nodes: list[dict[str, Any]]) -> tuple[dict[str, list[str]], list[str]]:
    containers = [node for node in nodes if is_container(node)]
    containers_by_id = {str(node["id"]): node for node in containers}
    containers_by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for container in containers:
        region_id = str(container.get("region_id") or "").strip()
        if region_id:
            containers_by_region[region_id].append(container)

    memberships: dict[str, list[str]] = defaultdict(list)
    ambiguous: list[str] = []
    for node in nodes:
        if is_container(node):
            continue
        if is_title(node) and not node.get("container_id"):
            continue

        explicit_container_id = str(node.get("container_id") or "").strip()
        if explicit_container_id:
            container = containers_by_id.get(explicit_container_id)
            if container is not None:
                memberships[explicit_container_id].append(str(node["id"]))
            else:
                ambiguous.append(str(node["id"]))
            continue

        region_id = str(node.get("region_id") or "").strip()
        if not region_id:
            continue

        candidates = containers_by_region.get(region_id, [])
        if len(candidates) == 1:
            memberships[str(candidates[0]["id"])].append(str(node["id"]))
            continue
        if len(candidates) <= 1:
            continue

        containing = [container for container in candidates if _container_contains_node(container, node)]
        if len(containing) == 1:
            memberships[str(containing[0]["id"])].append(str(node["id"]))
            continue
        if len(containing) > 1:
            containing.sort(key=_node_area)
            memberships[str(containing[0]["id"])].append(str(node["id"]))
            continue

        ambiguous.append(str(node["id"]))

    return dict(memberships), ambiguous


def apply_layout_postprocess(drawdsl: dict[str, Any]) -> dict[str, Any]:
    nodes = drawdsl.get("nodes", [])
    if not isinstance(nodes, list):
        return drawdsl

    text_policy = drawdsl.get("text_policy", {})
    constraints = drawdsl.get("constraints", {})
    layout = drawdsl.get("layout", {})
    _resolve_node_text_orientation(nodes, text_policy)

    if constraints.get("enforce_text_box_coupling", False):
        for node in nodes:
            if is_container(node):
                continue
            estimated_width, estimated_height = estimate_text_box(node, text_policy)
            node["width"] = round(estimated_width, 3)
            node["height"] = round(estimated_height, 3)

    _synthesize_text_blocks(nodes, text_policy)
    _apply_layout_groups(nodes, layout, constraints)
    _reflow_layout_groups(nodes, layout, constraints)
    _apply_layout_relations(nodes, layout, constraints)
    _separate_layout_groups(nodes, layout, constraints)

    if constraints.get("avoid_overlap", False):
        _reflow_rows_and_columns(nodes, constraints)
        _separate_regions(nodes, constraints)
        _resolve_residual_overlaps(nodes, constraints)

    _auto_fit_containers(nodes, constraints)
    _anchor_titles_to_containers(nodes, constraints)
    return drawdsl


def _infer_auto_text_direction(node: dict[str, Any], text_policy: dict[str, Any]) -> str:
    text = str(node.get("text") or "").strip()
    if not text or is_container(node) or is_label(node):
        return "horizontal"

    cleaned = re.sub(r"\s+", "", text.replace("\n", ""))
    if len(cleaned) < 3:
        return "horizontal"

    width = float(node.get("width") or 0.0)
    height = float(node.get("height") or 0.0)
    if width <= 0.0 or height <= 0.0:
        return "horizontal"

    if width > 1.15:
        return "horizontal"

    if height < width * 1.35:
        return "horizontal"

    font_size_pt = font_size_for_node(node, text_policy) or 12.0
    horizontal_width = len(cleaned) * font_size_pt * 0.0068 + 2 * padding_x(node)
    if horizontal_width <= width * 1.08:
        return "horizontal"

    return "vertical"


def _resolve_node_text_orientation(nodes: list[dict[str, Any]], text_policy: dict[str, Any]) -> None:
    for node in nodes:
        direction = resolve_text_direction(node, text_policy)
        node["_resolved_text_direction"] = direction
        node["_resolved_text_angle_deg"] = expected_text_angle_deg(node, text_policy)
        if direction == "vertical" and node.get("text"):
            node["text"] = _normalize_vertical_text(str(node["text"]))


def _normalize_vertical_text(text: str) -> str:
    compact = " ".join(part.strip() for part in text.splitlines() if part.strip())
    compact = re.sub(r"\s+", " ", compact)
    compact = compact.replace("- ", "-")
    return compact.strip()


def _synthesize_text_blocks(nodes: list[dict[str, Any]], text_policy: dict[str, Any]) -> None:
    for node in nodes:
        if is_container(node) or not node.get("text") or node.get("text_block"):
            continue
        if resolve_text_direction(node, text_policy) != "vertical":
            continue

        text_block_width = max(float(node["height"]) - 2 * padding_y(node), 0.18)
        text_block_height = max(float(node["width"]) - 2 * padding_x(node), 0.18)
        node["_auto_text_block"] = {
            "txt_width": round(text_block_width, 3),
            "txt_height": round(text_block_height, 3),
        }


def _apply_layout_groups(nodes: list[dict[str, Any]], layout: dict[str, Any], constraints: dict[str, Any]) -> None:
    groups = layout.get("groups")
    if not isinstance(groups, list):
        return

    nodes_by_id = {str(node["id"]): node for node in nodes}
    for group in groups:
        if not isinstance(group, dict):
            continue
        members = [nodes_by_id[node_id] for node_id in group.get("members", []) if node_id in nodes_by_id]
        if len(members) < 2:
            continue

        arrangement = str(group.get("arrangement") or "manual").lower()
        gap_x = float(group.get("gap_x") or constraints.get("min_gap_x") or 0.18)
        gap_y = float(group.get("gap_y") or constraints.get("min_gap_y") or 0.18)
        align_x = str(group.get("align_x") or "center").lower()
        align_y = str(group.get("align_y") or "center").lower()

        if arrangement == "row":
            _arrange_row(members, gap_x, align_y)
        elif arrangement == "column":
            _arrange_column(members, gap_y, align_x)


def _reflow_layout_groups(nodes: list[dict[str, Any]], layout: dict[str, Any], constraints: dict[str, Any]) -> None:
    groups = layout.get("groups")
    if not isinstance(groups, list):
        return

    nodes_by_id = {str(node["id"]): node for node in nodes}
    default_gap_x = float(constraints.get("min_gap_x") or 0.18)
    default_gap_y = float(constraints.get("min_gap_y") or 0.18)
    for group in groups:
        if not isinstance(group, dict):
            continue
        members = [nodes_by_id[node_id] for node_id in group.get("members", []) if node_id in nodes_by_id]
        if len(members) < 2:
            continue

        arrangement = str(group.get("arrangement") or "manual").lower()
        min_gap_x = float(group.get("min_gap_x") or group.get("gap_x") or default_gap_x)
        min_gap_y = float(group.get("min_gap_y") or group.get("gap_y") or default_gap_y)
        if arrangement == "row":
            _enforce_row_gap(members, min_gap_x)
        elif arrangement == "column":
            _enforce_column_gap(members, min_gap_y)
        else:
            for _ in range(2):
                for row in _cluster_rows(members, min_gap_y):
                    _enforce_row_gap(row, min_gap_x)
                for column in _cluster_columns(members, min_gap_x):
                    _enforce_column_gap(column, min_gap_y)


def _apply_layout_relations(nodes: list[dict[str, Any]], layout: dict[str, Any], constraints: dict[str, Any]) -> None:
    relations = layout.get("relations")
    groups = layout.get("groups")
    if not isinstance(relations, list) or not isinstance(groups, list):
        return

    nodes_by_id = {str(node["id"]): node for node in nodes}
    group_nodes: dict[str, list[dict[str, Any]]] = {}
    group_specs: dict[str, dict[str, Any]] = {}
    for group in groups:
        if not isinstance(group, dict):
            continue
        group_id = str(group.get("id") or "").strip()
        if not group_id:
            continue
        members = [nodes_by_id[node_id] for node_id in group.get("members", []) if node_id in nodes_by_id]
        if members:
            group_nodes[group_id] = members
            group_specs[group_id] = group

    default_gap_x = float(constraints.get("min_gap_x") or 0.18)
    default_gap_y = float(constraints.get("min_gap_y") or 0.18)
    for relation in relations:
        if not isinstance(relation, dict):
            continue
        source_id = str(relation.get("source") or "")
        target_id = str(relation.get("target") or "")
        source = group_nodes.get(source_id)
        target = group_nodes.get(target_id)
        relation_type = str(relation.get("type") or "").lower()
        if not source or not target or not relation_type:
            continue

        gap = relation.get("gap")
        gap_x = float(gap) if gap is not None else default_gap_x
        gap_y = float(gap) if gap is not None else default_gap_y
        _enforce_group_relation(
            source,
            target,
            relation_type,
            gap_x,
            gap_y,
            source_group=group_specs.get(source_id),
            target_group=group_specs.get(target_id),
        )


def _separate_layout_groups(nodes: list[dict[str, Any]], layout: dict[str, Any], constraints: dict[str, Any]) -> None:
    groups = layout.get("groups")
    if not isinstance(groups, list):
        return

    nodes_by_id = {str(node["id"]): node for node in nodes}
    group_entries: list[tuple[dict[str, Any], list[dict[str, Any]], set[str]]] = []
    for group in groups:
        if not isinstance(group, dict):
            continue
        members = [nodes_by_id[node_id] for node_id in group.get("members", []) if node_id in nodes_by_id]
        member_ids = {str(member["id"]) for member in members}
        if members:
            group_entries.append((group, members, member_ids))

    default_gap_x = float(constraints.get("min_gap_x") or 0.18)
    default_gap_y = float(constraints.get("min_gap_y") or 0.18)
    for _ in range(6):
        moved = False
        for index, (left_group, left_members, left_ids) in enumerate(group_entries):
            left_bounds = _group_bounds(left_members, left_group)
            if left_bounds is None:
                continue
            for right_group, right_members, right_ids in group_entries[index + 1 :]:
                if left_ids & right_ids:
                    continue
                right_bounds = _group_bounds(right_members, right_group)
                if right_bounds is None:
                    continue

                overlap_x, overlap_y = _bounds_overlap(left_bounds, right_bounds)
                if overlap_x <= 0.0 or overlap_y <= 0.0:
                    continue

                left_area = _bounds_area(left_bounds)
                right_area = _bounds_area(right_bounds)
                move_members = left_members if left_area <= right_area else right_members
                move_bounds = left_bounds if left_area <= right_area else right_bounds
                stable_bounds = right_bounds if move_members is left_members else left_bounds
                move_center_x, move_center_y = _bounds_center(move_bounds)
                stable_center_x, stable_center_y = _bounds_center(stable_bounds)

                if overlap_x <= overlap_y:
                    shift_x = -(overlap_x + default_gap_x) if move_center_x < stable_center_x else overlap_x + default_gap_x
                    shift_y = 0.0
                else:
                    shift_x = 0.0
                    shift_y = -(overlap_y + default_gap_y) if move_center_y < stable_center_y else overlap_y + default_gap_y

                _shift_nodes(move_members, shift_x, shift_y)
                moved = True
        if not moved:
            break


def _reflow_rows_and_columns(nodes: list[dict[str, Any]], constraints: dict[str, Any]) -> None:
    nodes_by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        if is_container(node) or is_title(node):
            continue
        region_id = str(node.get("region_id") or "").strip()
        if not region_id:
            continue
        nodes_by_region[region_id].append(node)

    min_gap_x = float(constraints.get("min_gap_x") or 0.18)
    min_gap_y = float(constraints.get("min_gap_y") or 0.18)
    for region_nodes in nodes_by_region.values():
        for _ in range(2):
            for group in _cluster_rows(region_nodes, min_gap_y):
                _enforce_row_gap(group, min_gap_x)
            for group in _cluster_columns(region_nodes, min_gap_x):
                _enforce_column_gap(group, min_gap_y)


def _separate_regions(nodes: list[dict[str, Any]], constraints: dict[str, Any]) -> None:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    bounds_basis: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        region_id = str(node.get("region_id") or "").strip()
        if not region_id:
            continue
        groups[region_id].append(node)
        if not is_container(node):
            bounds_basis[region_id].append(node)

    region_ids = list(bounds_basis.keys())
    min_gap_x = float(constraints.get("min_gap_x") or 0.18)
    min_gap_y = float(constraints.get("min_gap_y") or 0.18)
    for _ in range(6):
        moved = False
        for index, left_region in enumerate(region_ids):
            left_nodes = bounds_basis[left_region]
            left_bounds = _nodes_bounds(left_nodes)
            if left_bounds is None:
                continue
            for right_region in region_ids[index + 1 :]:
                right_nodes = bounds_basis[right_region]
                right_bounds = _nodes_bounds(right_nodes)
                if right_bounds is None:
                    continue
                overlap_x, overlap_y = _bounds_overlap(left_bounds, right_bounds)
                if overlap_x <= 0.0 or overlap_y <= 0.0:
                    continue

                left_area = _bounds_area(left_bounds)
                right_area = _bounds_area(right_bounds)
                move_region = left_region if left_area <= right_area else right_region
                stable_region = right_region if move_region == left_region else left_region
                move_bounds = left_bounds if move_region == left_region else right_bounds
                stable_bounds = right_bounds if stable_region == right_region else left_bounds
                move_center_x, move_center_y = _bounds_center(move_bounds)
                stable_center_x, stable_center_y = _bounds_center(stable_bounds)

                if overlap_x <= overlap_y:
                    distance = overlap_x + min_gap_x
                    shift_x = -distance if move_center_x < stable_center_x else distance
                    shift_y = 0.0
                else:
                    distance = overlap_y + min_gap_y
                    shift_y = -distance if move_center_y < stable_center_y else distance
                    shift_x = 0.0

                _shift_nodes(groups[move_region], shift_x, shift_y)
                moved = True
        if not moved:
            break


def _resolve_residual_overlaps(nodes: list[dict[str, Any]], constraints: dict[str, Any]) -> None:
    min_gap_x = float(constraints.get("min_gap_x") or 0.18)
    min_gap_y = float(constraints.get("min_gap_y") or 0.18)
    candidates = [node for node in nodes if not is_container(node) and not is_title(node)]

    for _ in range(8):
        moved = False
        for index, left in enumerate(candidates):
            left_bounds = _rect_bounds(left)
            for right in candidates[index + 1 :]:
                overlap_x, overlap_y = _bounds_overlap(left_bounds, _rect_bounds(right))
                if overlap_x <= 0.03 or overlap_y <= 0.03:
                    continue

                if is_label(left) and not is_label(right):
                    _shift_label_off_node(left, right, overlap_x, overlap_y, min_gap_x, min_gap_y)
                elif is_label(right) and not is_label(left):
                    _shift_label_off_node(right, left, overlap_x, overlap_y, min_gap_x, min_gap_y)
                elif abs(float(right["x"]) - float(left["x"])) >= abs(float(right["y"]) - float(left["y"])):
                    shift = overlap_x + min_gap_x
                    if float(right["x"]) >= float(left["x"]):
                        _shift_nodes([right], shift, 0.0)
                    else:
                        _shift_nodes([left], shift, 0.0)
                else:
                    shift = overlap_y + min_gap_y
                    if float(right["y"]) <= float(left["y"]):
                        _shift_nodes([right], 0.0, -shift)
                    else:
                        _shift_nodes([left], 0.0, -shift)
                moved = True
                left_bounds = _rect_bounds(left)
        if not moved:
            break


def _auto_fit_containers(nodes: list[dict[str, Any]], constraints: dict[str, Any]) -> None:
    memberships, _ = infer_container_memberships(nodes)
    nodes_by_id = {str(node["id"]): node for node in nodes}
    containers = [node for node in nodes if is_container(node)]
    containers.sort(key=_node_area)
    min_gap_x = float(constraints.get("min_gap_x") or 0.18)
    min_gap_y = float(constraints.get("min_gap_y") or 0.18)

    for container in containers:
        member_ids = memberships.get(str(container["id"]), [])
        members = [nodes_by_id[node_id] for node_id in member_ids if node_id in nodes_by_id]
        members = [node for node in members if not is_title(node)]
        bounds = _nodes_bounds(members)
        if bounds is None:
            continue

        raw_pad_x = container.get("padding_x")
        raw_pad_y = container.get("padding_y")
        default_pad_x = constraints.get("default_container_padding_x")
        default_pad_y = constraints.get("default_container_padding_y")
        pad_x = float(raw_pad_x) if raw_pad_x is not None else float(default_pad_x) if default_pad_x is not None else max(0.24, min_gap_x * 1.4)
        pad_y = float(raw_pad_y) if raw_pad_y is not None else float(default_pad_y) if default_pad_y is not None else max(0.24, min_gap_y * 1.4)
        left, bottom, right, top = bounds
        container["x"] = round((left + right) / 2, 3)
        container["y"] = round((bottom + top) / 2, 3)
        container["width"] = round((right - left) + 2 * pad_x, 3)
        container["height"] = round((top - bottom) + 2 * pad_y, 3)


def _anchor_titles_to_containers(nodes: list[dict[str, Any]], constraints: dict[str, Any]) -> None:
    containers = [node for node in nodes if is_container(node)]
    containers_by_id = {str(node["id"]): node for node in containers}
    containers_by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for container in containers:
        region_id = str(container.get("region_id") or "").strip()
        if region_id:
            containers_by_region[region_id].append(container)

    for node in nodes:
        if not is_title(node):
            continue

        target: dict[str, Any] | None = None
        explicit_container_id = str(node.get("container_id") or "").strip()
        if explicit_container_id:
            target = containers_by_id.get(explicit_container_id)
        if target is None:
            candidates = containers_by_region.get(str(node.get("region_id") or "").strip(), [])
            if len(candidates) == 1:
                target = candidates[0]

        if target is None:
            continue

        target_bounds = _rect_bounds(target)
        raw_clearance = node.get("title_clearance_y")
        default_clearance = constraints.get("default_title_clearance_y")
        if raw_clearance is not None:
            clearance = float(raw_clearance)
        elif default_clearance is not None:
            clearance = float(default_clearance)
        else:
            clearance = max(0.06, padding_y(node) * 0.6)
        node["x"] = round(float(target["x"]), 3)
        node["y"] = round(target_bounds[3] + float(node["height"]) / 2 + clearance, 3)


def _cluster_rows(nodes: list[dict[str, Any]], min_gap_y: float) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    for node in sorted(nodes, key=lambda item: float(item["y"]), reverse=True):
        placed = False
        for group in groups:
            if _same_row(node, group[0], min_gap_y):
                group.append(node)
                placed = True
                break
        if not placed:
            groups.append([node])
    return [group for group in groups if len(group) > 1]


def _cluster_columns(nodes: list[dict[str, Any]], min_gap_x: float) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    for node in sorted(nodes, key=lambda item: float(item["x"])):
        placed = False
        for group in groups:
            if _same_column(node, group[0], min_gap_x):
                group.append(node)
                placed = True
                break
        if not placed:
            groups.append([node])
    return [group for group in groups if len(group) > 1]


def _same_row(left: dict[str, Any], right: dict[str, Any], min_gap_y: float) -> bool:
    center_delta = abs(float(left["y"]) - float(right["y"]))
    avg_height = (float(left["height"]) + float(right["height"])) / 2
    return center_delta <= max(avg_height * 0.55, min_gap_y * 2.2)


def _same_column(left: dict[str, Any], right: dict[str, Any], min_gap_x: float) -> bool:
    center_delta = abs(float(left["x"]) - float(right["x"]))
    avg_width = (float(left["width"]) + float(right["width"])) / 2
    return center_delta <= max(avg_width * 0.75, min_gap_x * 2.2)


def _arrange_row(nodes: list[dict[str, Any]], gap_x: float, align_y: str) -> None:
    ordered = list(nodes)
    if not ordered:
        return
    reference_y = _aligned_y(ordered[0], align_y)
    for index in range(1, len(ordered)):
        previous = ordered[index - 1]
        current = ordered[index]
        previous_right = float(previous["x"]) + float(previous["width"]) / 2
        current["x"] = round(previous_right + gap_x + float(current["width"]) / 2, 3)
        _set_aligned_y(current, reference_y, align_y)


def _arrange_column(nodes: list[dict[str, Any]], gap_y: float, align_x: str) -> None:
    ordered = list(nodes)
    if not ordered:
        return
    reference_x = _aligned_x(ordered[0], align_x)
    for index in range(1, len(ordered)):
        previous = ordered[index - 1]
        current = ordered[index]
        previous_bottom = float(previous["y"]) - float(previous["height"]) / 2
        current["y"] = round(previous_bottom - gap_y - float(current["height"]) / 2, 3)
        _set_aligned_x(current, reference_x, align_x)


def _enforce_group_relation(
    source: list[dict[str, Any]],
    target: list[dict[str, Any]],
    relation_type: str,
    gap_x: float,
    gap_y: float,
    *,
    source_group: dict[str, Any] | None = None,
    target_group: dict[str, Any] | None = None,
) -> None:
    source_bounds = _group_bounds(source, source_group)
    target_bounds = _group_bounds(target, target_group)
    if source_bounds is None or target_bounds is None:
        return

    if relation_type == "right_of":
        required_left = source_bounds[2] + gap_x
        delta = required_left - target_bounds[0]
        if delta > 0:
            _shift_nodes(target, delta, 0.0)
    elif relation_type == "left_of":
        required_right = source_bounds[0] - gap_x
        delta = target_bounds[2] - required_right
        if delta > 0:
            _shift_nodes(target, -delta, 0.0)
    elif relation_type == "below":
        required_top = source_bounds[1] - gap_y
        delta = target_bounds[3] - required_top
        if delta > 0:
            _shift_nodes(target, 0.0, -delta)
    elif relation_type == "above":
        required_bottom = source_bounds[3] + gap_y
        delta = required_bottom - target_bounds[1]
        if delta > 0:
            _shift_nodes(target, 0.0, delta)
    elif relation_type == "align_center_x":
        _shift_nodes(target, _bounds_center(source_bounds)[0] - _bounds_center(target_bounds)[0], 0.0)
    elif relation_type == "align_center_y":
        _shift_nodes(target, 0.0, _bounds_center(source_bounds)[1] - _bounds_center(target_bounds)[1])
    elif relation_type == "align_left":
        _shift_nodes(target, source_bounds[0] - target_bounds[0], 0.0)
    elif relation_type == "align_right":
        _shift_nodes(target, source_bounds[2] - target_bounds[2], 0.0)
    elif relation_type == "align_top":
        _shift_nodes(target, 0.0, source_bounds[3] - target_bounds[3])
    elif relation_type == "align_bottom":
        _shift_nodes(target, 0.0, source_bounds[1] - target_bounds[1])


def _group_bounds(nodes: list[dict[str, Any]], group: dict[str, Any] | None = None) -> tuple[float, float, float, float] | None:
    bounds = _nodes_bounds(nodes)
    if bounds is None:
        return None
    if not isinstance(group, dict):
        return bounds

    margin_left = float(group.get("margin_left") or 0.0)
    margin_right = float(group.get("margin_right") or 0.0)
    margin_top = float(group.get("margin_top") or 0.0)
    margin_bottom = float(group.get("margin_bottom") or 0.0)
    return (
        bounds[0] - margin_left,
        bounds[1] - margin_bottom,
        bounds[2] + margin_right,
        bounds[3] + margin_top,
    )


def _enforce_row_gap(nodes: list[dict[str, Any]], min_gap_x: float) -> None:
    ordered = sorted(nodes, key=lambda item: float(item["x"]))
    for index in range(1, len(ordered)):
        previous = ordered[index - 1]
        current = ordered[index]
        previous_right = float(previous["x"]) + float(previous["width"]) / 2
        current_left = float(current["x"]) - float(current["width"]) / 2
        delta = previous_right + min_gap_x - current_left
        if delta > 0:
            for follower in ordered[index:]:
                _shift_nodes([follower], delta, 0.0)


def _enforce_column_gap(nodes: list[dict[str, Any]], min_gap_y: float) -> None:
    ordered = sorted(nodes, key=lambda item: float(item["y"]), reverse=True)
    for index in range(1, len(ordered)):
        previous = ordered[index - 1]
        current = ordered[index]
        previous_bottom = float(previous["y"]) - float(previous["height"]) / 2
        current_top = float(current["y"]) + float(current["height"]) / 2
        delta = current_top - (previous_bottom - min_gap_y)
        if delta > 0:
            for follower in ordered[index:]:
                _shift_nodes([follower], 0.0, -delta)


def _aligned_x(node: dict[str, Any], align_x: str) -> float:
    if align_x == "left":
        return float(node["x"]) - float(node["width"]) / 2
    if align_x == "right":
        return float(node["x"]) + float(node["width"]) / 2
    return float(node["x"])


def _aligned_y(node: dict[str, Any], align_y: str) -> float:
    if align_y == "top":
        return float(node["y"]) + float(node["height"]) / 2
    if align_y == "bottom":
        return float(node["y"]) - float(node["height"]) / 2
    return float(node["y"])


def _set_aligned_x(node: dict[str, Any], reference_x: float, align_x: str) -> None:
    if align_x == "left":
        node["x"] = round(reference_x + float(node["width"]) / 2, 3)
    elif align_x == "right":
        node["x"] = round(reference_x - float(node["width"]) / 2, 3)
    else:
        node["x"] = round(reference_x, 3)


def _set_aligned_y(node: dict[str, Any], reference_y: float, align_y: str) -> None:
    if align_y == "top":
        node["y"] = round(reference_y - float(node["height"]) / 2, 3)
    elif align_y == "bottom":
        node["y"] = round(reference_y + float(node["height"]) / 2, 3)
    else:
        node["y"] = round(reference_y, 3)


def _shift_label_off_node(
    label: dict[str, Any],
    other: dict[str, Any],
    overlap_x: float,
    overlap_y: float,
    min_gap_x: float,
    min_gap_y: float,
) -> None:
    delta_x = float(label["x"]) - float(other["x"])
    delta_y = float(label["y"]) - float(other["y"])
    if abs(delta_y) >= abs(delta_x):
        shift = overlap_y + min_gap_y
        _shift_nodes([label], 0.0, shift if delta_y >= 0 else -shift)
    else:
        shift = overlap_x + min_gap_x
        _shift_nodes([label], shift if delta_x >= 0 else -shift, 0.0)


def _shift_nodes(nodes: list[dict[str, Any]], shift_x: float, shift_y: float) -> None:
    if shift_x == 0.0 and shift_y == 0.0:
        return
    for node in nodes:
        node["x"] = round(float(node["x"]) + shift_x, 3)
        node["y"] = round(float(node["y"]) + shift_y, 3)


def _container_contains_node(container: dict[str, Any], node: dict[str, Any], tolerance: float = 0.04) -> bool:
    container_bounds = _rect_bounds(container)
    node_bounds = _rect_bounds(node)
    return (
        node_bounds[0] >= container_bounds[0] - tolerance
        and node_bounds[1] >= container_bounds[1] - tolerance
        and node_bounds[2] <= container_bounds[2] + tolerance
        and node_bounds[3] <= container_bounds[3] + tolerance
    )


def _rect_bounds(node: dict[str, Any]) -> tuple[float, float, float, float]:
    x = float(node["x"])
    y = float(node["y"])
    width = float(node["width"])
    height = float(node["height"])
    return x - width / 2, y - height / 2, x + width / 2, y + height / 2


def _nodes_bounds(nodes: list[dict[str, Any]]) -> tuple[float, float, float, float] | None:
    if not nodes:
        return None
    left = min(_rect_bounds(node)[0] for node in nodes)
    bottom = min(_rect_bounds(node)[1] for node in nodes)
    right = max(_rect_bounds(node)[2] for node in nodes)
    top = max(_rect_bounds(node)[3] for node in nodes)
    return left, bottom, right, top


def _bounds_overlap(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
) -> tuple[float, float]:
    overlap_x = min(left[2], right[2]) - max(left[0], right[0])
    overlap_y = min(left[3], right[3]) - max(left[1], right[1])
    return max(0.0, overlap_x), max(0.0, overlap_y)


def _bounds_area(bounds: tuple[float, float, float, float]) -> float:
    return max(0.0, bounds[2] - bounds[0]) * max(0.0, bounds[3] - bounds[1])


def _bounds_center(bounds: tuple[float, float, float, float]) -> tuple[float, float]:
    return (bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2


def _node_area(node: dict[str, Any]) -> float:
    return float(node["width"]) * float(node["height"])
