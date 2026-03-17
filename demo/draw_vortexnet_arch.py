#!/usr/bin/env python3
import json
import os
import urllib.request
import uuid

BASE = os.environ.get("VISIO_BRIDGE_BASE", "http://host.docker.internal:18761")
TOKEN = os.environ.get("VISIO_BRIDGE_TOKEN", "")


def rid() -> str:
    return str(uuid.uuid4())


def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def request_json(method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data, headers=_headers(), method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def post(path: str, payload: dict) -> dict:
    payload = {"request_id": rid(), **payload}
    return request_json("POST", path, payload)


session = post("/session/create", {"visible": True})
session_id = session["session_id"]

created: dict[str, int] = {}
connectors: list[int] = []


def add(
    key: str,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    fill: tuple[int, int, int] | None = None,
    line: tuple[int, int, int] = (40, 40, 40),
    font_size: float = 10.0,
):
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
            "font_name": "Times New Roman",
            "font_size_pt": font_size,
            "font_rgb": [20, 20, 20],
        },
    )

    color_payload = {
        "session_id": session_id,
        "shape_id": sid,
        "line_rgb": list(line),
        "line_weight_pt": 1.0,
    }
    if fill is not None:
        color_payload["fill_rgb"] = list(fill)

    post("/shape/set_colors", color_payload)
    return sid


def connect(a: str, b: str, color: tuple[int, int, int] = (35, 35, 35), weight: float = 1.0):
    r = post(
        "/shape/connect",
        {
            "session_id": session_id,
            "from_shape_id": created[a],
            "to_shape_id": created[b],
        },
    )
    cid = int(r["data"]["connector_id"])
    connectors.append(cid)
    post(
        "/shape/set_colors",
        {
            "session_id": session_id,
            "shape_id": cid,
            "line_rgb": list(color),
            "line_weight_pt": weight,
        },
    )


# ---- containers ----
add("model_container", 2.0, 5.7, 2.2, 5.3, "Model", fill=(248, 248, 248), font_size=12)
add("backbone_container", 5.1, 7.9, 4.2, 2.0, "Backbone", fill=(248, 248, 248), font_size=12)
add("neck_container", 6.0, 4.7, 3.8, 3.0, "", fill=(248, 248, 248), font_size=10)
add("cbs_detail_container", 8.6, 7.9, 2.0, 2.0, "CBS", fill=(248, 248, 248), font_size=12)
add("c2f_detail_container", 8.6, 4.5, 2.0, 4.6, "c2f", fill=(248, 248, 248), font_size=12)

# ---- left lane ----
add("raw", 0.8, 7.8, 1.2, 0.8, "RAW", fill=(170, 220, 170), font_size=11)
add("backbone_main", 2.0, 7.2, 1.8, 1.0, "Backbone\nVortexNet", fill=(187, 202, 224), font_size=11)
add("neck_main", 2.0, 5.8, 1.8, 1.0, "Neck\nFAD-PAN", fill=(234, 191, 150), font_size=11)
add("head_main", 2.0, 4.4, 1.8, 0.9, "Head", fill=(166, 206, 145), font_size=11)
add("nms", 2.0, 2.0, 1.6, 1.0, "NMS-\nSimilar", fill=(247, 199, 36), font_size=11)
add("box_draw", 0.8, 1.2, 1.2, 0.8, "Box Draw", fill=(170, 220, 170), font_size=11)
add("loss", 3.5, 4.1, 1.8, 1.0, "+Obj Loss\n+Box Loss\n+Cls Loss", fill=(170, 211, 225), font_size=10)

# ---- backbone sequence ----
x0 = 3.3
dx = 0.43
labels = [
    ("bb_cbs1", "CBS", (140, 210, 205)),
    ("bb_cbs2", "CBS", (140, 210, 205)),
    ("bb_c2f1", "c2f", (193, 228, 180)),
    ("bb_amsp1", "AMSP-VC", (240, 224, 120)),
    ("bb_c2f2", "c2f", (193, 228, 180)),
    ("bb_amsp2", "AMSP-VC", (240, 224, 120)),
    ("bb_c2f3", "c2f", (193, 228, 180)),
    ("bb_amsp3", "AMSP-VC", (240, 224, 120)),
    ("bb_c2f4", "c2f", (193, 228, 180)),
    ("bb_sppf", "SPPF", (236, 198, 221)),
]
for i, (k, t, c) in enumerate(labels):
    h = 0.9 if "AMSP" not in t else 1.2
    add(k, x0 + i * dx, 7.8, 0.32, h, t, fill=c, font_size=8.8)

# ---- neck graph ----
add("neck_cat1", 5.0, 5.4, 0.32, 0.9, "Cat", fill=(180, 220, 110), font_size=8.5)
add("neck_up1", 5.4, 5.4, 0.32, 0.9, "Upsample", fill=(241, 184, 99), font_size=8.2)
add("neck_fad1", 5.8, 5.4, 0.32, 0.9, "FAD-CSP", fill=(162, 104, 210), font_size=8.5)
add("neck_cat2", 6.2, 5.4, 0.32, 0.9, "Cat", fill=(180, 220, 110), font_size=8.5)
add("neck_up2", 6.6, 5.4, 0.32, 0.9, "Upsample", fill=(241, 184, 99), font_size=8.2)
add("neck_cbs_top", 7.0, 5.4, 0.32, 0.9, "CBS", fill=(140, 210, 205), font_size=8.5)

