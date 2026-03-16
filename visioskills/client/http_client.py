from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


@dataclass
class BridgeConfig:
    base_url: str
    token: Optional[str] = None
    timeout_s: float = 30.0


class VisioBridgeClient:
    def __init__(self, config: BridgeConfig):
        self.config = config

    def _headers(self) -> Dict[str, str]:
        h: Dict[str, str] = {"Content-Type": "application/json"}
        if self.config.token:
            h["Authorization"] = f"Bearer {self.config.token}"
        return h

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if "request_id" not in payload:
            payload["request_id"] = str(uuid.uuid4())
        r = requests.post(
            f"{self.config.base_url}{path}",
            json=payload,
            headers=self._headers(),
            timeout=self.config.timeout_s,
        )
        r.raise_for_status()
        return r.json()

    def health(self) -> Dict[str, Any]:
        r = requests.get(f"{self.config.base_url}/health", timeout=self.config.timeout_s)
        r.raise_for_status()
        return r.json()

    def ping_visio(self) -> Dict[str, Any]:
        return self._post("/ping_visio", {})

    def create_session(self, file_path: Optional[str] = None, visible: bool = True) -> Dict[str, Any]:
        return self._post("/session/create", {"file_path": file_path, "visible": visible})

    def add_shape(
        self,
        session_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        shape_type: str = "Rectangle",
        text: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/shape/add",
            {
                "session_id": session_id,
                "shape_type": shape_type,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "text": text,
            },
        )

    def select_shape(self, session_id: str, shape_id: int) -> Dict[str, Any]:
        return self._post("/shape/select", {"session_id": session_id, "shape_id": shape_id})

    def update_shape_geometry(
        self,
        session_id: str,
        shape_id: int,
        x: Optional[float] = None,
        y: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/shape/update_geometry",
            {
                "session_id": session_id,
                "shape_id": shape_id,
                "x": x,
                "y": y,
                "width": width,
                "height": height,
            },
        )

    def set_text_style(
        self,
        session_id: str,
        shape_id: int,
        text: Optional[str] = None,
        font_name: Optional[str] = None,
        font_size_pt: Optional[float] = None,
        font_rgb: Optional[tuple[int, int, int]] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/shape/set_text_style",
            {
                "session_id": session_id,
                "shape_id": shape_id,
                "text": text,
                "font_name": font_name,
                "font_size_pt": font_size_pt,
                "font_rgb": font_rgb,
            },
        )

    def set_colors(
        self,
        session_id: str,
        shape_id: int,
        line_rgb: Optional[tuple[int, int, int]] = None,
        fill_rgb: Optional[tuple[int, int, int]] = None,
        line_weight_pt: Optional[float] = None,
    ) -> Dict[str, Any]:
        return self._post(
            "/shape/set_colors",
            {
                "session_id": session_id,
                "shape_id": shape_id,
                "line_rgb": line_rgb,
                "fill_rgb": fill_rgb,
                "line_weight_pt": line_weight_pt,
            },
        )

    def connect_shapes(self, session_id: str, from_shape_id: int, to_shape_id: int) -> Dict[str, Any]:
        return self._post(
            "/shape/connect",
            {"session_id": session_id, "from_shape_id": from_shape_id, "to_shape_id": to_shape_id},
        )

    def save_session(self, session_id: str, save_path: Optional[str] = None) -> Dict[str, Any]:
        return self._post("/session/save", {"session_id": session_id, "save_path": save_path})

    def close_session(self, session_id: str, save: bool = True) -> Dict[str, Any]:
        return self._post("/session/close", {"session_id": session_id, "save": save})
