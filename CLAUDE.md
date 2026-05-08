# Floor-plan POC — orientation for any agent picking this up

This file gives a working agent enough background to compose its own
approach to a floor-plan task without falling into the traps that
rounds 1–5 already mapped. It is a cheat-sheet, not a tutorial.

## What this repo is

POC for measuring floor plans (walls, rooms, useable area) using a
vision-language model orchestrating deterministic geometry / OCR /
segmentation tools. Five rounds of work documented in `REPORT.md` cover:
synthetic IoU-0.92 baseline, real Arabic plans, MitUNet wall mask, real
multi-floor Czech / Slovak apartment buildings, and a four-way detector
comparison. Read `REPORT.md` first if you have ten minutes — every
finding below cross-references a section there.

The big open architectural gap: **rounds 1–5 hard-coded the orchestration
in Python**. The agent never picked which tool to call. Round 6 onwards
should treat that loop as the deliverable, not the wrapper functions.

---

## 1. How to actually use the libraries (CLI / API, not via wrappers)

Treat `src/tools.py` as a library of pre-tested snippets, not a contract.
You can ignore it and call the underlying libraries directly any time
that fits the problem better.

### OpenCV (cv2 4.10) — wall mask, contours, morphology
```python
import cv2
img  = cv2.imread(path)                                        # BGR uint8
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# Adaptive threshold = recall-rich wall mask. Captures dark strokes
# (walls AND text AND dim lines AND hatching). 9-12% dark ratio is
# normal for our plans.
mask = cv2.adaptiveThreshold(gray, 255,
                             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                             cv2.THRESH_BINARY_INV,
                             blockSize=31, C=15)
# Close gaps (door openings, dim-line breaks). Kernel size dictates
# what "gap" means; 5 px is reasonable, 9 px aggressive, 15 px floods.
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
# External contour of largest non-bg component = "the building" — but
# fragile when the page contains property lines, terraces, neighbours
# (see Round 4/5 fail-modes in REPORT.md).
cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
```
Failure-mode reminders:
- text and dim lines are dark and survive adaptive threshold; mask out
  text bboxes from the EasyOCR pass before contour-extraction
- on architectural plans the building is often a *sub-component*, not
  the largest one; consider VLM-guided crop before contour

### MitUNet (CC-BY-NC) — precision-tuned wall segmentation
Weights pre-downloaded at
`models/mitunet/experiments/models/mitunet_finetune_a6_mit_b4_tversky_8864_28E.pth`
(257 MB, 64.2 M params).

```python
import torch, segmentation_models_pytorch as smp, albumentations as A
from albumentations.pytorch import ToTensorV2
WEIGHTS = "models/mitunet/experiments/models/mitunet_finetune_a6_mit_b4_tversky_8864_28E.pth"
aux   = smp.Segformer(encoder_name="mit_b4", encoder_weights=None)
model = smp.Unet(encoder_name="mit_b4", encoder_weights=None,
                 in_channels=3, classes=1, decoder_attention_type="scse")
model.encoder = aux.encoder
model.load_state_dict(torch.load(WEIGHTS, map_location="cpu", weights_only=False))
model.eval()
tfm = A.Compose([A.Resize(512,512),
                 A.Normalize(mean=(0.485,0.456,0.406), std=(0.229,0.224,0.225)),
                 ToTensorV2()])
x = tfm(image=cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB))["image"].unsqueeze(0)
with torch.no_grad():
    prob = torch.sigmoid(model(x)).squeeze().numpy()      # 512x512
mask = cv2.resize((prob > 0.5).astype("uint8")*255, (W,H), cv2.INTER_NEAREST)
```
- Latency: 0.7–3.6 s/plan on CPU.
- Output: thin (1–2 px after resize-back) wall mask, 4–5 % dark ratio.
- License is **CC-BY-NC 4.0**. Non-commercial only.
- Distribution gap: trained on CubiCasa5K + Russian regional plans.
  Czech / Slovak / Arabic plans get fragmented walls — Round 3 lost
  whole rooms because gaps weren't bridged even after 7-px dilation.
