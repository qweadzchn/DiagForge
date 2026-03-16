from __future__ import annotations

import os
import queue
import threading
import uuid
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Dict, Optional


class VisioError(Exception):
    pass


@dataclass
class SessionState:
    session_id: str
    file_path: Optional[str]
    visible: bool
    doc_name: str


class _ComWorker:
    """Single-thread COM executor (STA).

    All Visio COM calls must pass through this worker to avoid thread-affinity issues.
    """

    def __init__(self) -> None:
        self._q: queue.Queue[tuple[Future, Any, tuple, dict]] = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def submit(self, fn, *args, **kwargs):
        fut: Future = Future()
        self._q.put((fut, fn, args, kwargs))
        return fut

    def _run(self) -> None:
        try:
            import pythoncom  # type: ignore

            pythoncom.CoInitialize()
        except Exception as e:  # pragma: no cover - executed on Windows runtime
            # keep worker alive; tasks will fail with this root cause
            init_error = e
        else:
            init_error = None

        while True:
            fut, fn, args, kwargs = self._q.get()
            if init_error is not None:
                fut.set_exception(VisioError(f"COM initialization failed: {init_error}"))
                continue
            try:
                result = fn(*args, **kwargs)
                fut.set_result(result)
            except Exception as e:  # pragma: no cover
                fut.set_exception(VisioError(str(e)))


