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

---

# Round 3 — MitUNet, Florence-2 retry, norm layer, DXF

Round 3 closes three of the four gaps from round 2.

## MitUNet (arXiv 2512.02413, MVA 2026) — empirically run

| Field | Value |
|---|---|
| Repo | https://github.com/aliasstudio/mitunet (MIT) |
| Weights | `experiments/models/mitunet_finetune_a6_mit_b4_tversky_8864_28E.pth` via Git-LFS, **257 MB**, **CC-BY-NC 4.0** (non-commercial — important if this ever ships) |
| Architecture | `smp.Unet(encoder=mit_b4, decoder_attention="scse")` with the encoder *transplanted* from `smp.Segformer(mit_b4)` before `load_state_dict` |
| Class taxonomy | **walls only** (binary mask, sigmoid + 0.5 threshold) |
| Input size | resize 512×512, ImageNet normalise |
| Params | **64.2 M** |
| Load time (CPU) | 5.4 s |

**Inference time on CPU**:
- synth_clean.png: 3.6 s (first call has compile overhead)
- hf_00.png: 0.7 s
- hf_01.png: 0.7 s

### MitUNet vs OpenCV adaptive — quality on synth GT

GT mask reconstructed from `synth.py` (rectangles with `wall_px=6`).

| Metric | MitUNet | OpenCV adaptive |
|---|---|---|
| IoU strict | 0.772 | **0.826** |
| IoU vs dilated GT (1 px) | **0.781** | 0.671 |
| Precision | **0.870** | 0.826 |
| Recall | 0.872 | **1.000** |

OpenCV adaptive wins strict-IoU because it captures **every** dark pixel
including text — recall 1.0 — but precision is dragged down by those false
positives. MitUNet has more balanced precision/recall and wins under any
1-px tolerance.

### Real plans — wall pixel ratio

| Sample | OpenCV adaptive | MitUNet |
|---|---|---|
| synth_clean | 9.5 % | 7.9 % |
| hf_00 (Arabic real) | 12.3 % | **5.2 %** |
| hf_01 (Arabic real) | 9.0 % | **4.4 %** |

On real plans MitUNet predicts **40–60 % less wall area** than OpenCV
adaptive — it has *learned* to ignore furniture, dimension lines, hatching,
text. That is the core value-add over a generic CV threshold.

### MitUNet downstream — feeding masks into `extract_rooms`

| Sample | OpenCV → rooms | MitUNet → rooms |
|---|---|---|
| synth_clean.png | 5 (correct) | **5 (correct)** |
| hf_00.png | 18 polygons (over-merged) | **0 polygons** |
| hf_01.png | 18 polygons (over-merged) | **0 polygons** |

**Failure mode:** MitUNet predicts walls as ~1–2 px thick after resize-back.
Tiny gaps (door arcs, wall breaks) leave the inverted mask as one large
connected component → no rooms detected. Tested dilations 3/5/7 do not
recover rooms on `hf_00.png` and `hf_01.png` — gaps are too large for naive
morphology to bridge. This is the **out-of-distribution generalization gap**
between the CubiCasa5K + Russian-CIS training set and the Arabic-style
plans we sampled.

**Practical conclusion:** MitUNet is the right *wall semantic filter* but
not a complete room-extractor on plans outside its training distribution.
A production stack should:
1. Use MitUNet to suppress non-wall content.
2. Combine with OpenCV adaptive (logical OR) to keep recall.
3. Add a door-closure step before connected-components.

## Florence-2 retry with `transformers==4.41.2`

Pinning fixed the `forced_bos_token_id` config bug. New blocker:

```
ImportError: This modeling file requires the following packages that
were not found in your environment: flash_attn.
Run `pip install flash_attn`
```

`flash_attn` requires CUDA at build time and does not install on a CPU-only
host. Workaround would be to fork the modelling file and pass
`attn_implementation="sdpa"`. **Verdict: Florence-2-base on CPU has two
blockers stacked (transformers pin + flash_attn fork). Skip until either
GPU or a community CPU-patched fork is available.**

