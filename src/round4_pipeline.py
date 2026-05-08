"""Round 4: run the proposed stack on real multi-floor apartment buildings.

For each plan in samples/real_multifloor/manifest.json:
1. Detect walls (OpenCV adaptive).
2. Get building outline (largest concave hull / external contour of wall mask).
3. Ask Claude Opus 4.7 to anchor scale: "what is the approximate width of
   the building outline in meters?" (gives us px/m without needing dim labels).
4. Compute outline area in m² and net interior area (sum of room polygons).
5. Apply norm: gross = outline.buffer(0)  (already external);  net = sum(rooms).
6. Aggregate per building × per-instance and compare to manifest listed_total.
"""
from __future__ import annotations
import json, os, sys, time, math
import cv2
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(__file__))
from tools import detect_walls, extract_rooms, vlm_call, render_overlay, save_image


def building_outline(wall_mask_path: str) -> dict | None:
    """Approximate the building footprint as the largest external contour of the wall mask."""
    mask = cv2.imread(wall_mask_path, cv2.IMREAD_GRAYSCALE)
    H, W = mask.shape
    # Close gaps so the building is one blob
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    # Fill internal holes
    inv = cv2.bitwise_not(closed)
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    # Background = comp touching border with largest area
    bg = -1; bg_area = -1
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        if (x == 0 or y == 0 or x + w == W or y + h == H) and a > bg_area:
            bg, bg_area = i, a
    # Solid mask = NOT background
    solid = np.where(lbl == bg, 0, 255).astype(np.uint8)
    contours, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    if not contours:
        return None
    cnt = max(contours, key=cv2.contourArea)
    if cv2.contourArea(cnt) < 1000:
        return None
    pts = cnt.squeeze(1).tolist()
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    x, y, w, h = cv2.boundingRect(cnt)
    return {
        "polygon_px": pts,
        "area_px": float(poly.area),
        "bbox_px": [int(x), int(y), int(x + w), int(y + h)],
        "width_px": int(w),
        "height_px": int(h),
    }


VLM_PROMPT = (
    "This is an architectural floor plan of a building. Estimate, in metres, "
    "the approximate horizontal width of the building's outer walls (the bounding "
    "rectangle of the building footprint as drawn on the page). Use door arcs "
    "(typically 0.9 m) and bathroom fixtures (toilet ~0.7 m, bathtub ~1.7 m) as "
    "reference if no dimension labels are visible. Return ONLY JSON: "
    "{\"building_width_m\": <float>, \"building_depth_m\": <float>, "
    "\"reasoning\": \"<one short sentence>\"}. Numbers only, no markdown."
)


def parse_json(text: str) -> dict | None:
    text = text.strip()
    import re
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1).strip()
    s, e = text.find("{"), text.rfind("}")
    if s == -1 or e == -1:
        return None
    try:
        return json.loads(text[s:e+1])
    except Exception:
        return None


def measure_floor(image_path: str, model: str = "claude-opus-4-7") -> dict:
    """Run the full pipeline on one floor plan."""
    walls = detect_walls(image_path)
    outline = building_outline(walls["wall_mask_path"])
    if not outline:
        return {"image": image_path, "error": "no_outline"}

    t0 = time.time()
    vlm = vlm_call(image_path, VLM_PROMPT, model=model, timeout_s=300)
    vlm_dt = time.time() - t0
    parsed = parse_json(vlm["stdout"]) if vlm["ok"] else None
    if not parsed or "building_width_m" not in parsed:
        return {"image": image_path, "error": "vlm_no_json",
                "vlm_seconds": round(vlm_dt, 1), "vlm_stdout_head": (vlm["stdout"] or "")[:300]}

    width_m = float(parsed["building_width_m"])
    px_per_m_w = outline["width_px"] / width_m if width_m > 0 else None
    # Cross-check with depth (height)
    depth_m = float(parsed.get("building_depth_m") or 0)
    px_per_m_h = outline["height_px"] / depth_m if depth_m > 0 else None
    # Use the average if both available; require ratio_consistency > 0.7
    if px_per_m_w and px_per_m_h:
        cons = min(px_per_m_w, px_per_m_h) / max(px_per_m_w, px_per_m_h)
        px_per_m = (px_per_m_w + px_per_m_h) / 2 if cons > 0.7 else px_per_m_w
    else:
        px_per_m = px_per_m_w
        cons = None

    if not px_per_m or px_per_m <= 0:
        return {"image": image_path, "error": "bad_scale"}

    floor_area_m2 = round(outline["area_px"] / (px_per_m ** 2), 2)
    img = cv2.imread(image_path)
    base = os.path.splitext(os.path.basename(image_path))[0]
    overlay = img.copy()
    poly_np = np.array(outline["polygon_px"], np.int32)
    cv2.polylines(overlay, [poly_np], True, (0, 0, 255), 4)
    cv2.putText(overlay, f"{floor_area_m2} m2 (px/m={px_per_m:.1f})",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    out = f"out/round4/{base}.outline.png"
    save_image(overlay, out)

    return {
        "image": image_path,
        "vlm_model": model,
        "vlm_seconds": round(vlm_dt, 1),
        "vlm_width_m": width_m,
        "vlm_depth_m": depth_m,
        "vlm_reasoning": parsed.get("reasoning"),
        "outline_width_px": outline["width_px"],
        "outline_height_px": outline["height_px"],
        "outline_area_px": int(outline["area_px"]),
        "px_per_m": round(px_per_m, 2),
        "scale_consistency_w_h": round(cons, 3) if cons else None,
        "floor_area_m2": floor_area_m2,
        "overlay": out,
    }


def main():
    os.makedirs("out/round4", exist_ok=True)
    with open("samples/real_multifloor/manifest.json") as f:
        manifest = json.load(f)

    by_building = {}
    for b in manifest["buildings"]:
        bid = b["id"]
        listed = b["listed_total_m2"]
        floors_above = b["floors_above_ground"]
        floors_below = b.get("floors_below_ground", 0)
        per_plan = []
        sum_m2 = 0.0
        for plan in b["plans"]:
            img = f"samples/real_multifloor/{plan['file']}"
            r = measure_floor(img)
            r["level"] = plan["level"]
            r["instances"] = plan["instances"]
            per_plan.append(r)
            if "floor_area_m2" in r:
                sum_m2 += r["floor_area_m2"] * plan["instances"]
            print(f"{bid} | {plan['file']} | {r}")
        diff_pct = (sum_m2 - listed) / listed * 100 if listed else None
        by_building[bid] = {
            "title": b["title"],
            "year": b["year"],
            "city": b["city_country"],
            "listed_total_m2": listed,
            "floors_above": floors_above,
            "floors_below": floors_below,
            "instances_total": sum(p["instances"] for p in b["plans"]),
            "pipeline_total_m2": round(sum_m2, 2),
            "deviation_pct": round(diff_pct, 1) if diff_pct is not None else None,
            "per_plan": per_plan,
        }

    with open("out/round4/results.json", "w") as f:
        json.dump(by_building, f, indent=2, ensure_ascii=False)
    print("\nWrote out/round4/results.json")
    for bid, d in by_building.items():
        print(f"\n=== {bid} {d['title']} ===")
        print(f"  listed:   {d['listed_total_m2']} m²")
        print(f"  pipeline: {d['pipeline_total_m2']} m²")
        print(f"  deviation: {d['deviation_pct']} %")


if __name__ == "__main__":
    main()
