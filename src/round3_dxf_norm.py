"""Round 3 deterministic checks: ezdxf semantic extraction + Shapely net/gross norm layer."""
import json, math, time
import ezdxf
from ezdxf import bbox
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union

# ---- 1) Generate a minimal-but-realistic DXF apartment with semantic layers ----
out_dxf = "samples/synth_apartment.dxf"
doc = ezdxf.new(setup=True)
doc.layers.add("WALL", color=7)
doc.layers.add("DOOR", color=1)
doc.layers.add("WINDOW", color=4)
doc.layers.add("ROOM", color=3)
doc.layers.add("DIM", color=5)
msp = doc.modelspace()

# Apartment footprint in metres (1 unit = 1 m). Five rooms, same layout as synth_clean.
rooms = [
    ("kitchen", 0.0, 0.0, 3.5, 4.0),
    ("living",  3.5, 0.0, 5.0, 4.0),
    ("bath",    0.0, 4.0, 2.5, 3.0),
    ("bed1",    2.5, 4.0, 3.5, 3.0),
    ("bed2",    6.0, 4.0, 2.5, 3.0),
]
WALL_THICKNESS_M = 0.15

# WALL layer: outer rectangle of each room as a closed polyline
for name, x, y, w, h in rooms:
    pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)]
    msp.add_lwpolyline(pts, dxfattribs={"layer": "WALL"})
# DOOR layer: an arc per room (centered on a wall midpoint)
msp.add_arc((1.75, 4.0), 0.9, 0, 90, dxfattribs={"layer": "DOOR"})
msp.add_arc((4.5, 4.0), 0.9, 0, 90, dxfattribs={"layer": "DOOR"})
# WINDOW layer: a rectangle on an external wall
msp.add_lwpolyline([(0.5, -0.1), (1.7, -0.1), (1.7, 0.1), (0.5, 0.1), (0.5, -0.1)],
                   dxfattribs={"layer": "WINDOW"})
# ROOM layer: text labels at centroids
for name, x, y, w, h in rooms:
    msp.add_text(name, dxfattribs={"layer": "ROOM", "height": 0.25}).set_placement(
        (x + w / 2, y + h / 2)
    )
# DIM layer: a couple of dimension annotations as plain text (most CAD apps export this way)
msp.add_text("3.50 m", dxfattribs={"layer": "DIM", "height": 0.18}).set_placement((1.5, -0.5))
doc.saveas(out_dxf)

t0 = time.time()
doc2 = ezdxf.readfile(out_dxf)
load_s = time.time() - t0
msp2 = doc2.modelspace()

# Extract by layer
by_layer = {}
for e in msp2:
    by_layer.setdefault(e.dxf.layer, []).append(e.dxftype())
# Build shapely polygons for each LWPOLYLINE on WALL layer; that gives us
# room footprints directly.
room_polys = []
for e in msp2.query('LWPOLYLINE[layer=="WALL"]'):
    pts = [(p[0], p[1]) for p in e.get_points()]
    if pts and pts[0] != pts[-1]:
        pts.append(pts[0])
    poly = Polygon(pts)
    if poly.is_valid and poly.area > 0:
        room_polys.append(poly)

# Read text labels
texts = []
for e in list(msp2.query('TEXT[layer=="ROOM"]')) + list(msp2.query('TEXT[layer=="DIM"]')):
    texts.append({"text": e.dxf.text, "layer": e.dxf.layer,
                  "pos": [round(e.dxf.insert.x, 2), round(e.dxf.insert.y, 2)]})

# ---- 2) Norm layer: ČSN 73 4055 / ISO 9836 net <-> gross via Shapely buffer ----
# Net = sum of room polygons (interior). Gross = polygons buffered by half-wall.
net_areas = [round(p.area, 3) for p in room_polys]
net_total = round(sum(net_areas), 3)

# Gross: buffer each polygon by +half wall, then union to avoid double-counting
buffered = unary_union([p.buffer(WALL_THICKNESS_M / 2, join_style=2) for p in room_polys])
gross_total = round(buffered.area, 3)
# Convention check: gross should be ~5–10 % larger than net for typical apartments.
# We also produce per-room "to-centerline" by buffering by full half-wall.
to_centerline = [round(p.buffer(WALL_THICKNESS_M / 2, join_style=2).area, 3) for p in room_polys]

result = {
    "ezdxf_load_seconds": round(load_s, 4),
    "entities_by_layer": {k: dict.fromkeys(set(v), 0) for k, v in by_layer.items()},
    "rooms_recovered": len(room_polys),
    "rooms_expected": len(rooms),
    "net_areas_m2": net_areas,
    "net_total_m2": net_total,
    "gross_total_m2": gross_total,
    "to_centerline_m2": to_centerline,
    "wall_thickness_m": WALL_THICKNESS_M,
    "gt_net_total_m2": sum(w * h for _, _, _, w, h in rooms),
    "gt_total_match": math.isclose(net_total, sum(w * h for _, _, _, w, h in rooms), rel_tol=1e-6),
    "texts_found": texts,
}
# Count entity types per layer
for k, v in by_layer.items():
    result["entities_by_layer"][k] = {t: v.count(t) for t in set(v)}

print(json.dumps(result, indent=2, ensure_ascii=False))