class VisioAdapter:
    def __init__(self) -> None:
        self._worker = _ComWorker()
        self._sessions: Dict[str, SessionState] = {}
        self._sessions_lock = threading.Lock()

    # ---------- public API ----------
    def ping(self) -> str:
        return self._run_sync(self._ping_impl)

    def create_session(self, file_path: Optional[str], visible: bool) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        created = self._run_sync(self._create_or_open_doc_impl, session_id, file_path, visible)
        state = SessionState(
            session_id=session_id,
            file_path=file_path,
            visible=visible,
            doc_name=created["doc_name"],
        )
        with self._sessions_lock:
            self._sessions[session_id] = state
        return {"session_id": session_id, "file_path": file_path}

    def add_shape(
        self,
        session_id: str,
        page_name: Optional[str],
        shape_type: str,
        x: float,
        y: float,
        width: float,
        height: float,
        text: Optional[str],
    ) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(
            self._add_shape_impl,
            session_id,
            page_name,
            shape_type,
            x,
            y,
            width,
            height,
            text,
        )

    def select_shape(self, session_id: str, shape_id: int) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(self._select_shape_impl, session_id, shape_id)

    def update_shape_geometry(
        self,
        session_id: str,
        shape_id: int,
        x: Optional[float],
        y: Optional[float],
        width: Optional[float],
        height: Optional[float],
    ) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(self._update_shape_geometry_impl, session_id, shape_id, x, y, width, height)

    def set_shape_text_style(
        self,
        session_id: str,
        shape_id: int,
        text: Optional[str],
        font_name: Optional[str],
        font_size_pt: Optional[float],
        font_rgb: Optional[tuple[int, int, int]],
    ) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(
            self._set_shape_text_style_impl,
            session_id,
            shape_id,
            text,
            font_name,
            font_size_pt,
            font_rgb,
        )

    def set_shape_text_block(
        self,
        session_id: str,
        shape_id: int,
        txt_pin_x: Optional[float],
        txt_pin_y: Optional[float],
        txt_width: Optional[float],
        txt_height: Optional[float],
    ) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(
            self._set_shape_text_block_impl,
            session_id,
            shape_id,
            txt_pin_x,
            txt_pin_y,
            txt_width,
            txt_height,
        )

    def set_shape_colors(
        self,
        session_id: str,
        shape_id: int,
        line_rgb: Optional[tuple[int, int, int]],
        fill_rgb: Optional[tuple[int, int, int]],
        line_weight_pt: Optional[float],
    ) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(
            self._set_shape_colors_impl,
            session_id,
            shape_id,
            line_rgb,
            fill_rgb,
            line_weight_pt,
        )

    def align_shapes(self, session_id: str, shape_ids: list[int], mode: str) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(self._align_shapes_impl, session_id, shape_ids, mode)

    def distribute_shapes(self, session_id: str, shape_ids: list[int], axis: str) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(self._distribute_shapes_impl, session_id, shape_ids, axis)

    def connect_shapes(self, session_id: str, from_shape_id: int, to_shape_id: int, page_name: Optional[str]) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(self._connect_shapes_impl, session_id, from_shape_id, to_shape_id, page_name)

    def save_session(self, session_id: str, save_path: Optional[str]) -> Dict[str, Any]:
        self._assert_session(session_id)
        return self._run_sync(self._save_session_impl, session_id, save_path)

    def close_session(self, session_id: str, save: bool) -> Dict[str, Any]:
        self._assert_session(session_id)
        data = self._run_sync(self._close_session_impl, session_id, save)
        with self._sessions_lock:
            self._sessions.pop(session_id, None)
        return data

    # ---------- worker helpers ----------
    def _run_sync(self, fn, *args, timeout: float = 60.0, **kwargs):
        fut = self._worker.submit(fn, *args, **kwargs)
        return fut.result(timeout=timeout)

    def _assert_session(self, session_id: str) -> SessionState:
        with self._sessions_lock:
            s = self._sessions.get(session_id)
        if not s:
            raise VisioError(f"Unknown session_id: {session_id}")
        return s

    # ---------- COM impl ----------
    def _get_app(self):
        import win32com.client  # type: ignore

        app = win32com.client.Dispatch("Visio.Application")
        return app

    def _get_doc(self, app, session_id: str):
        state = self._assert_session(session_id)
        try:
            return app.Documents.Item(state.doc_name)
        except Exception as e:
            raise VisioError(f"No open Visio document bound to session {session_id} ({state.doc_name})") from e

    def _get_page(self, doc, page_name: Optional[str]):
        if page_name:
            return doc.Pages.ItemU(page_name)
        return doc.Pages.Item(1)

    def _ping_impl(self) -> str:
        app = self._get_app()
        return str(app.Version)

    def _create_or_open_doc_impl(self, session_id: str, file_path: Optional[str], visible: bool) -> Dict[str, Any]:
        app = self._get_app()
        app.Visible = visible

        if file_path and os.path.exists(file_path):
            doc = app.Documents.Open(file_path)
        elif file_path:
            doc = app.Documents.Add("")
            doc.SaveAs(file_path)
        else:
            doc = app.Documents.Add("")

        return {"ok": True, "doc_name": str(doc.Name)}

    def _add_shape_impl(
        self,
        session_id: str,
        page_name: Optional[str],
        shape_type: str,
        x: float,
        y: float,
        width: float,
        height: float,
        text: Optional[str],
    ) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, page_name)

        st = shape_type.lower()
        left = x - width / 2
        right = x + width / 2
        bottom = y - height / 2
        top = y + height / 2

        if st in {"rectangle", "rect", "box"}:
            shape = page.DrawRectangle(left, bottom, right, top)
        elif st in {"circle", "ellipse", "oval"}:
            shape = page.DrawOval(left, bottom, right, top)
        elif st in {"line"}:
            shape = page.DrawLine(left, bottom, right, top)
        else:
            # fallback rectangle for predictable behavior
            shape = page.DrawRectangle(left, bottom, right, top)

        if text is not None:
            shape.Text = text

        return {"shape_id": int(shape.ID), "name": str(shape.NameU), "page": str(page.NameU)}

    def _select_shape_impl(self, session_id: str, shape_id: int) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, None)
        shp = page.Shapes.ItemFromID(shape_id)
        window = app.ActiveWindow
        window.Select(shp, 2)  # 2 = visSelect
        return {"shape_id": shape_id, "selected": True}

    def _update_shape_geometry_impl(
        self,
        session_id: str,
        shape_id: int,
        x: Optional[float],
        y: Optional[float],
        width: Optional[float],
        height: Optional[float],
    ) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, None)
        shp = page.Shapes.ItemFromID(shape_id)

        if x is not None:
            shp.CellsU("PinX").ResultIU = float(x)
        if y is not None:
            shp.CellsU("PinY").ResultIU = float(y)
        if width is not None:
            shp.CellsU("Width").ResultIU = float(width)
        if height is not None:
            shp.CellsU("Height").ResultIU = float(height)

        return {"shape_id": shape_id, "updated": True}

    def _set_shape_text_style_impl(
        self,
        session_id: str,
        shape_id: int,
        text: Optional[str],
        font_name: Optional[str],
        font_size_pt: Optional[float],
        font_rgb: Optional[tuple[int, int, int]],
    ) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, None)
        shp = page.Shapes.ItemFromID(shape_id)

        if text is not None:
            shp.Text = text
        if font_name:
            # Use direct quoted face name for broad compatibility across Visio installs.
            shp.CellsU("Char.Font").FormulaU = f'"{font_name}"'
        if font_size_pt is not None:
            # Char.Size uses drawing units internally; keep explicit point unit.
            shp.CellsU("Char.Size").FormulaU = f"{float(font_size_pt)} pt"
        if font_rgb is not None:
            r, g, b = font_rgb
            shp.CellsU("Char.Color").FormulaU = f"RGB({int(r)},{int(g)},{int(b)})"

        return {"shape_id": shape_id, "updated": True}

    def _set_shape_text_block_impl(
        self,
        session_id: str,
        shape_id: int,
        txt_pin_x: Optional[float],
        txt_pin_y: Optional[float],
        txt_width: Optional[float],
        txt_height: Optional[float],
    ) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, None)
        shp = page.Shapes.ItemFromID(shape_id)

        if txt_pin_x is not None:
            shp.CellsU("TxtPinX").ResultIU = float(txt_pin_x)
        if txt_pin_y is not None:
            shp.CellsU("TxtPinY").ResultIU = float(txt_pin_y)
        if txt_width is not None:
            shp.CellsU("TxtWidth").ResultIU = float(txt_width)
        if txt_height is not None:
            shp.CellsU("TxtHeight").ResultIU = float(txt_height)

        return {"shape_id": shape_id, "updated": True}

    def _set_shape_colors_impl(
        self,
        session_id: str,
        shape_id: int,
        line_rgb: Optional[tuple[int, int, int]],
        fill_rgb: Optional[tuple[int, int, int]],
        line_weight_pt: Optional[float],
    ) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, None)
        shp = page.Shapes.ItemFromID(shape_id)

        if line_rgb is not None:
            r, g, b = line_rgb
            shp.CellsU("LineColor").FormulaU = f"RGB({int(r)},{int(g)},{int(b)})"
        if fill_rgb is not None:
            r, g, b = fill_rgb
            shp.CellsU("FillForegnd").FormulaU = f"RGB({int(r)},{int(g)},{int(b)})"
        if line_weight_pt is not None:
            shp.CellsU("LineWeight").FormulaU = f"{float(line_weight_pt)} pt"

        return {"shape_id": shape_id, "updated": True}

    def _align_shapes_impl(self, session_id: str, shape_ids: list[int], mode: str) -> Dict[str, Any]:
        if len(shape_ids) < 2:
            raise VisioError("align requires at least 2 shapes")

        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, None)
        shapes = [page.Shapes.ItemFromID(int(sid)) for sid in shape_ids]
        anchor = shapes[0]

        def edge(shp, which: str) -> float:
            px = shp.CellsU("PinX").ResultIU
            py = shp.CellsU("PinY").ResultIU
            w = shp.CellsU("Width").ResultIU
            h = shp.CellsU("Height").ResultIU
            if which == "left":
                return px - w / 2
            if which == "right":
                return px + w / 2
            if which == "top":
                return py + h / 2
            if which == "bottom":
                return py - h / 2
            if which == "center_x":
                return px
            if which == "center_y":
                return py
            raise VisioError(f"unsupported align mode: {which}")

        ref = edge(anchor, mode)
        for shp in shapes[1:]:
            w = shp.CellsU("Width").ResultIU
            h = shp.CellsU("Height").ResultIU
            if mode == "left":
                shp.CellsU("PinX").ResultIU = ref + w / 2
            elif mode == "right":
                shp.CellsU("PinX").ResultIU = ref - w / 2
            elif mode == "center_x":
                shp.CellsU("PinX").ResultIU = ref
            elif mode == "top":
                shp.CellsU("PinY").ResultIU = ref - h / 2
            elif mode == "bottom":
                shp.CellsU("PinY").ResultIU = ref + h / 2
            elif mode == "center_y":
                shp.CellsU("PinY").ResultIU = ref
            else:
                raise VisioError(f"unsupported align mode: {mode}")

        return {"aligned": len(shape_ids), "mode": mode}

    def _distribute_shapes_impl(self, session_id: str, shape_ids: list[int], axis: str) -> Dict[str, Any]:
        if len(shape_ids) < 3:
            raise VisioError("distribute requires at least 3 shapes")

        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, None)
        shapes = [page.Shapes.ItemFromID(int(sid)) for sid in shape_ids]

        if axis == "horizontal":
            shapes.sort(key=lambda s: s.CellsU("PinX").ResultIU)
            start = shapes[0].CellsU("PinX").ResultIU
            end = shapes[-1].CellsU("PinX").ResultIU
            gap = (end - start) / (len(shapes) - 1)
            for i, shp in enumerate(shapes[1:-1], start=1):
                shp.CellsU("PinX").ResultIU = start + i * gap
        elif axis == "vertical":
            shapes.sort(key=lambda s: s.CellsU("PinY").ResultIU)
            start = shapes[0].CellsU("PinY").ResultIU
            end = shapes[-1].CellsU("PinY").ResultIU
            gap = (end - start) / (len(shapes) - 1)
            for i, shp in enumerate(shapes[1:-1], start=1):
                shp.CellsU("PinY").ResultIU = start + i * gap
        else:
            raise VisioError("axis must be horizontal or vertical")

        return {"distributed": len(shape_ids), "axis": axis}

    def _connect_shapes_impl(self, session_id: str, from_shape_id: int, to_shape_id: int, page_name: Optional[str]) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        page = self._get_page(doc, page_name)

        src = page.Shapes.ItemFromID(from_shape_id)
        dst = page.Shapes.ItemFromID(to_shape_id)

        conn = page.Drop(app.ConnectorToolDataObject, 0, 0)
        self._glue_connector_end(conn, "BeginX", src)
        self._glue_connector_end(conn, "EndX", dst)

        return {"connector_id": int(conn.ID), "from_shape_id": from_shape_id, "to_shape_id": to_shape_id}

    def _glue_connector_end(self, connector, endpoint_cell: str, target_shape) -> None:
        cell = connector.CellsU(endpoint_cell)
        # Prefer 2D center pin; fallback to 1D line endpoints for line-like shapes.
        try:
            cell.GlueTo(target_shape.CellsU("PinX"))
            return
        except Exception:
            pass

        for fallback in ("BeginX", "EndX"):
            try:
                cell.GlueTo(target_shape.CellsU(fallback))
                return
            except Exception:
                continue

        raise VisioError(f"Cannot glue connector endpoint {endpoint_cell} to target shape {target_shape.ID}")

    def _save_session_impl(self, session_id: str, save_path: Optional[str]) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        if save_path:
            doc.SaveAs(save_path)
            return {"saved": True, "path": save_path}

        try:
            doc.Save()
            return {"saved": True, "path": str(getattr(doc, "Path", ""))}
        except Exception:
            # Unsaved new doc: fallback to user's Documents
            home = os.path.expanduser("~")
            fallback = os.path.join(home, "Documents", f"png2vsdx_autosave_{session_id[:8]}.vsdx")
            doc.SaveAs(fallback)
            return {"saved": True, "path": fallback}

    def _close_session_impl(self, session_id: str, save: bool) -> Dict[str, Any]:
        app = self._get_app()
        doc = self._get_doc(app, session_id)
        if save:
            doc.Save()
        doc.Close()
        return {"closed": True, "session_id": session_id}