- Use it as a *precision filter on top of cv2.adaptiveThreshold*
  (logical AND with a tolerance buffer), never as the only wall source.

### EasyOCR — multi-language text on plans
```python
import easyocr
reader = easyocr.Reader(['en','cs'])     # add 'ar' for Arabic, 'ru' for Cyrillic
boxes = reader.readtext(np_image)        # list of (bbox, text, conf)
```
- ~0.8 s on Latin synth, ~10 s on Arabic real plan (round 2).
- Returns per-region bbox in image coords. Use those bboxes to mask
  text out of the wall mask before contour-extraction.

### PaddleOCR PP-OCRv4 — high-confidence Latin
```python
from paddleocr import PaddleOCR
ocr = PaddleOCR(lang='en', enable_mkldnn=False, ocr_version='PP-OCRv4')
result = ocr.ocr(np_image, cls=False)
```
**Mandatory**: `enable_mkldnn=False` and `ocr_version='PP-OCRv4'`. The v5
server models hit a CPU OneDNN bug
(`ConvertPirAttribute2RuntimeAttribute`).

### Tesseract — fallback
`tesseract IMAGE - --psm 11 -l eng` (psm 11 = sparse text). 0.2 s, garbage
on Arabic. Use only as a sanity check on Latin plans.

### Shapely 2.1 — geometry
```python
from shapely.geometry import Polygon
from shapely.ops import unary_union
gross = unary_union([Polygon(r).buffer(t/2) for r in rooms]).area
```
The `unary_union(buffer(t/2))` line is the only way to convert a list of
room polygons into ČSN 73 4055-style gross floor area without
double-counting shared walls.

### Claude vision via the CLI
```bash
claude -p --model claude-opus-4-7 \
       --tools Read \
       --permission-mode acceptEdits \
       --settings '{"hooks":{}}' \
       --setting-sources project \
       <<<"Use Read on '$ABS_IMG'. Then answer: …"
```
- `--tools Read` lets the sub-agent load the image; suppress hooks via
  `--settings '{"hooks":{}}'` so the parent stop hook doesn't hijack
  the response.
- Models tested:
  - **claude-opus-4-7 (default for vision):** 7–20 s/plan, robust JSON
    output, fixture-reference reasoning. Round 5 default.
  - **claude-sonnet-4-6:** 138 s on Arabic real plan (8× slower than
    Opus 4.7 on the same image). Use only for Latin synth where Opus
    feels overkill.
  - **claude-haiku-4-5:** systematically substitutes ceiling height for
    room depth on Arabic plans. Don't use for floor-plan vision.

### Anthropic Messages API with `tool_use` (the missing loop)
The proper round-6 path. Skeleton (not yet implemented in this repo):
```python
import anthropic
client = anthropic.Anthropic()
TOOLS = [
    {"name":"detect_walls","description":"…","input_schema":{…}},
    {"name":"crop_region","description":"VLM-decided crop","input_schema":{…}},
    {"name":"vlm_anchor_scale","description":"…","input_schema":{…}},
    {"name":"compute_area","description":"…","input_schema":{…}},
]
msgs = [{"role":"user","content":[
    {"type":"image","source":{"type":"base64","media_type":"image/jpeg",
                              "data":b64}},
    {"type":"text","text":"Measure the apartment area."}]}]
while True:
    r = client.messages.create(model="claude-opus-4-7",
                               max_tokens=4096, tools=TOOLS, messages=msgs)
    if r.stop_reason == "end_turn": break
    for block in r.content:
        if block.type == "tool_use":
            result = dispatch(block.name, block.input)
            msgs += [{"role":"assistant","content":r.content},
                     {"role":"user","content":[{"type":"tool_result",
                                                "tool_use_id":block.id,
                                                "content":json.dumps(result)}]}]
```
Use `prompt_caching` on the system prompt + this CLAUDE.md content;
typical loop is 3–6 round-trips per plan.

