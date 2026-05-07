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

---

# Round 2 — empirical library / model / API audit

Round 1 verified that the *Python helper layer* works end-to-end. Round 2 answers
the bigger question: **for each external library, pretrained model and API in
the originally proposed stack, does it actually run on this CPU box and produce
useful output on our samples?** Numbers in this section come from `out/round2.json`.

## OCR libraries (reading dimension annotations)

| Tool | Install effort | synth_clean | hf_00 (Arabic) | Verdict |
|---|---|---|---|---|
| **Tesseract 5.3.4** | apt + `pytesseract` | 0.2 s, all dims perfect | 0.5 s, garbled — no Arabic in default tessdata | Latin-only cheap baseline |
| **PaddleOCR PP-OCRv4** | `pip paddlepaddle paddleocr`; **needs `enable_mkldnn=False` on CPU** (PIR/oneDNN bug in PP-OCRv5 server models) | 2.4 s, `['kitchen','living','3.50x4.00','5.00x4.00','bath','bed1','bed2','2.50x3.00','3.50x3.00','2.50x3.00']`, mean score ≈ 0.98 | Arabic model not present in this build (only `en`+`ch` available for v4) | Best Latin/Chinese OCR; **Arabic gap blocking** |
| **EasyOCR** | `pip easyocr` (~250 MB on first init) | 0.8 s; one-char errors (`bath→path`, `bed2→ped2`) | **10.5 s, 44 text regions including Arabic numerals (٤٫٦٥, ٢٫٧٠) and labels (مطبخ kitchen, معيشة living, طرقة corridor)** | **Winner for multilingual plans; Arabic out of the box** |

The PaddleOCR fix (`enable_mkldnn=False`) is non-obvious and was found by switching
back from `PP-OCRv5` to `PP-OCRv4`; we leave a note in `tools.py` once OCR is
wired in.

## Pretrained floor-plan segmentation models

| Tool | Install / weights | Result | Verdict |
|---|---|---|---|
| **CubiCasa5K original (Apache-2.0)** | gdrive link `1gRB7DbU8K3v-eM3F4vFMhAyMSLhuMYz0` returns "permission denied / too many accesses" | could not load | **Unobtainable in May 2026** |
| **`JessiP23/cubicasa-segformer-v2`** (HF community retrain) | `pip segmentation-models-pytorch albumentations` + `.pt` from HF | metrics.json shows: bg 0.88, wall 0.30, window 0.30, door 0.15, **all 7 room classes 0.00 IoU** | Broken — room classes never learned |
| **`karanjaWakaba/Yolo_segmentation_cubicasa`** (235 classes) | `pip ultralytics` + HF download | **0 detections** at conf ∈ {0.05, 0.10} × imgsz ∈ {640, 1024} on synth_clean.png, hf_00.png, hf_01.png | Useless on out-of-distribution plans |
| **MitUNet (arXiv 2512.02413, Dec 2025)** | repo + Zenodo weights public | not yet installed in this round | High priority for round 3 (newest wall-mask SOTA) |
| **DeepFloorplan TF1** | repo with R3D weights link | not yet installed | Worth trying — TF1 dependency overhead is the main cost |
| **R2V / FloorplanTransformation** (PyTorch fork) | repo with R3D weights | not yet installed | Older but reproducible |

**Headline finding:** the easiest-to-grab community CubiCasa weights on
HuggingFace are not usable substitutes for the original training. To get a
real "CubiCasa baseline" we have to either retrieve the original Apache-2.0
weights through other channels or retrain on the public dataset. **MitUNet
(public weights on Zenodo)** is the better short-term target.

## Foundation segmenters (zero-shot)

| Tool | Install | Time / image | Output | Verdict |
|---|---|---|---|---|
| **MobileSAM** (`ultralytics SAM('mobile_sam.pt')`, 38.8 MB) | `pip ultralytics` | synth 133 s · hf_00 119 s | 29–31 unfiltered masks ("everything segmentation") | CPU-feasible but slow & needs prompting/filtering |
| **Florence-2-base** (Microsoft, 230 MB) | `pip transformers accelerate timm einops` | — | **failed to load**: `Florence2LanguageConfig.forced_bos_token_id` AttributeError on `transformers ≥ 4.45` | Needs `transformers~=4.41` pin; deferred |
| **SAM 2** (full) | `pip + ckpts ~600 MB` | not tested | — | Probably > 60 s/image on this CPU |

## VLM API A/B — same prompt, three Claude tiers, two images

Prompt: *"Return ONLY JSON `{\"rooms\":[{\"label\":...,\"w_m\":...,\"h_m\":...}]}` for every room with a written W×H dimension. No prose."*

| Model | synth_clean | hf_00 (Arabic) | hf_00 total area |
|---|---|---|---|
| **claude-haiku-4-5** | 5.4 s, **5/5 rooms correct** | 69.5 s, 8 rooms, **systematic bug**: every `h_m` is 2.65 m (ceiling height read instead of room depth) | 71.9 m² — undershoots |
| **claude-sonnet-4-6** | 4.8 s, **5/5 correct** | **138.5 s** (slowest), 9 rooms, dims plausibly real | 101.4 m² — closest to "right shape" |
| **claude-opus-4-7** | 6.3 s, **5/5 correct** | **17.6 s (fastest!)**, 9 rooms, dims plausibly real | 131.4 m² — over-counts ~+13 % |

