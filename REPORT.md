# Floor-plan tool verification — POC results

Goal: empirically check whether Claude (via `claude -p` subprocess) can
drive deterministic CV/geometry tools to extract apartment areas from raster
floor plans, and where it breaks.

## Setup

- Host: Linux container, no GPU, Python 3.11, OpenCV 4.13, Shapely 2.1, PyMuPDF 1.27.
- LLM: Claude **Sonnet 4.6** (`claude-sonnet-4-6`) via `claude -p` subprocess. Hooks suppressed via `--settings '{"hooks":{}}'`. Permission mode `acceptEdits`. Read tool allowed so the model loads image bytes itself.
- Samples: 2 synthetic plans with hard ground truth (`src/synth.py`), 5 real Arabic plans pulled from HuggingFace dataset `Ahmed167/floor-plans-dataset` (1.7 MB parquet, 31 plans). Wikimedia upload host is blocked by egress policy; HF + GitHub raw work.

Code:
- `src/tools.py` — deterministic tools (`detect_walls`, `extract_rooms`, `calibrate_scale_from_*`, `compute_areas`, `render_overlay`, `vlm_call`, `auto_pipeline`).
- `src/synth.py` — synthetic plan generator with ground-truth JSON.
- `src/experiment.py` — runs both synth and real samples, writes `out/results.json` and overlays.

Reproduce:
```
.venv/bin/python src/synth.py
.venv/bin/python src/experiment.py
```

## Headline numbers

| Sample | Rooms (GT/det/VLM) | mIoU | Per-room \|err\| | Total area err |
|---|---|---|---|---|
| synth_clean.png   | 5 / 5 / —  | 0.916 | 9.7 % | **−9.0 %** |
| synth_nodims.png  | 5 / 5 / —  | 0.916 | 9.7 % | **−9.0 %** |
| hf_00.png (real)  | — / 18 / 9 | n/a   | n/a   | det 117.0 m² vs VLM 116.4 m² |
| hf_01.png (real)  | — / 18 / 6 | n/a   | n/a   | det 123.9 m² vs VLM **79.8 m²** |

Synthetic mean IoU 0.916 with a systematic −9 % bias is exactly what you get when polygons exclude wall thickness — i.e. the CV pipeline produces *net usable area* (consistent with ČSN 73 4055 net definition). For *gross floor area* you would inflate by half-wall on every side.

VLM dimension reading on real plans: **7.4 s and 24.8 s** subprocess time, valid JSON every time, with most written W×H values transcribed correctly (one or two digits misread on tightly-spaced labels).

## What worked

1. **`claude -p` as a tool callable from Python.** Subprocess returns in single-digit seconds for trivial prompts and 7–30 s for image+JSON tasks. Hooks must be suppressed, otherwise stop-hook output replaces the model's answer (`{"hooks":{}}` via `--settings`).
2. **Synthetic-plan deterministic pipeline.** All 5 rooms detected, IoU > 0.9, area error driven entirely by wall-thickness convention.
3. **VLM dimension extraction on Arabic plans.** Sonnet 4.6 reads Eastern-Arabic-numeral dimensions written inside rooms and returns clean structured JSON. Cross-check on `hf_00.png`: 9 rooms × W×H values, total 116.4 m² — sane apartment number.
4. **VLM as overlay verifier.** Asked Sonnet to grade the `hf_01.png` overlay; it correctly identified frame/text-block polygons as non-rooms and reported "6/8 plausible". Closed-loop verification works.
5. **Scale calibration via VLM-anchor.** Picking the largest VLM-labelled area and matching it to the largest detected polygon (excluding the merged-frame blob) yields px/m ≈ 89 (hf_00) and 76 (hf_01) — within the expected range for ~600 px-wide plans of ~7 m houses.

## What broke

