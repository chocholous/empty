"""Round 5: outline detector v2 = MitUNet wall mask + fill holes + largest component.

Replaces round 4's `building_outline` (OpenCV adaptive + raw external contour),
which was fooled by drawn property lines and terraces.

For each plan we run BOTH detectors (v1 and v2) and emit deviations vs listed
total in a single comparison table.
"""
from __future__ import annotations
import json, os, sys, time, re
import cv2
import numpy as np
import torch
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2
from shapely.geometry import Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(__file__))
from tools import detect_walls, vlm_call, save_image
from round4_pipeline import building_outline as outline_v1, parse_json, VLM_PROMPT


# ---------- MitUNet single-instance loader ----------
WEIGHTS = "models/mitunet/experiments/models/mitunet_finetune_a6_mit_b4_tversky_8864_28E.pth"

_TRANSFORM = A.Compose([
    A.Resize(512, 512),
    A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)),
    ToTensorV2(),
])

_model_cache = {}


def get_mitunet():
    if "m" not in _model_cache:
        aux = smp.Segformer(encoder_name="mit_b4", encoder_weights=None)
        m = smp.Unet(encoder_name="mit_b4", encoder_weights=None,
                     in_channels=3, classes=1, decoder_attention_type="scse")
        m.encoder = aux.encoder
        sd = torch.load(WEIGHTS, map_location="cpu", weights_only=False)
        m.load_state_dict(sd)
        m.eval()
        _model_cache["m"] = m
    return _model_cache["m"]


def mitunet_wall_mask(image_path: str) -> np.ndarray:
    img = cv2.imread(image_path)
    H, W = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    x = _TRANSFORM(image=rgb)["image"].unsqueeze(0)
    with torch.no_grad():
        prob = torch.sigmoid(get_mitunet()(x)).squeeze().numpy()
    mask = (prob > 0.5).astype(np.uint8) * 255
    return cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)