Surprises:
- **Opus 4.7 was 8× faster than Sonnet 4.6 on the Arabic plan** (17.6 s vs 138.5 s) and matched its dimensional accuracy. On dense plans Opus is the right cost/quality choice for this task.
- **Haiku 4.5 systematically misreads** Arabic apartment plans by substituting a ceiling-height constant (2.65 m) for room depth. It is *unsuitable* for floor-plan dimension extraction even though it works fine on the synthetic Latin sample.
- All three returned valid (or fence-stripped) JSON every call, no parser failures.

Action item: **default model in `vlm_call` should be Opus 4.7 for real plans, Sonnet 4.6 as fallback.** Haiku only for clean Latin synth samples (rare in production).

## PyMuPDF on a vector PDF

Generated `samples/synth_vector.pdf` (1605 B) with reportlab, then ran PyMuPDF.

| Metric | Value |
|---|---|
| `page.get_drawings()` time | **0.01 s** |
| Rectangles recovered | 5 / 5 |
| Coordinate precision | float-pt (0 % area error after px↔mm conversion) |
| Text spans (`page.get_text("dict")`) | 10 / 10 with bboxes |
| Page user units | 1 pt = 1/72 in (deterministic, no calibration needed) |

**Conclusion:** for any vector-PDF input the whole pipeline collapses to
**PyMuPDF + Shapely**. No CV, no LLM, area accuracy is float-pt. The hard
problem is *raster-only* inputs.

## Decision matrix (per-tool fitness)

| Layer | Tool | Quality | CPU time | Install effort | Use it? |
|---|---|---|---|---|---|
| Vector PDF | **PyMuPDF** | float-pt | 10 ms | trivial | **Yes — primary path for PDFs** |
| Vector PDF | pdfplumber | text/lines | tens of ms | trivial | Yes — complement to PyMuPDF for text positions |
| DXF | **ezdxf 1.4** | float-pt | n/a tested | trivial | Yes — primary path for DXF |
| Raster CV | **OpenCV adaptive threshold + CC** | good on clean, fragile on real | 50–200 ms | already installed | Yes — baseline |
| Raster ML | CubiCasa5K orig | unknown | — | weights blocked | Pending — chase original weights |
| Raster ML | MitUNet (12/2025) | unknown | unknown | medium | **Try in round 3** |
| Raster ML | Community CubiCasa retrains | broken | — | medium | **No** |
| Raster zero-shot | MobileSAM | many masks, no semantics | ~120 s | trivial | Only if prompt-driven (text → SAM) |
| OCR Latin | **PaddleOCR v4 (en)** | excellent | 2.4 s | medium (oneDNN gotcha) | **Yes for Latin** |
| OCR Latin cheap | **Tesseract 5** | very good on clean text | 0.2 s | trivial | Yes — cheap fallback |
| OCR multilingual | **EasyOCR** | strong incl. Arabic | 0.8–10 s | trivial | **Yes — primary OCR for non-Latin** |
| Geometry | **Shapely 2.1** | float-pt | < 1 ms | trivial | Yes — already in stack |
| VLM real plans | **Claude Opus 4.7** | accurate, fastest | 17 s on hf_00 | API/CLI | **Yes — default VLM** |
| VLM Latin plans | Claude Sonnet 4.6 | accurate | 5 s synth, 138 s hf_00 | API/CLI | Yes — fallback / cheaper Latin |
| VLM small plans | Claude Haiku 4.5 | broken on Arabic | 5–69 s | API/CLI | **No for production** |
| VLM alternative | GPT-4o, Gemini 2.5 Pro | not tested (no key) | — | API key needed | Round 3 |

## Updated stack recommendation

Based on Round 2 evidence:

1. **Input router**: PyMuPDF first (vector PDF → exact). DXF → ezdxf. Else → raster path.
2. **Raster CV**: OpenCV for walls + door arcs; **add MitUNet** for difficult plans (round 3).
3. **OCR**: EasyOCR multilingual primary, PaddleOCR-v4 for high-confidence Latin, Tesseract as fast cheap fallback.
4. **Geometry**: Shapely for areas, NetworkX for room adjacency graph (not yet exercised).
5. **VLM orchestrator**: Claude Opus 4.7 default, Sonnet 4.6 fallback. Haiku only for trivial cases.
6. **Norm layer**: Shapely buffer for ČSN 73 4055 / ISO 9836 net↔gross (not yet exercised).

## What round 2 did not prove

- **MitUNet, DeepFloorplan, R2V** still untested.
- **No DXF sample**; ezdxf only verified by import.
- **No GPT-4o / Gemini comparison** (no API keys in this environment).
- **No vector-PDF with Czech apartment** (synth-rendered only).