---

## 2. What "area" means in Czech, Slovak, and international practice

Most pipeline failures in this repo trace to comparing the wrong thing
to the wrong number. Before computing any deviation %, identify which
definition you're working with.

### Czech standards (also valid in Slovakia with STN equivalents)
| Term (CZ) | What it measures | Where it appears |
|---|---|---|
| **Užitná plocha** (UP) | Net useable floor area inside the unit, *excluding* walls, columns, shafts. Includes corridors and storage. Per **ČSN 73 4055** / ČSN ISO 9836. | sreality.cz "Užitná plocha", rental contracts, building permits |
| **Podlahová plocha bytu** (PP) | UP **+ half-area of balconies/loggias/terraces**. Per **Act 311/2013 Sb.** §3 | tax declarations, real-estate transfer |
| **Zastavěná plocha** (ZP) | Building footprint outline including exterior walls. | katastr nemovitostí "výměra zastavěné plochy", building permit |
| **Obytná plocha** | Subset of UP — only living rooms (bedrooms, living rooms). Excludes kitchen, bath, hallway. | older communist-era valuations, housing stats |
| **Hrubá podlažní plocha** (HPP / GFA) | Σ over floors of ZP (built area incl walls), excluding open balconies. | architectural project data, EIA |
| **Obestavěný prostor** (OP) | Enclosed volume m³. | construction-cost estimates |

### What different sources actually publish
| Source | Field name | What it actually contains | Reliability |
|---|---|---|---|
| **sreality.cz** | "Užitná plocha" | UP per ČSN 73 4055 | High (legally binding for sales) |
| **sreality.cz** | "Plocha bytu" | PP = UP + ½ balcony | Medium (rounded, sometimes confused with UP) |
| **bezrealitky.cz** | "Užitná plocha" | UP, but inconsistent (sometimes seller-reported gross) | Medium |
| **katastr nemovitostí** (cuzk.cz) | "Výměra" | ZP for buildings, "výměra parcely" for land | High but different from internal area |
| **archiweb.cz / archdaily.com** | "Plocha" / "Area" | **Inconsistent**: GFA, footprint, per-unit, per-floor | **Low** — read the project notes |
| **NOZ §1159** flat definition | n/a | Includes "příslušenství" (auxiliary spaces) | Legal fine print |

Round 4 cost a debugging round because ArchDaily's "Area: 283 m²"
turned out to be per-floor footprint for Podun but gross floor area for
Iconik. **Never trust an "Area" field without confirming its
definition** against a second source (cadastre, building permit, or the
floor-plan note "Užitná plocha celkem").

### Cross-check arithmetic
- For an apartment building: `HPP ≈ ZP × n_floors_above_ground − atrium_voids` (basement variable per local code)
- For one apartment: `UP × ~1.10–1.15 ≈ PP` (depending on balcony share)
- For a free-standing house: `ZP ≈ UP_ground_floor + wall_thickness ≈ UP_ground_floor × 1.07–1.10`

---

## 3. What's already been tried and where it broke

Read `REPORT.md` for full numbers. One-line summaries:

| Round | What | Verdict |
|---|---|---|
| 1 | Synth + DeepFloorplan + room polygons | IoU 0.92 strict on synthetic; door arc closure missing → real plans over-merge |
| 2 | Real Arabic plan, OCR, VLM dimensions | EasyOCR works on Arabic (10 s); Sonnet 4.6 138 s vs Opus 4.7 17.6 s; Haiku reads ceiling height as depth — disqualified |
| 3 | MitUNet wall mask (CC-BY-NC) | IoU 0.77 on synth; on real OOD plans returns 0 polygons after extract_rooms (gaps not bridged) |
| 4 | Real multi-floor: Iconik (Praha 2023, listed 5433 m²) + Podun (Bratislava 2024) | Iconik +4.9 % vs listed (PASS); Podun "+549 %" was metadata-misinterpretation, per-floor pipeline within ±16 % |
| 5 | Outline detector v2 (MitUNet hull) + 4-way comparison | v2 worse than v1 on Iconik (+223 %); vlm_rect (Opus W×D, no CV) actually competitive (+5.9 % on Podun) |
| 6 (live) | Manual tool-calling loop on Iconik 8 (round-5 fail) | Crop → walls → outline → 2-fixture cross-check → ~75 m² interior. Demonstrates that the missing piece is the loop, not better tools. |