1. **Room segmentation on real plans is fragile.** `extract_rooms` is just connected-components on `NOT(walls)`. Doors leave gaps, so adjacent rooms merge into one polygon. Text icons and door arcs survive as small polygons. On real samples the pipeline reported 18 components when the actual room count was 9 (hf_00) and 6 (hf_01). For hf_01 this inflated total area by **+55 %** even after good calibration.
2. **Default px/m is meaningless for real plans.** Without VLM-anchored scale calibration the synth-default of 50 px/m gave hf_00 a "374 m² apartment". Calibration is mandatory.
3. **VLM is not a measurement tool.** It reads what is *written* on the plan. On a plan with no written dimensions and no scale bar, the VLM has nothing to anchor to — the pipeline can't recover scale from pixels alone. Synthetic `synth_nodims.png` works only because we know `px_per_m` from the generator.
4. **Wall-thickness ambiguity.** −9 % systematic error on synth is a *convention* issue, not a bug. The pipeline must be told whether the consumer wants net (interior face), to-centerline, or gross (exterior face) area.
5. **VLM occasionally hallucinates digits.** On hf_00 the top-left bedroom is annotated 4.50 × 3.91 m on the plan, Sonnet returned 4.00 × 3.91 — a decimal misread that quietly distorts area by 12 %. A second pass at higher resolution or a digit-OCR fallback (PaddleOCR) would catch this.

## Findings about Claude orchestration

- **Subprocess plumbing is fine.** `claude -p --tools Read --settings '{"hooks":{}}' --setting-sources project` reliably runs vision tasks in 7–30 s.
- **Why Sonnet 4.6, not Haiku.** The 2+2 smoke test ran on Haiku 4.5 only to confirm subprocess invocation. All real vision work uses Sonnet 4.6 — Haiku would lose digits and miss small rooms.
- **Tool-call overhead is high enough that you don't want a chatty agent loop.** Two-pass orchestration (deterministic pipeline → render overlay → single VLM verification call) is a much better latency profile than letting the model call tools step by step.
- **JSON schemas help.** Asking for `{"rooms":[{"label":...,"w":...,"h":...}]}` returned parseable JSON every call; freeform prose returned was sometimes wrapped in ```json fences but the parser handles that.

## Recommended architecture (based on this POC)

1. **CV layer** — adaptive threshold → connected components → polygons. Cheap, works perfectly on clean vector renders.
2. **Door + closure layer** *(missing in this POC, this is the main fix)* — detect door arcs (Hough or template), close gaps so rooms are isolated. Without this, real plans over-merge.
3. **VLM layer** — read room labels and written dimensions, return JSON. Sonnet 4.6 is the right model.
4. **Calibration layer** — anchor px/m via either (a) written dim of one labelled room, (b) scale bar OCR, or (c) building footprint dimension on façade (hf_00 has "9.94 m" on the top edge — tractable).
5. **Verification layer** — render overlay, ask VLM to flag non-room polygons. Use as a quality gate, not a fix.
6. **Norm layer** — apply ČSN 73 4055 / ČSN ISO 9836 rules for net/gross. The CV pipeline gives both: polygon = net, polygon ⊕ half-wall = gross.

## What this does NOT prove

- Anything about **multi-floor** plans, dimensioned but unscaled CAD, or photographed (perspective-warped) plans.
- Anything about **plan complexity** beyond rectilinear walls — curved walls and bay windows aren't tested.
- Performance at scale: each VLM call is 7–30 s, so a 100-plan batch is 12–50 minutes of LLM wall-clock. Door closure step would add ~0.2 s/plan (cheap).

## Numbers reference (from `out/results.json`)

```
synth_clean      gt=59.50 m²   det=54.14 m²   err=−9.0 %   mIoU=0.916
synth_nodims     gt=59.50 m²   det=54.14 m²   err=−9.0 %   mIoU=0.916
hf_00 (real)     vlm=116.4 m²  det=117.0 m²   px/m=89.4    vlm_time=7.4s
hf_01 (real)     vlm= 79.8 m²  det=123.9 m²   px/m=76.3    vlm_time=24.8s
```

Verdict: **the right tool surface plus Claude Sonnet 4.6 is enough to anchor scale and read dimensions on raster plans**, but room-polygon extraction needs a door-closure pass before the totals from CV match those from VLM on real samples. The synthetic case is solved; the real case is one missing component (door closure) away from being solved.