add("neck_fad2", 5.0, 4.0, 0.32, 0.9, "FAD-CSP", fill=(162, 104, 210), font_size=8.5)
add("neck_cbs1", 5.4, 4.0, 0.32, 0.9, "CBS", fill=(140, 210, 205), font_size=8.5)
add("neck_cat3", 5.8, 4.0, 0.32, 0.9, "Cat", fill=(180, 220, 110), font_size=8.5)
add("neck_fad3", 6.2, 4.0, 0.32, 0.9, "FAD-CSP", fill=(162, 104, 210), font_size=8.5)
add("neck_cbs2", 6.6, 4.0, 0.32, 0.9, "CBS", fill=(140, 210, 205), font_size=8.5)
add("neck_cat4", 7.0, 4.0, 0.32, 0.9, "Cat", fill=(180, 220, 110), font_size=8.5)
add("neck_fad4", 7.4, 4.0, 0.32, 0.9, "FAD-CSP", fill=(162, 104, 210), font_size=8.5)
add("detect", 6.2, 2.9, 1.0, 0.5, "Dectet", fill=(160, 160, 160), font_size=10)

# ---- right detail: CBS ----
add("d_conv", 8.1, 7.8, 0.42, 0.9, "Conv2d", fill=(193, 210, 160), font_size=9)
add("d_bn", 8.6, 7.8, 0.42, 0.9, "Batch\nNorm2d", fill=(188, 140, 193), font_size=9)
add("d_silu", 9.1, 7.8, 0.42, 0.9, "SiLU", fill=(236, 192, 149), font_size=9)

# ---- right detail: c2f ----
add("c2f_cbs_top", 8.6, 5.8, 0.8, 0.45, "CBS", fill=(140, 210, 205), font_size=9)
add("c2f_split", 8.6, 5.2, 0.8, 0.45, "Split", fill=(218, 219, 95), font_size=9)
add("c2f_bottleneck", 8.6, 4.5, 0.95, 0.6, "Bottleneck", fill=(90, 171, 219), font_size=9)
add("c2f_c", 8.6, 3.8, 0.3, 0.45, "C", fill=(255, 255, 255), font_size=12)
add("c2f_cbs_bottom", 8.6, 3.2, 0.8, 0.45, "CBS", fill=(140, 210, 205), font_size=9)

# ---- bottom IO chain ----
add("io1", 3.7, 1.8, 0.7, 0.45, "I/O", fill=(244, 244, 244), font_size=10)
add("io2", 5.0, 1.8, 1.4, 0.45, "I/O (Per batch)", fill=(244, 244, 244), font_size=10)
add("io3", 6.9, 1.8, 1.7, 0.45, "I/O (Cross-stage)", fill=(244, 244, 244), font_size=10)
add("io4", 9.1, 1.8, 2.1, 0.45, "I/O (Not in Network)", fill=(244, 244, 244), font_size=10)

# ---- links ----
connect("raw", "backbone_main")
connect("backbone_main", "neck_main", color=(245, 80, 20), weight=1.2)
connect("neck_main", "head_main", color=(245, 80, 20), weight=1.2)
connect("head_main", "nms", color=(245, 80, 20), weight=1.2)
connect("head_main", "loss", color=(245, 80, 20), weight=1.2)
connect("nms", "box_draw")
connect("nms", "io1")
connect("io1", "io2")
connect("io2", "io3", color=(245, 80, 20), weight=1.2)
connect("io3", "io4", color=(45, 60, 230), weight=1.2)

# backbone chain
bb_keys = [k for (k, _, _) in labels]
for a, b in zip(bb_keys[:-1], bb_keys[1:]):
    connect(a, b)

# backbone -> neck taps
connect("bb_c2f2", "neck_cat1", color=(245, 80, 20), weight=1.1)
connect("bb_c2f3", "neck_cat2", color=(245, 80, 20), weight=1.1)
connect("bb_sppf", "neck_cbs_top", color=(245, 80, 20), weight=1.1)

# neck internal
connect("neck_cbs_top", "neck_up2")
connect("neck_up2", "neck_cat2")
connect("neck_cat2", "neck_fad1")
connect("neck_fad1", "neck_up1")
connect("neck_up1", "neck_cat1")

connect("neck_cat1", "neck_fad2")
connect("neck_fad2", "neck_cbs1")
connect("neck_cbs1", "neck_cat3")
connect("neck_cat3", "neck_fad3")
connect("neck_fad3", "neck_cbs2")
connect("neck_cbs2", "neck_cat4")
connect("neck_cat4", "neck_fad4")

connect("neck_fad2", "detect", color=(245, 80, 20), weight=1.2)
connect("neck_fad3", "detect", color=(245, 80, 20), weight=1.2)
connect("neck_fad4", "detect", color=(245, 80, 20), weight=1.2)

# detail chains
connect("d_conv", "d_bn")
connect("d_bn", "d_silu")

connect("c2f_cbs_top", "c2f_split")
connect("c2f_split", "c2f_bottleneck")
connect("c2f_bottleneck", "c2f_c")
connect("c2f_c", "c2f_cbs_bottom")
connect("c2f_split", "c2f_c", color=(245, 80, 20), weight=1.1)

# detect -> io3
connect("detect", "io3")

# save
save_path = r"D:\\work\\png2vsdx\\demo\\vortexnet_arch_rebuild_20260317.vsdx"
save = post("/session/save", {"session_id": session_id, "save_path": save_path})

print(json.dumps({
    "session_id": session_id,
    "shape_count": len(created),
    "connector_count": len(connectors),
    "save": save,
    "save_path": save_path,
}, ensure_ascii=False, indent=2))