### Gotchas to remember (don't re-discover)
- **CubiCasa5K original Apache-2.0 weights**: gdrive permission-denied
  since 5/2026. Community retrains on HF are broken (per-class IoU 0.0).
- **MitUNet weights are CC-BY-NC**. Non-commercial only.
- **Florence-2** needs `flash_attn` (CUDA-only) on transformers ≤ 4.41,
  breaks on ≥ 4.45. Don't waste time.
- **MobileSAM** stand-alone everything-segmentation: 30 unfiltered
  masks, useless without prompts.
- **Egress blocked**: archive.org, zenodo.org, dataverse.harvard.edu,
  upload.wikimedia.org, cdn.huggingface.co. **Egress works**:
  github.com, raw.githubusercontent.com, huggingface.co (incl LFS),
  images.adsttc.com, sreality.cz, bezrealitky.cz, archiweb.cz.
- **`scale_consistency_w_h < 0.6`** is the auto-flag rule that caught
  3/3 fail-cases in round 5 with zero false positives.
- **Listed-total invariant + floor-sum invariant** together resolve
  ArchDaily metadata ambiguity (round 4 Podun) without external lookup.

---

## 4. Verification disciplines

When you finish a measurement, check at least one of these. The pipeline
is allowed to be ±10 % wrong, but it must *know* when it is wrong.

1. **Listed-total invariant**: Σ (per-floor pipeline area × instances) ≈
   listed gross floor area. ±10 % flags review.
2. **Floor-sum invariant**: typical-floor area should dominate. If F2…F5
   are uniform but F1 is 3× larger, F1 is probably broken (parking floor
   eating property lines — Podun F1).
3. **Two-source GT**: never trust ArchDaily "Area" alone. Cross-reference
   against sreality "Užitná plocha", katastr "výměra", or the floor-plan
   note "Užitná plocha celkem".
4. **Scale consistency**: `min(px_per_m_w, px_per_m_h) /
   max(px_per_m_w, px_per_m_h)`. Below 0.6 → reject the result, fall
   back to the second-best detector or human review.
5. **Fixture cross-check**: anchor scale via two independent fixtures
   (e.g., door arc 0.9 m + bathtub 1.7 m). If they disagree by > 25 %,
   flag.

---

## 5. Repo layout

```
samples/                  test plans
  real_multifloor/        Iconik + Podun (round 4/5)
  real/hf/                Arabic floor-plan dataset (round 2)
  synth_clean.png         deterministic IoU-0.92 baseline (round 1)
src/                      pipeline code (each round = one runnable file)
  tools.py                pre-tested snippets — you may ignore these
  experiment.py           round 1 baseline
  pretrained_check.py     round 2 community-model audit
  round4_pipeline.py      round 4 multi-floor
  round5_pipeline.py      round 5 v1/v2/vlm_rect comparison
out/                      per-round artifacts (overlays, JSON, logs)
models/                   pretrained weights (large LFS)
  mitunet/                CubiCasa CC-BY-NC weights (257 MB)
REPORT.md                 full empirical write-up — START HERE
manifest.json             buildings + ground-truth metadata
```

`.venv` already provisioned with cv2, torch, smp, albumentations,
shapely, easyocr, paddleocr, anthropic, segmentation_models_pytorch.

---

If something here is stale relative to `REPORT.md`, `REPORT.md` wins —
this file is an index, that file is the diary.