def outline_v2(image_path: str, *, dilate_px: int = 10) -> dict | None:
    """v2 outline: MitUNet wall mask -> dilate -> largest non-bg connected component
    after hole-fill. Avoids dashed property lines and external terraces because
    MitUNet doesn't predict them as walls."""
    mit = mitunet_wall_mask(image_path)
    H, W = mit.shape
    # Dilate to bridge thin gaps in MitUNet output (1-2 px walls after resize-back)
    thick = cv2.dilate(mit, np.ones((dilate_px, dilate_px), np.uint8))
    # Fill holes by inverting and finding the background blob
    inv = cv2.bitwise_not(thick)
    n, lbl, stats, _ = cv2.connectedComponentsWithStats(inv, connectivity=4)
    bg, bg_area = -1, -1
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        if (x == 0 or y == 0 or x + w == W or y + h == H) and a > bg_area:
            bg, bg_area = i, a
    solid = np.where(lbl == bg, 0, 255).astype(np.uint8)
    cnts, _ = cv2.findContours(solid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    if not cnts:
        return None
    cnt = max(cnts, key=cv2.contourArea)
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


def measure_floor_v2(image_path: str, model: str = "claude-opus-4-7") -> dict:
    """Run pipeline using BOTH outline_v1 (CV adaptive contour) and outline_v2 (MitUNet hull)."""
    out = {"image": image_path}
    walls = detect_walls(image_path)
    o1 = outline_v1(walls["wall_mask_path"])
    t0 = time.time()
    o2 = outline_v2(image_path)
    out["mitunet_seconds"] = round(time.time() - t0, 2)

    t0 = time.time()
    vlm = vlm_call(image_path, VLM_PROMPT, model=model, timeout_s=300)
    out["vlm_seconds"] = round(time.time() - t0, 2)
    parsed = parse_json(vlm["stdout"]) if vlm["ok"] else None
    if not parsed or "building_width_m" not in parsed:
        out["error"] = "vlm_no_json"
        out["vlm_stdout_head"] = (vlm["stdout"] or "")[:200]
        return out

    width_m = float(parsed["building_width_m"])
    depth_m = float(parsed.get("building_depth_m") or 0)
    out["vlm_width_m"] = width_m
    out["vlm_depth_m"] = depth_m
    out["vlm_reasoning"] = parsed.get("reasoning")

    for tag, o in [("v1_cv_adaptive", o1), ("v2_mitunet_hull", o2)]:
        if o is None:
            out[tag] = {"error": "no_outline"}
            continue
        px_per_m_w = o["width_px"] / width_m if width_m > 0 else 0
        px_per_m_h = o["height_px"] / depth_m if depth_m > 0 else 0
        if px_per_m_w and px_per_m_h:
            cons = min(px_per_m_w, px_per_m_h) / max(px_per_m_w, px_per_m_h)
            px_per_m = (px_per_m_w + px_per_m_h) / 2 if cons > 0.7 else px_per_m_w
        else:
            px_per_m = px_per_m_w or px_per_m_h
            cons = None
        floor_area = round(o["area_px"] / (px_per_m ** 2), 2) if px_per_m > 0 else None
        out[tag] = {
            "outline_width_px": o["width_px"],
            "outline_height_px": o["height_px"],
            "outline_area_px": int(o["area_px"]),
            "px_per_m": round(px_per_m, 2) if px_per_m else None,
            "scale_consistency_w_h": round(cons, 3) if cons else None,
            "floor_area_m2": floor_area,
        }

    # Side-by-side overlay
    img = cv2.imread(image_path)
    base = os.path.splitext(os.path.basename(image_path))[0]
    H, W = img.shape[:2]
    panel = np.zeros((H, W * 2 + 20, 3), np.uint8) + 255
    panel[:, :W] = img
    panel[:, W + 20:] = img
    if o1:
        cv2.polylines(panel[:, :W], [np.array(o1["polygon_px"], np.int32)], True, (0, 0, 255), 4)
        cv2.putText(panel[:, :W], f"v1 {out['v1_cv_adaptive'].get('floor_area_m2','-')} m2",
                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 4)
    if o2:
        cv2.polylines(panel[:, W + 20:], [np.array(o2["polygon_px"], np.int32)], True, (255, 0, 0), 4)
        cv2.putText(panel[:, W + 20:], f"v2 {out['v2_mitunet_hull'].get('floor_area_m2','-')} m2",
                    (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (255, 0, 0), 4)
    save_image(panel, f"out/round5/{base}.compare.png")
    out["compare_overlay"] = f"out/round5/{base}.compare.png"
    return out


def main():
    os.makedirs("out/round5", exist_ok=True)
    with open("samples/real_multifloor/manifest.json") as f:
        manifest = json.load(f)

    # Warm up MitUNet (loading + first inference is the slow bit)
    print("Loading MitUNet...")
    _ = get_mitunet()

    by_building = {}
    for b in manifest["buildings"]:
        bid = b["id"]
        listed = b["listed_total_m2"]
        per_plan = []
        sums = {"v1_cv_adaptive": 0.0, "v2_mitunet_hull": 0.0}
        for plan in b["plans"]:
            img = f"samples/real_multifloor/{plan['file']}"
            r = measure_floor_v2(img)
            r["level"] = plan["level"]
            r["instances"] = plan["instances"]
            per_plan.append(r)
            for tag in sums:
                fa = r.get(tag, {}).get("floor_area_m2")
                if fa:
                    sums[tag] += fa * plan["instances"]
            print(f"{bid} | {plan['file']} | "
                  f"v1={r.get('v1_cv_adaptive', {}).get('floor_area_m2','-')} m2 "
                  f"v2={r.get('v2_mitunet_hull', {}).get('floor_area_m2','-')} m2 "
                  f"vlm={r.get('vlm_width_m','-')}x{r.get('vlm_depth_m','-')} m")

        deviations = {tag: (round((s - listed) / listed * 100, 1) if listed else None)
                      for tag, s in sums.items()}
        by_building[bid] = {
            "title": b["title"],
            "listed_total_m2": listed,
            "per_plan": per_plan,
            "v1_pipeline_total_m2": round(sums["v1_cv_adaptive"], 2),
            "v2_pipeline_total_m2": round(sums["v2_mitunet_hull"], 2),
            "v1_deviation_pct": deviations["v1_cv_adaptive"],
            "v2_deviation_pct": deviations["v2_mitunet_hull"],
        }

    with open("out/round5/results.json", "w") as f:
        json.dump(by_building, f, indent=2, ensure_ascii=False)
    print("\nWrote out/round5/results.json")
    print("\n=== Summary ===")
    for bid, d in by_building.items():
        print(f"\n{d['title']:35s}  listed={d['listed_total_m2']} m²")
        print(f"  v1 (CV adaptive contour):  {d['v1_pipeline_total_m2']:>9} m²   {d['v1_deviation_pct']:+}%")
        print(f"  v2 (MitUNet hull):         {d['v2_pipeline_total_m2']:>9} m²   {d['v2_deviation_pct']:+}%")


if __name__ == "__main__":
    main()