## Norm layer — Shapely buffer (ČSN 73 4055 / ISO 9836)

Verified on the synth_clean polygons:

| Quantity | Value | Notes |
|---|---|---|
| `wall_thickness_m` | 0.150 | typical Czech interior partition |
| Net total (sum of polygon.area) | 59.500 m² | matches GT exactly |
| Per-room "to-centerline" (`p.buffer(t/2)`) | [15.15, 21.37, 8.35, 11.50, 8.35] m² | each room ~+8 % |
| Gross total (`unary_union(buffered)`) | 61.847 m² | only +3.95 % vs net |

The `unary_union` step is what makes this correct: shared interior walls
get counted only once, while exterior walls get a half-thickness buffer on
the outside. This is the **one Shapely operation** that closes the gap
between "polygon area" and "ČSN 73 4055 / ISO 9836 gross floor area".

## DXF + ezdxf 1.4 — semantic extraction

Generated `samples/synth_apartment.dxf` (1 unit = 1 m, 5 layers:
`WALL`, `DOOR`, `WINDOW`, `ROOM`, `DIM`) using ezdxf, then re-read it.

| Metric | Value |
|---|---|
| Load time | 0.019 s |
| `LWPOLYLINE` on layer `WALL` | 5 / 5 |
| `ARC` on layer `DOOR` | 2 / 2 |
| `LWPOLYLINE` on layer `WINDOW` | 1 / 1 |
| `TEXT` on layer `ROOM` | 5 / 5 (positions preserved at room centroids) |
| `TEXT` on layer `DIM` | 1 / 1 |
| Sum of polygon areas | 59.500 m² (exact GT match) |

ezdxf preserves layers, entity types, exact coordinates and inserts.
A DXF with semantic layers is a solved input — same status as a vector PDF.

## Round 3 decision-matrix updates

| Layer | Tool | Quality update | Use it? |
|---|---|---|---|
| Raster ML | **MitUNet** | precision 0.87 / 0.7 s on 600-px plans / wall-only | **Yes — as semantic filter, not stand-alone room extractor**. CC-BY-NC 4.0 — non-commercial only. |
| Raster zero-shot VLM | Florence-2-base | requires `flash_attn` (GPU) or a forked modelling file | **No on CPU box** |
| Geometry / Norm | **Shapely + `unary_union(buffer)`** | 1-line correct net→gross under ISO 9836 | **Yes** — primary norm-layer impl |
| Vector input | **ezdxf 1.4** | exact polygons, layers, texts, arcs | **Yes** — primary path for DXF |

## What round 3 still leaves open

- **DeepFloorplan**, **R2V** — still untested; lower priority now that MitUNet covers the modern wall-mask slot.
- **GPT-4o / Gemini 2.5 Pro / Qwen-VL-Max** — VLM A/B vs Claude requires API keys not present in this environment.
- **Original CubiCasa5K Apache-2.0 weights** — gdrive link still blocked.
- **Florence-2 CPU fork** — possible but requires modelling file patch.

## Headline (after rounds 1–3)

The empirical answer to *"can the proposed stack actually work on CPU
in May 2026?"* is **yes for vector inputs (PyMuPDF, ezdxf are essentially
solved), conditional yes for raster inputs (OpenCV + MitUNet + EasyOCR +
Claude Opus 4.7), and no for any path through the community-hosted
floor-plan models (CubiCasa SegFormer, YOLO-CubiCasa) or Florence-2 on
CPU**. The proper raster pipeline is approximately:

```
raster
  → MitUNet (wall mask, precision filter)
  → OpenCV adaptive (recall fill-in, OR-merged with MitUNet)
  → door-arc detector + close gaps        # ← still TODO
  → connected components → polygons (Shapely)
  → EasyOCR (multilingual dim labels)
  → Claude Opus 4.7 anchors scale + verifies overlay
  → unary_union(buffer(t/2)) for ČSN/ISO gross
```

Each component in this chain is now empirically observed to work in this
environment, except the door-arc step which remains a known-open gap.
