"""End-to-end verification experiment.

Runs deterministic CV pipeline + VLM dimension reader on the same plan and
cross-checks them. Outputs a JSON record per sample plus an overlay PNG.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from tools import (
    auto_pipeline,
    detect_walls,
    extract_rooms,
    compute_areas,
    render_overlay,
    vlm_call,
)


VLM_DIMS_PROMPT = (
    "This is an architectural floor plan. Inside each room there is usually a "
    "written dimension W x H in meters (decimal). Read every visible room and "
    "return ONLY a JSON object of the form "
    "{\"rooms\":[{\"label\":\"bedroom\",\"w\":3.5,\"h\":4.0},...]}. "
    "If a room has no readable dimension, omit it. No prose, no markdown fences."
)

VLM_VERIFY_PROMPT = (
    "I have detected room polygons and overlaid them on the floor plan with "
    "computed areas. For each labelled overlay region, say whether the polygon "
    "looks plausible vs. the actual room boundary in the plan. Return JSON "
    "{\"verdicts\":[{\"id\":<int>,\"plausible\":true|false,\"note\":\"...\"}]} only."
)


def _parse_json_blob(text: str) -> dict | None:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def run_synthetic(image_path: str, gt_path: str, out_dir: str = "out") -> dict:
    with open(gt_path) as f:
        gt = json.load(f)
    res = auto_pipeline(image_path, scale_px_per_m=gt["px_per_m"], out_dir=out_dir)
    # match detected rooms to GT by bbox-IoU
    det = res["rooms"]
    matches = []
    for g in gt["rooms"]:
        gx1, gy1, gx2, gy2 = g["bbox_px"]
        best_id, best_iou = None, 0.0
        for d in det:
            dx1, dy1, dx2, dy2 = d["bbox_px"]
            ix1 = max(gx1, dx1)
            iy1 = max(gy1, dy1)
            ix2 = min(gx2, dx2)
            iy2 = min(gy2, dy2)
            if ix2 <= ix1 or iy2 <= iy1:
                continue
            inter = (ix2 - ix1) * (iy2 - iy1)
            union = (gx2 - gx1) * (gy2 - gy1) + (dx2 - dx1) * (dy2 - dy1) - inter
            iou = inter / union if union else 0
            if iou > best_iou:
                best_iou, best_id = iou, d["id"]
        det_room = next((d for d in det if d["id"] == best_id), None)
        if det_room is None:
            matches.append({"gt_name": g["name"], "matched": False})
            continue
        err = (det_room["area_m2"] - g["area_m2"]) / g["area_m2"]
        matches.append({
            "gt_name": g["name"],
            "matched": True,
            "iou": round(best_iou, 3),
            "gt_area_m2": g["area_m2"],
            "det_area_m2": det_room["area_m2"],
            "rel_err": round(err, 4),
        })
    matched = [m for m in matches if m["matched"]]
    summary = {
        "kind": "synthetic",
        "image": image_path,
        "gt_room_count": len(gt["rooms"]),
        "det_room_count": res["room_count"],
        "matched": len(matched),
        "mean_iou": round(float(np.mean([m["iou"] for m in matched])), 3) if matched else None,
        "mean_abs_rel_err": round(float(np.mean([abs(m["rel_err"]) for m in matched])), 4) if matched else None,
        "gt_total_m2": gt["total_area_m2"],
        "det_total_m2": res["total_area_m2"],
        "rel_err_total": round((res["total_area_m2"] - gt["total_area_m2"]) / gt["total_area_m2"], 4),
        "overlay": res["overlay_path"],
        "rooms": matches,
    }
    return summary


def run_real(image_path: str, model: str = "claude-sonnet-4-6",
             out_dir: str = "out") -> dict:
    base = os.path.splitext(os.path.basename(image_path))[0]
    walls = detect_walls(image_path)
    rooms_res = extract_rooms(walls["wall_mask_path"])

    t0 = time.time()
    vlm_dims = vlm_call(image_path, VLM_DIMS_PROMPT, model=model, timeout_s=420)
    dt_dims = time.time() - t0
    parsed = _parse_json_blob(vlm_dims["stdout"]) if vlm_dims["ok"] else None
    vlm_rooms = parsed.get("rooms", []) if parsed else []
    # fill missing area
    for r in vlm_rooms:
        try:
            w, h = float(r.get("w") or 0), float(r.get("h") or 0)
            r["area_m2"] = round(w * h, 2) if w and h else None
        except (TypeError, ValueError):
            r["area_m2"] = None
    vlm_total = round(sum(r["area_m2"] for r in vlm_rooms if r.get("area_m2")), 2)

    # Calibrate scale by matching the largest VLM area to the largest detected polygon
    det_sorted = sorted(rooms_res["rooms"], key=lambda d: -d["area_px"])
    vlm_with_area = sorted([r for r in vlm_rooms if r.get("area_m2")],
                           key=lambda r: -r["area_m2"])
    px_per_m = None
    if det_sorted and vlm_with_area:
        # Use 2nd-largest detected (skip the merged-corridor blob if huge)
        idx = 1 if len(det_sorted) > 1 else 0
        ref_det = det_sorted[idx]
        ref_vlm = vlm_with_area[idx if len(vlm_with_area) > idx else 0]
        if ref_vlm["area_m2"] > 0:
            px_per_m = (ref_det["area_px"] / ref_vlm["area_m2"]) ** 0.5
    if px_per_m:
        areas = compute_areas(rooms_res["rooms"], px_per_m)
    else:
        areas = {"rooms": rooms_res["rooms"], "total_area_m2": None}

    overlay_path = os.path.join(out_dir, f"{base}.overlay.png")
    render_overlay(image_path, areas["rooms"], overlay_path)

    return {
        "kind": "real",
        "image": image_path,
        "model": model,
        "vlm_call_seconds": round(dt_dims, 1),
        "vlm_ok": vlm_dims["ok"],
        "vlm_room_count": len(vlm_rooms),
        "vlm_total_m2": vlm_total,
        "det_room_count": rooms_res["room_count"],
        "px_per_m_calibrated": round(px_per_m, 2) if px_per_m else None,
        "det_total_m2": areas.get("total_area_m2"),
        "vlm_rooms": vlm_rooms,
        "det_rooms": [{"id": r["id"], "bbox_px": r["bbox_px"],
                       "area_px": r["area_px"],
                       "area_m2": r.get("area_m2")} for r in areas["rooms"]],
        "overlay": overlay_path,
        "vlm_raw_stdout": vlm_dims["stdout"][:1500],
    }


if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    results = []
    # Synthetic samples
    for img, gt in [
        ("samples/synth_clean.png", "samples/synth_clean.gt.json"),
        ("samples/synth_nodims.png", "samples/synth_nodims.gt.json"),
    ]:
        print(f"=== synthetic: {img} ===")
        r = run_synthetic(img, gt)
        results.append(r)
        print(json.dumps({k: v for k, v in r.items() if k != "rooms"}, indent=2))
    # Real samples (subset to keep total time bounded)
    for img in ["samples/hf_00.png", "samples/hf_01.png"]:
        print(f"=== real: {img} ===")
        r = run_real(img)
        results.append(r)
        print(json.dumps({k: v for k, v in r.items()
                          if k not in ("vlm_rooms", "det_rooms", "vlm_raw_stdout")},
                         indent=2))
    with open("out/results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote out/results.json")
