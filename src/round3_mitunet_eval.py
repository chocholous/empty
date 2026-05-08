"""Quantitative IoU on synth_clean: MitUNet vs OpenCV adaptive vs GT."""
import json, cv2, numpy as np

# Build GT wall mask from synth.py logic: each room is a black rectangle frame, wall_px=6
with open("samples/synth_clean.gt.json") as f:
    gt = json.load(f)
W, H = gt["image_size"]
wall_px = 6  # synth.py default
gt_mask = np.zeros((H, W), np.uint8)
for r in gt["rooms"]:
    x1, y1, x2, y2 = r["bbox_px"]
    cv2.rectangle(gt_mask, (x1, y1), (x2, y2), 255, wall_px)

cv2.imwrite("out/synth_clean.gt_walls.png", gt_mask)

# Load MitUNet mask
mit = cv2.imread("out/synth_clean.mitunet.png", cv2.IMREAD_GRAYSCALE)
mit_bin = (mit > 127).astype(np.uint8) * 255

# Make CV adaptive mask (matching tools.py)
img = cv2.imread("samples/synth_clean.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv_adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                 cv2.THRESH_BINARY_INV, 35, 10)

def iou(a, b):
    a = (a > 0); b = (b > 0)
    inter = (a & b).sum()
    union = (a | b).sum()
    return float(inter) / float(union) if union else 0.0

def precision_recall(pred, gt):
    pred = (pred > 0); gt = (gt > 0)
    tp = (pred & gt).sum()
    fp = (pred & ~gt).sum()
    fn = (~pred & gt).sum()
    p = tp / (tp + fp) if (tp + fp) else 0
    r = tp / (tp + fn) if (tp + fn) else 0
    return float(p), float(r)

# To be fair, dilate GT slightly because MitUNet walls may shift by 1-2 px in resize
gt_dil = cv2.dilate(gt_mask, np.ones((3, 3), np.uint8), iterations=1)

out = {}
for name, pred in [("mitunet", mit_bin), ("opencv_adaptive", cv_adapt)]:
    out[name] = {
        "iou_strict": round(iou(pred, gt_mask), 3),
        "iou_dilated_gt": round(iou(pred, gt_dil), 3),
        "precision_strict": round(precision_recall(pred, gt_mask)[0], 3),
        "recall_strict":    round(precision_recall(pred, gt_mask)[1], 3),
    }
print(json.dumps(out, indent=2))
with open("out/round3_mitunet_iou.json", "w") as f:
    json.dump(out, f, indent=2)

# Side-by-side viz
import numpy as np
viz = np.zeros((H, W * 3, 3), np.uint8)
viz[:, :W] = cv2.cvtColor(gt_mask, cv2.COLOR_GRAY2BGR)
viz[:, W:2*W] = cv2.cvtColor(cv_adapt, cv2.COLOR_GRAY2BGR)
viz[:, 2*W:] = cv2.cvtColor(mit_bin, cv2.COLOR_GRAY2BGR)
cv2.putText(viz, "GT", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.putText(viz, "OpenCV adaptive", (W + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
cv2.putText(viz, "MitUNet", (2 * W + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
cv2.imwrite("out/synth_clean.wall_compare.png", viz)
print("wrote out/synth_clean.wall_compare.png")
