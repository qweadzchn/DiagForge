from __future__ import annotations

import os
import re
import threading
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

try:
    from .visio_adapter import VisioAdapter, VisioError
except ImportError:  # allows `uvicorn app:app` from this directory
    from visio_adapter import VisioAdapter, VisioError


APP_NAME = "png2vsdx-visio-bridge"
APP_VERSION = "0.1.0"
TOKEN_ENV = "VISIO_BRIDGE_TOKEN"
EXPORT_DIR_ENV = "VISIO_BRIDGE_EXPORT_DIR"
DEFAULT_EXPORT_DIR = r"D:\work\png2vsdx\exports"
EXPORT_TICKET_TTL_S = 300


class HealthResponse(BaseModel):
    ok: bool
    service: str
    version: str


class PingVisioResponse(BaseModel):
    ok: bool
    visio_version: str


class SessionCreateRequest(BaseModel):
    request_id: str
    file_path: Optional[str] = None
    visible: bool = True


class SessionCreateResponse(BaseModel):
    session_id: str
    file_path: Optional[str] = None


class AddShapeRequest(BaseModel):
    request_id: str
    session_id: str
    page_name: Optional[str] = None
    shape_type: str = Field(default="Rectangle")
    x: float
    y: float
    width: float = 1.8
    height: float = 1.0
    text: Optional[str] = None


class UpdateShapeGeometryRequest(BaseModel):
    request_id: str
    session_id: str
    shape_id: int
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None


class SetShapeTextStyleRequest(BaseModel):
    request_id: str
    session_id: str
    shape_id: int
    text: Optional[str] = None
    font_name: Optional[str] = None
    font_size_pt: Optional[float] = None
    font_rgb: Optional[tuple[int, int, int]] = None


class SetShapeTextBlockRequest(BaseModel):
    request_id: str
    session_id: str
    shape_id: int
    txt_pin_x: Optional[float] = None
    txt_pin_y: Optional[float] = None
    txt_width: Optional[float] = None
    txt_height: Optional[float] = None


class SetShapeColorRequest(BaseModel):
    request_id: str
    session_id: str
    shape_id: int
    line_rgb: Optional[tuple[int, int, int]] = None
    fill_rgb: Optional[tuple[int, int, int]] = None
    line_weight_pt: Optional[float] = None


class AlignShapesRequest(BaseModel):
    request_id: str
    session_id: str
    shape_ids: list[int]
    mode: str = Field(description="left|right|center_x|top|bottom|center_y")


class DistributeShapesRequest(BaseModel):
    request_id: str
    session_id: str
    shape_ids: list[int]
    axis: str = Field(description="horizontal|vertical")


class ConnectShapesRequest(BaseModel):
    request_id: str
    session_id: str
    from_shape_id: int
    to_shape_id: int
    page_name: Optional[str] = None


class SaveSessionRequest(BaseModel):
    request_id: str
    session_id: str
    save_path: Optional[str] = None


class CloseSessionRequest(BaseModel):
    request_id: str
    session_id: str
    save: bool = True


class ExportPagePngRequest(BaseModel):
    request_id: str
    session_id: str
    page_name: Optional[str] = None
    file_name: Optional[str] = None


class SelectShapeRequest(BaseModel):
    request_id: str
    session_id: str
    shape_id: int


class GenericOk(BaseModel):
    ok: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)


@dataclass
class RequestCacheEntry:
    payload: Dict[str, Any]


@dataclass
class ArtifactTicketEntry:
    file_path: str
    file_name: str
    media_type: str
    expires_at: float
    consumed: bool = False


class IdempotencyStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cache: Dict[str, RequestCacheEntry] = {}

    def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            entry = self._cache.get(request_id)
            return entry.payload if entry else None

    def put(self, request_id: str, payload: Dict[str, Any]) -> None:
        with self._lock:
            self._cache[request_id] = RequestCacheEntry(payload=payload)


class ArtifactTicketStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._tickets: Dict[str, ArtifactTicketEntry] = {}

    def _purge_expired_locked(self) -> None:
        now = time.time()
        expired = [k for k, v in self._tickets.items() if v.expires_at <= now]
        for k in expired:
            self._tickets.pop(k, None)

    def issue(self, *, file_path: str, file_name: str, media_type: str, ttl_s: int = EXPORT_TICKET_TTL_S) -> Dict[str, Any]:
        ticket = str(uuid.uuid4())
        expires_at = time.time() + max(1, int(ttl_s))
        entry = ArtifactTicketEntry(
            file_path=file_path,
            file_name=file_name,
            media_type=media_type,
            expires_at=expires_at,
            consumed=False,
        )
        with self._lock:
            self._purge_expired_locked()
            self._tickets[ticket] = entry

        return {
            "ticket": ticket,
            "expires_at_epoch": int(expires_at),
            "expires_in_s": int(expires_at - time.time()),
        }

    def consume(self, ticket: str) -> Optional[ArtifactTicketEntry]:
        with self._lock:
            self._purge_expired_locked()
            entry = self._tickets.get(ticket)
            if not entry or entry.consumed:
                return None
            entry.consumed = True
            return entry


app = FastAPI(title=APP_NAME, version=APP_VERSION)
adapter = VisioAdapter()
idempotency = IdempotencyStore()
artifact_tickets = ArtifactTicketStore()


def _check_auth(authorization: Optional[str]) -> None:
    expected = os.environ.get(TOKEN_ENV)
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != expected:
        raise HTTPException(status_code=403, detail="Invalid Bearer token")


def _idempotent(request_id: str, payload_builder) -> Dict[str, Any]:
    cached = idempotency.get(request_id)
    if cached is not None:
        return cached
    payload = payload_builder()
    idempotency.put(request_id, payload)
    return payload


def _export_dir() -> str:
    base = os.environ.get(EXPORT_DIR_ENV, DEFAULT_EXPORT_DIR)
    return os.path.abspath(base)


def _normalize_export_file_name(session_id: str, request_id: str, file_name: Optional[str]) -> str:
    if not file_name:
        return f"{session_id[:8]}_{request_id[:8]}.png"

    if os.path.basename(file_name) != file_name:
        raise HTTPException(status_code=400, detail="file_name must not include path separators")

    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", file_name):
        raise HTTPException(status_code=400, detail="file_name contains unsupported characters")

    if not file_name.lower().endswith(".png"):
        raise HTTPException(status_code=400, detail="Only .png export is supported")

    return file_name


def _safe_export_path(file_name: str) -> str:
    out_dir = _export_dir()
    os.makedirs(out_dir, exist_ok=True)

    full = os.path.abspath(os.path.join(out_dir, file_name))
    if os.path.commonpath([full, out_dir]) != out_dir:
        raise HTTPException(status_code=400, detail="Resolved export path escapes export directory")

    return full


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True, service=APP_NAME, version=APP_VERSION)


@app.post("/ping_visio", response_model=PingVisioResponse)
def ping_visio(authorization: Optional[str] = Header(default=None)) -> PingVisioResponse:
    _check_auth(authorization)
    try:
        version = adapter.ping()
        return PingVisioResponse(ok=True, visio_version=version)
    except VisioError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/session/create", response_model=SessionCreateResponse)
def create_session(req: SessionCreateRequest, authorization: Optional[str] = Header(default=None)) -> SessionCreateResponse:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        session = adapter.create_session(file_path=req.file_path, visible=req.visible)
        return {"session_id": session["session_id"], "file_path": session.get("file_path")}

    payload = _idempotent(req.request_id, op)
    return SessionCreateResponse(**payload)


