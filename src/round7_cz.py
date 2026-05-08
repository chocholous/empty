"""Round 7: Czech apartment buildings from archiweb.cz with explicit Užitná plocha GT.

Targets:
- Akcíz (Praha 2022): UP=527 m², ZP=545 m², 3 NP, 14 apartments. PRIMARY.
- Block Karlín (Praha 2023): no GT, 7 NP, 98 apartments. Qualitative.
- Na Neklance (Praha 2024): no GT, 4 NP + basement, 31 apartments. Qualitative.
- Panorama Jih (Brno control): UP=5758 m², ZP=1314 m², 6 NP. Cross-check.

Resolution caveat: archiweb thumbnails are 389x275 (~13 px/m on a 30 m
building). Round 4-5 had 2000x1414. Expect degraded fixture-based
scale anchoring.
"""
from __future__ import annotations
import os, sys, json, time
sys.path.insert(0, os.path.dirname(__file__))
from round5_pipeline import measure_floor_v2, get_mitunet


def main():
    os.makedirs("out/round7", exist_ok=True)
    with open("samples/cz_apartments/manifest.json") as f:
        manifest = json.load(f)
    print("Loading MitUNet...")
    _ = get_mitunet()

    rows_per_building = {}
    for b in manifest["buildings"]:
        bid = b["id"]
        UP = (b.get("listed_areas_m2") or {}).get("uzitna_plocha")
        ZP = (b.get("listed_areas_m2") or {}).get("zastavena_plocha")
        per_plan = []
        # Sum the 3 detector flavors over all floor instances
        sums = {"v1": 0.0, "v2": 0.0, "vlm_rect": 0.0}
        for plan in b["plans"]:
            img = f"samples/cz_apartments/{plan['file']}"
            r = measure_floor_v2(img)
            r["level"] = plan["level"]
            r["instances"] = plan["instances"]
            per_plan.append(r)
            v1 = r.get("v1_cv_adaptive", {}).get("floor_area_m2")
            v2 = r.get("v2_mitunet_hull", {}).get("floor_area_m2")
            vw, vd = r.get("vlm_width_m"), r.get("vlm_depth_m")
            vrect = vw * vd if vw and vd else None
            n = plan["instances"]
            if v1: sums["v1"] += v1 * n
            if v2: sums["v2"] += v2 * n
            if vrect: sums["vlm_rect"] += vrect * n
            print(f"{bid:10s} | {plan['file']:30s} | inst={n} | v1={v1} v2={v2} W×D={vw}×{vd}")

        # Listed-total invariant (only if GT available)
        deviations = {}
        if UP:
            deviations = {tag: round((s - UP) / UP * 100, 1) for tag, s in sums.items()}

        # Footprint cross-check: pipeline-typical-floor-area ≈ ZP?
        typical_v1 = None
        if ZP and per_plan:
            # Take the largest instance count plan as the typical floor
            typical_plan = max(per_plan, key=lambda p: p.get("instances", 1))
            typical_v1 = typical_plan.get("v1_cv_adaptive", {}).get("floor_area_m2")

        rows_per_building[bid] = {
            "title": b["title"],
            "year": b["year"],
            "city": b["city_country"],
            "listed_UP_m2": UP,
            "listed_ZP_m2": ZP,
            "floors_above": b["floors_above_ground"],
            "v1_total_m2": round(sums["v1"], 1),
            "v2_total_m2": round(sums["v2"], 1),
            "vlm_rect_total_m2": round(sums["vlm_rect"], 1),
            "deviation_vs_UP_pct": deviations,
            "typical_floor_v1_m2": typical_v1,
            "typical_floor_v1_vs_ZP_pct": round((typical_v1 - ZP) / ZP * 100, 1) if (ZP and typical_v1) else None,
            "per_plan": per_plan,
        }

    out = "out/round7/results.json"
    with open(out, "w") as f:
        json.dump(rows_per_building, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {out}\n")

    # Summary table
    print(f"{'building':30s} {'UP':>6s} {'ZP':>6s} {'v1':>8s}  {'v2':>8s}  {'vlm_rect':>9s}  Δ_UP_v1")
    for bid, d in rows_per_building.items():
        UP = d["listed_UP_m2"] or 0
        ZP = d["listed_ZP_m2"] or 0
        dev = d["deviation_vs_UP_pct"].get("v1", "-") if d["deviation_vs_UP_pct"] else "-"
        print(f"{d['title'][:30]:30s} {UP:>6} {ZP:>6} {d['v1_total_m2']:>8}  {d['v2_total_m2']:>8}  {d['vlm_rect_total_m2']:>9}  {dev}%")


if __name__ == "__main__":
    main()
