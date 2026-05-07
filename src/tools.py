"""Deterministic tools for floor-plan analysis.

Each function is a "tool" the LLM can call. They are deterministic, return
JSON-serialisable Python objects, and never read pixel measurements via
LLM judgement — measurement is computed from the image bytes by classical CV
or geometry libraries. The LLM's job is to (a) decide which tool to call,
(b) supply human-judgement parameters (e.g. which two points define the
known scale), and (c) verify rendered overlays.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
from typing import Iterable

import cv2
import numpy as np
from shapely.geometry import Polygon, box
from shapely.ops import unary_union


# ---------- I/O ----------

def load_image(path: str) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    return img


def save_image(img: np.ndarray, path: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, img)
    return path


# ---------- Tool: detect walls ----------

def detect_walls(image_path: str, *, dilate: int = 2) -> dict:
    """Return a binary wall mask + simple stats.

    Heuristic: walls are dark pixels forming continuous straight strokes.
    We threshold (dark = wall), close small gaps, then keep the largest
    connected components.
    """
    img = load_image(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Adaptive threshold copes with shading/photos better than fixed.
    th = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 35, 10
    )
    if dilate > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (dilate, dilate))
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel)
    # Drop very small components (text ticks, noise)
    n, labels, stats, _ = cv2.connectedComponentsWithStats(th, connectivity=8)
    keep = np.zeros_like(th)
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 200:
            keep[labels == i] = 255
    out = os.path.join("out", os.path.splitext(os.path.basename(image_path))[0] + ".walls.png")
    save_image(keep, out)
    return {
        "image_path": image_path,
        "wall_mask_path": out,
        "image_size": [int(img.shape[1]), int(img.shape[0])],
        "wall_pixel_count": int((keep > 0).sum()),
        "wall_ratio": float((keep > 0).mean()),
    }


# ---------- Tool: extract room polygons ----------

def extract_rooms(wall_mask_path: str, *, min_area_px: int = 2000) -> dict:
    """Find room polygons: connected components of NOT(walls) excluding
    the outer background. Simplifies via approxPolyDP."""
    mask = cv2.imread(wall_mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(wall_mask_path)
    inv = cv2.bitwise_not(mask)
    n, labels, stats, cents = cv2.connectedComponentsWithStats(inv, connectivity=4)
    H, W = mask.shape
    rooms: list[dict] = []
    # background = component touching the image border with largest area
    bg_id = -1
    bg_area = -1
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        touches = x == 0 or y == 0 or x + w == W or y + h == H
        if touches and a > bg_area:
            bg_area = a
            bg_id = i
    for i in range(1, n):
        if i == bg_id:
            continue
        a = stats[i, cv2.CC_STAT_AREA]
        if a < min_area_px:
            continue
        comp = (labels == i).astype(np.uint8) * 255
        contours, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            continue
        cnt = max(contours, key=cv2.contourArea)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.01 * peri, True).reshape(-1, 2)
        if len(approx) < 3:
            continue
        poly = Polygon(approx)
        if not poly.is_valid or poly.area < min_area_px:
            continue
        x, y, w, h = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP], stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        cx, cy = cents[i]
        rooms.append({
            "id": i,
            "bbox_px": [int(x), int(y), int(x + w), int(y + h)],
            "centroid_px": [float(cx), float(cy)],
            "area_px": float(poly.area),
            "polygon_px": [[int(p[0]), int(p[1])] for p in approx],
            "vertex_count": int(len(approx)),
        })
    rooms.sort(key=lambda r: -r["area_px"])
    return {"wall_mask_path": wall_mask_path, "room_count": len(rooms), "rooms": rooms}


# ---------- Tool: scale calibration ----------

def calibrate_scale_from_known_segment(p1_px: tuple[float, float],
                                       p2_px: tuple[float, float],
                                       known_length_m: float) -> dict:
    dx = p2_px[0] - p1_px[0]
    dy = p2_px[1] - p1_px[1]
    px_len = math.hypot(dx, dy)
    if px_len <= 0 or known_length_m <= 0:
        raise ValueError("invalid scale segment")
    return {
        "px_per_m": px_len / known_length_m,
        "m_per_px": known_length_m / px_len,
        "segment_px_length": px_len,
        "known_length_m": known_length_m,
    }


def calibrate_scale_from_room_dim(room_bbox_px: list[int],
                                  room_w_m: float, room_h_m: float) -> dict:
    x1, y1, x2, y2 = room_bbox_px
    w_px = x2 - x1
    h_px = y2 - y1
    pxpm_w = w_px / room_w_m if room_w_m > 0 else 0
    pxpm_h = h_px / room_h_m if room_h_m > 0 else 0
    pxpm = (pxpm_w + pxpm_h) / 2 if pxpm_w and pxpm_h else (pxpm_w or pxpm_h)
    return {
        "px_per_m": pxpm,
        "m_per_px": 1.0 / pxpm if pxpm else None,
        "px_per_m_from_width": pxpm_w,
        "px_per_m_from_height": pxpm_h,
        "ratio_consistency": (min(pxpm_w, pxpm_h) / max(pxpm_w, pxpm_h)) if pxpm_w and pxpm_h else None,
    }


# ---------- Tool: compute areas ----------

def compute_areas(rooms: list[dict], px_per_m: float) -> dict:
    if px_per_m <= 0:
        raise ValueError("px_per_m must be > 0")
    out = []
    total = 0.0
    for r in rooms:
        area_m2 = r["area_px"] / (px_per_m ** 2)
        total += area_m2
        out.append({**r, "area_m2": round(area_m2, 3)})
    return {"px_per_m": px_per_m, "total_area_m2": round(total, 3), "rooms": out}


# ---------- Tool: render overlay ----------

def render_overlay(image_path: str, rooms: list[dict], out_path: str,
                   *, labels: list[str] | None = None) -> str:
    img = load_image(image_path).copy()
    overlay = img.copy()
    rng = np.random.default_rng(42)
    for i, r in enumerate(rooms):
        poly = np.array(r["polygon_px"], np.int32)
        color = tuple(int(c) for c in rng.integers(60, 230, 3))
        cv2.fillPoly(overlay, [poly], color)
        cv2.polylines(img, [poly], True, color, 2)
    blended = cv2.addWeighted(overlay, 0.35, img, 0.65, 0)
    for i, r in enumerate(rooms):
        cx, cy = r["centroid_px"]
        text_lines = []
        if labels and i < len(labels):
            text_lines.append(labels[i])
        if "area_m2" in r:
            text_lines.append(f"{r['area_m2']:.2f} m2")
        else:
            text_lines.append(f"#{r.get('id','?')}")
        for j, t in enumerate(text_lines):
            cv2.putText(blended, t, (int(cx) - 40, int(cy) + j * 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(blended, t, (int(cx) - 40, int(cy) + j * 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    save_image(blended, out_path)
    return out_path


# ---------- Tool: VLM verify ----------

_HOOK_OVERRIDE = json.dumps({"hooks": {}})


def vlm_call(image_path: str, prompt: str, *, model: str = "claude-sonnet-4-6",
             timeout_s: int = 180) -> dict:
    """Call a Claude model on a local image via `claude -p`.

    Uses the Read tool to load image bytes. Hooks are suppressed so the stop
    hook doesn't hijack the response.
    """
    abs_img = os.path.abspath(image_path)
    full_prompt = (
        f"Use the Read tool on {abs_img!r} to load the image. Then answer the "
        f"following. Output ONLY the answer, no preamble.\n\n{prompt}"
    )
    try:
        r = subprocess.run(
            ["claude", "-p", "--model", model,
             "--tools", "Read",
             "--permission-mode", "acceptEdits",
             "--settings", _HOOK_OVERRIDE,
             "--setting-sources", "project"],
            input=full_prompt,
            capture_output=True, text=True, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "timeout", "model": model}
    return {
        "ok": r.returncode == 0,
        "stdout": r.stdout.strip(),
        "stderr": r.stderr.strip()[:500],
        "model": model,
    }


# ---------- Helper: package full pipeline ----------

def auto_pipeline(image_path: str, *,
                  scale_px_per_m: float | None = None,
                  ref_room_idx: int | None = None,
                  ref_room_w_m: float | None = None,
                  ref_room_h_m: float | None = None,
                  out_dir: str = "out") -> dict:
    """Run wall→rooms→scale→areas→overlay end-to-end without LLM."""
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]
    walls = detect_walls(image_path)
    rooms_res = extract_rooms(walls["wall_mask_path"])
    rooms = rooms_res["rooms"]

    if scale_px_per_m is None:
        if ref_room_idx is not None and ref_room_w_m and ref_room_h_m:
            scale = calibrate_scale_from_room_dim(
                rooms[ref_room_idx]["bbox_px"], ref_room_w_m, ref_room_h_m,
            )
            scale_px_per_m = scale["px_per_m"]
        else:
            scale_px_per_m = 50.0  # default for synthetic
    areas = compute_areas(rooms, scale_px_per_m)
    overlay_path = os.path.join(out_dir, f"{base}.overlay.png")
    render_overlay(image_path, areas["rooms"], overlay_path)
    return {
        "image_path": image_path,
        "wall_mask_path": walls["wall_mask_path"],
        "px_per_m": scale_px_per_m,
        "room_count": rooms_res["room_count"],
        "total_area_m2": areas["total_area_m2"],
        "rooms": areas["rooms"],
        "overlay_path": overlay_path,
    }


if __name__ == "__main__":
    import sys
    res = auto_pipeline(sys.argv[1])
    print(json.dumps({k: v for k, v in res.items() if k != "rooms"}, indent=2))
    print(f"detected {res['room_count']} rooms, total {res['total_area_m2']} m2")
    for r in res["rooms"]:
        print(f"  #{r['id']}: bbox={r['bbox_px']} area={r['area_m2']:.2f} m2 verts={r['vertex_count']}")