@app.post("/shape/add", response_model=GenericOk)
def add_shape(req: AddShapeRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.add_shape(
            session_id=req.session_id,
            page_name=req.page_name,
            shape_type=req.shape_type,
            x=req.x,
            y=req.y,
            width=req.width,
            height=req.height,
            text=req.text,
        )
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/select", response_model=GenericOk)
def select_shape(req: SelectShapeRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.select_shape(req.session_id, req.shape_id)
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/update_geometry", response_model=GenericOk)
def update_geometry(req: UpdateShapeGeometryRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.update_shape_geometry(
            session_id=req.session_id,
            shape_id=req.shape_id,
            x=req.x,
            y=req.y,
            width=req.width,
            height=req.height,
        )
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/set_text_style", response_model=GenericOk)
def set_text_style(req: SetShapeTextStyleRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.set_shape_text_style(
            session_id=req.session_id,
            shape_id=req.shape_id,
            text=req.text,
            font_name=req.font_name,
            font_size_pt=req.font_size_pt,
            font_rgb=req.font_rgb,
        )
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/set_text_block", response_model=GenericOk)
def set_text_block(req: SetShapeTextBlockRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.set_shape_text_block(
            session_id=req.session_id,
            shape_id=req.shape_id,
            txt_pin_x=req.txt_pin_x,
            txt_pin_y=req.txt_pin_y,
            txt_width=req.txt_width,
            txt_height=req.txt_height,
        )
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/set_colors", response_model=GenericOk)
def set_colors(req: SetShapeColorRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.set_shape_colors(
            session_id=req.session_id,
            shape_id=req.shape_id,
            line_rgb=req.line_rgb,
            fill_rgb=req.fill_rgb,
            line_weight_pt=req.line_weight_pt,
        )
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/align", response_model=GenericOk)
def align_shapes(req: AlignShapesRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.align_shapes(req.session_id, req.shape_ids, req.mode)
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/distribute", response_model=GenericOk)
def distribute_shapes(req: DistributeShapesRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.distribute_shapes(req.session_id, req.shape_ids, req.axis)
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/shape/connect", response_model=GenericOk)
def connect_shapes(req: ConnectShapesRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.connect_shapes(
            session_id=req.session_id,
            from_shape_id=req.from_shape_id,
            to_shape_id=req.to_shape_id,
            page_name=req.page_name,
        )
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/session/save", response_model=GenericOk)
def save_session(req: SaveSessionRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.save_session(req.session_id, req.save_path)
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/session/close", response_model=GenericOk)
def close_session(req: CloseSessionRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        data = adapter.close_session(req.session_id, req.save)
        return {"ok": True, "data": data}

    return GenericOk(**_idempotent(req.request_id, op))


@app.post("/session/export_png", response_model=GenericOk)
def export_session_png(req: ExportPagePngRequest, authorization: Optional[str] = Header(default=None)) -> GenericOk:
    _check_auth(authorization)

    def op() -> Dict[str, Any]:
        file_name = _normalize_export_file_name(req.session_id, req.request_id, req.file_name)
        export_path = _safe_export_path(file_name)
        exported = adapter.export_page_png(req.session_id, req.page_name, export_path)

        ticket = artifact_tickets.issue(
            file_path=export_path,
            file_name=file_name,
            media_type="image/png",
            ttl_s=EXPORT_TICKET_TTL_S,
        )

        return {
            "ok": True,
            "data": {
                **exported,
                "download": {
                    **ticket,
                    "url": f"/artifact/download/{ticket['ticket']}",
                    "one_time": True,
                },
            },
        }

    try:
        return GenericOk(**_idempotent(req.request_id, op))
    except VisioError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/artifact/download/{ticket}")
def download_artifact(ticket: str, authorization: Optional[str] = Header(default=None)):
    _check_auth(authorization)
    entry = artifact_tickets.consume(ticket)
    if entry is None:
        raise HTTPException(status_code=404, detail="Invalid/expired/consumed ticket")

    if not os.path.isfile(entry.file_path):
        raise HTTPException(status_code=404, detail="Artifact file no longer exists")

    return FileResponse(path=entry.file_path, media_type=entry.media_type, filename=entry.file_name)
