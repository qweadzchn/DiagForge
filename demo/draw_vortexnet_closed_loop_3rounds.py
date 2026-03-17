#!/usr/bin/env python3
"""Closed-loop 3-round drawing for VortexNet architecture.

- Draw round 1/2/3 with incremental refinements.
- Save VSDX per round on Windows.
- Export PNG per round through secure bridge endpoint.
- Download PNG to local workspace for visual inspection.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

BASE = os.environ.get("VISIO_BRIDGE_BASE", "http://host.docker.internal:18761")
TOKEN = os.environ.get("VISIO_BRIDGE_TOKEN", "")
LOCAL_OUT = Path(os.environ.get("LOCAL_PREVIEW_DIR", "./demo/exports"))
LOCAL_OUT.mkdir(parents=True, exist_ok=True)


def rid() -> str:
    return str(uuid.uuid4())


def headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def request_json(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers=headers(), method=method)

    last_err: Exception | None = None
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as e:
            last_err = e
            time.sleep(1.0 + i)

    raise RuntimeError(f"request failed {method} {path}: {last_err}")


def post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    return request_json("POST", path, {"request_id": rid(), **payload})


def download_artifact(ticket: str, local_path: Path) -> None:
    req = urllib.request.Request(
        BASE + f"/artifact/download/{ticket}",
        headers=headers(),
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        local_path.write_bytes(resp.read())


def draw_round(round_idx: int) -> dict[str, Any]:
    session = post("/session/create", {"visible": True})
    session_id = session["session_id"]

    created: dict[str, int] = {}

    # ---- style presets (incremental refinement) ----
    if round_idx == 1:
        node_font = 10.0
        title_font = 12.0
        line_w = 1.0
        model_w = 2.3
        io4_w = 2.3
    elif round_idx == 2:
        node_font = 10.5
        title_font = 12.5
        line_w = 1.05
        model_w = 2.45
        io4_w = 2.45
    else:
        node_font = 10.5
        title_font = 12.5
        line_w = 1.1
        model_w = 2.55
        io4_w = 2.6

    font_name = "Times New Roman"

    def add(
        key: str,
        x: float,
        y: float,
        w: float,
        h: float,
        text: str,
        *,
        fill: tuple[int, int, int] | None = None,
        line: tuple[int, int, int] = (20, 20, 20),
        fsize: float | None = None,
    ) -> int:
        r = post(
            "/shape/add",
            {
                "session_id": session_id,
                "shape_type": "Rectangle",
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "text": text,
            },
        )
        sid = int(r["data"]["shape_id"])
        created[key] = sid

        post(
            "/shape/set_text_style",
            {
                "session_id": session_id,
                "shape_id": sid,
                "font_name": font_name,
                "font_size_pt": fsize if fsize is not None else node_font,
                "font_rgb": [15, 15, 15],
            },
        )

        color_payload: dict[str, Any] = {
            "session_id": session_id,
            "shape_id": sid,
            "line_rgb": list(line),
            "line_weight_pt": line_w,
        }
        if fill is not None:
            color_payload["fill_rgb"] = list(fill)
        post("/shape/set_colors", color_payload)
        return sid

    def connect(a: str, b: str, *, rgb=(20, 20, 20), lw: float | None = None) -> int:
        c = post(
            "/shape/connect",
            {
                "session_id": session_id,
                "from_shape_id": created[a],
                "to_shape_id": created[b],
            },
        )
        cid = int(c["data"]["connector_id"])
        post(
            "/shape/set_colors",
            {
                "session_id": session_id,
                "shape_id": cid,
                "line_rgb": list(rgb),
                "line_weight_pt": line_w if lw is None else lw,
            },
        )
        return cid

    # ---- section titles ----
    add("title_model", 2.2, 8.85, 1.8, 0.42, "Model", fill=(250, 250, 250), fsize=title_font)
    add("title_backbone", 5.3, 8.85, 2.1, 0.42, "Backbone", fill=(250, 250, 250), fsize=title_font)
    add("title_cbs", 8.9, 8.85, 1.3, 0.42, "CBS", fill=(250, 250, 250), fsize=title_font)
    add("title_c2f", 8.9, 5.95, 1.3, 0.42, "c2f", fill=(250, 250, 250), fsize=title_font)

    # ---- visual containers (solid fallback for dashed outlines) ----
    add("box_model", 2.2, 5.7, model_w, 6.2, "", fill=(246, 246, 246), line=(10, 10, 10), fsize=9)
    add("box_backbone", 5.35, 7.95, 4.95, 2.0, "", fill=(246, 246, 246), line=(10, 10, 10), fsize=9)
    add("box_neck", 6.15, 4.7, 4.1, 3.9, "", fill=(246, 246, 246), line=(10, 10, 10), fsize=9)
    add("box_cbs", 8.9, 7.95, 2.0, 2.0, "", fill=(246, 246, 246), line=(10, 10, 10), fsize=9)
    add("box_c2f", 8.9, 4.0, 2.0, 3.95, "", fill=(246, 246, 246), line=(10, 10, 10), fsize=9)

    # ---- left lane ----
    add("raw", 0.8, 7.8, 1.6, 0.85, "RAW", fill=(165, 217, 160), fsize=13)
    add("b_main", 2.2, 7.2, 2.1, 1.08, "Backbone\nVortexNet", fill=(186, 198, 220), fsize=title_font)
    add("n_main", 2.2, 5.55, 2.1, 1.05, "Neck\nFAD-PAN", fill=(234, 188, 145), fsize=title_font)
    add("h_main", 2.2, 3.9, 2.1, 0.95, "Head", fill=(160, 202, 140), fsize=title_font)
    add("nms", 2.2, 1.15, 2.1, 1.05, "NMS-\nSimilar", fill=(246, 196, 20), fsize=title_font)
    add("boxdraw", 0.8, 0.45, 1.6, 0.75, "Box Draw", fill=(165, 217, 160), fsize=13)
    add("boxes_cls", 2.2, 2.4, 1.8, 0.45, "Boxes, Cls", fill=(246, 246, 246), line=(246, 246, 246), fsize=11.5)

    # loss + optimization area
    add("loss", 4.05, 3.95, 2.05, 1.25, "+Obj Loss\n+Box Loss\n+Cls Loss", fill=(170, 211, 225), fsize=12)
    add("weights", 4.35, 5.55, 1.2, 0.55, "Weights", fill=(246, 246, 246), line=(246, 246, 246), fsize=12)
    add("optimizer", 4.95, 5.0, 1.45, 0.9, "Optimizer", fill=(235, 241, 210), fsize=12)

    # ---- backbone sequence ----
    seq_x0, dx = 3.25, 0.44
    backbone_nodes = [
        ("bb_cbs1", "CBS", (140, 210, 205), 0.40, 1.05),
        ("bb_cbs2", "CBS", (140, 210, 205), 0.40, 1.05),
        ("bb_c2f1", "c2f", (193, 228, 180), 0.40, 1.05),
        ("bb_amsp1", "AMSP-VC", (241, 224, 112), 0.40, 1.55),
        ("bb_c2f2", "c2f", (193, 228, 180), 0.40, 1.05),
        ("bb_amsp2", "AMSP-VC", (241, 224, 112), 0.40, 1.55),
        ("bb_c2f3", "c2f", (193, 228, 180), 0.40, 1.05),
        ("bb_amsp3", "AMSP-VC", (241, 224, 112), 0.40, 1.55),
        ("bb_c2f4", "c2f", (193, 228, 180), 0.40, 1.05),
        ("bb_sppf", "SPPF", (236, 198, 221), 0.42, 1.05),
    ]
    for i, (k, t, c, w, h) in enumerate(backbone_nodes):
        add(k, seq_x0 + i * dx, 7.95, w, h, t, fill=c, fsize=12 if "AMSP" in t else 11)

    add("f_in", 2.95, 8.25, 0.5, 0.34, "F_in", fill=(255, 255, 255), line=(255, 255, 255), fsize=11)

    # ---- neck graph (top row then bottom row) ----
    top = [
        ("nt1", "Cat", (178, 220, 105), 5.05),
        ("nt2", "Upsample", (242, 185, 102), 5.50),
        ("nt3", "FAD-CSP", (156, 98, 208), 5.95),
        ("nt4", "Cat", (178, 220, 105), 6.40),
        ("nt5", "Upsample", (242, 185, 102), 6.85),
        ("nt6", "CBS", (140, 210, 205), 7.30),
    ]
    for k, t, c, x in top:
        add(k, x, 5.40, 0.38, 1.05, t, fill=c, fsize=11)

    bot = [
        ("nb1", "FAD-CSP", (156, 98, 208), 5.05),
        ("nb2", "CBS", (140, 210, 205), 5.50),
        ("nb3", "Cat", (178, 220, 105), 5.95),
        ("nb4", "FAD-CSP", (156, 98, 208), 6.40),
        ("nb5", "CBS", (140, 210, 205), 6.85),
        ("nb6", "Cat", (178, 220, 105), 7.30),
        ("nb7", "FAD-CSP", (156, 98, 208), 7.75),
    ]
    for k, t, c, x in bot:
        add(k, x, 4.00, 0.38, 1.05, t, fill=c, fsize=11)

    add("detect", 6.40, 2.95, 1.25, 0.52, "Dectet", fill=(146, 146, 146), fsize=13)
    add("s", 5.80, 3.15, 0.28, 0.28, "s", fill=(255, 255, 255), line=(255, 255, 255), fsize=14)
    add("m", 6.40, 3.45, 0.28, 0.28, "m", fill=(255, 255, 255), line=(255, 255, 255), fsize=14)
    add("l", 7.00, 3.15, 0.28, 0.28, "l", fill=(255, 255, 255), line=(255, 255, 255), fsize=14)

    add("f_out", 6.40, 2.15, 0.55, 0.32, "F_out", fill=(255, 255, 255), line=(255, 255, 255), fsize=11)

    # ---- right detail blocks ----
    add("d_conv", 8.35, 7.95, 0.44, 1.05, "Conv2d", fill=(193, 210, 160), fsize=12)
    add("d_bn", 8.90, 7.95, 0.44, 1.05, "Batch\nNorm2d", fill=(188, 140, 193), fsize=12)
    add("d_silu", 9.45, 7.95, 0.44, 1.05, "SiLU", fill=(236, 192, 149), fsize=12)

    add("c2f_top", 8.90, 5.25, 0.92, 0.52, "CBS", fill=(140, 210, 205), fsize=12)
    add("c2f_split", 8.90, 4.55, 0.92, 0.52, "Split", fill=(218, 219, 95), fsize=12)
    add("c2f_bneck", 8.90, 3.70, 1.10, 0.72, "Bottleneck", fill=(90, 171, 219), fsize=12)
    add("c2f_c", 8.90, 2.90, 0.34, 0.45, "C", fill=(255, 255, 255), fsize=14)
    add("c2f_bottom", 8.90, 2.20, 0.92, 0.52, "CBS", fill=(140, 210, 205), fsize=12)

    # ---- I/O chain ----
    add("io1", 3.80, 1.02, 0.74, 0.45, "I\O", fill=(244, 244, 244), fsize=12)
    add("io2", 5.15, 1.02, 1.62, 0.45, "I\O (Per batch)", fill=(244, 244, 244), fsize=12)
    add("io3", 7.05, 1.02, 1.95, 0.45, "I\O (Cross-stage)", fill=(244, 244, 244), fsize=12)
    add("io4", 9.45, 1.02, io4_w, 0.45, "I\O (Not in Network)", fill=(244, 244, 244), fsize=12)

    # ---- connectors ----
    connect("raw", "b_main")
    connect("b_main", "n_main", rgb=(245, 77, 20), lw=1.3)
    connect("n_main", "h_main", rgb=(245, 77, 20), lw=1.3)
    connect("h_main", "nms", rgb=(245, 77, 20), lw=1.3)
    connect("h_main", "loss", rgb=(245, 77, 20), lw=1.3)
    connect("nms", "boxdraw")
    connect("nms", "io1")

    bkeys = [x[0] for x in backbone_nodes]
    for a, b in zip(bkeys[:-1], bkeys[1:]):
        connect(a, b)

    connect("bb_c2f2", "nt1", rgb=(245, 77, 20), lw=1.2)
    connect("bb_c2f3", "nt4", rgb=(245, 77, 20), lw=1.2)
    connect("bb_sppf", "nt6", rgb=(245, 77, 20), lw=1.2)

    connect("nt6", "nt5")
    connect("nt5", "nt4")
    connect("nt4", "nt3")
    connect("nt3", "nt2")
    connect("nt2", "nt1")

    connect("nt1", "nb1")
    connect("nb1", "nb2")
    connect("nb2", "nb3")
    connect("nb3", "nb4")
    connect("nb4", "nb5")
    connect("nb5", "nb6")
    connect("nb6", "nb7")

    connect("nb1", "detect", rgb=(245, 77, 20), lw=1.3)
    connect("nb4", "detect", rgb=(245, 77, 20), lw=1.3)
    connect("nb7", "detect", rgb=(245, 77, 20), lw=1.3)

    connect("d_conv", "d_bn")
    connect("d_bn", "d_silu")

    connect("c2f_top", "c2f_split")
    connect("c2f_split", "c2f_bneck")
    connect("c2f_bneck", "c2f_c")
    connect("c2f_c", "c2f_bottom")
    connect("c2f_split", "c2f_c", rgb=(245, 77, 20), lw=1.2)

    connect("io1", "io2")
    connect("io2", "io3", rgb=(245, 77, 20), lw=1.3)
    connect("io3", "io4", rgb=(45, 62, 230), lw=1.3)
    connect("detect", "io3", rgb=(245, 77, 20), lw=1.3)

    connect("weights", "optimizer", rgb=(116, 160, 86), lw=1.3)

    # ---- export first, then save ----
    export_name = f"vortexnet_closedloop_r{round_idx}.png"
    export = post(
        "/session/export_png",
        {
            "session_id": session_id,
            "file_name": export_name,
        },
    )
    ticket = export["data"]["download"]["ticket"]

    local_png = LOCAL_OUT / export_name
    download_artifact(ticket, local_png)

    vsdx_path = fr"D:\work\png2vsdx\demo\vortexnet_closedloop_r{round_idx}_{int(time.time())}.vsdx"
    save: dict[str, Any] | None = None
    save_error: str | None = None
    try:
        save = post("/session/save", {"session_id": session_id, "save_path": vsdx_path})
    except Exception as e:
        save_error = str(e)

    out = {
        "round": round_idx,
        "session_id": session_id,
        "shape_count": len(created),
        "save_path": vsdx_path,
        "save": save,
        "export": export,
        "local_png": str(local_png),
    }
    if save_error:
        out["save_error"] = save_error
    return out


def main() -> None:
    out: dict[str, Any] = {
        "health": request_json("GET", "/health"),
        "ping": post("/ping_visio", {}),
        "rounds": [],
    }

    for r in (1, 2, 3):
        try:
            out["rounds"].append(draw_round(r))
        except Exception as e:
            out["rounds"].append({"round": r, "error": str(e)})

    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
