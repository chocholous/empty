"""MitUNet smoke test on our 3 samples + comparison vs OpenCV adaptive."""
import time, json, os
import torch
import cv2
import numpy as np
import segmentation_models_pytorch as smp
import albumentations as A
from albumentations.pytorch import ToTensorV2

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
WEIGHTS = "models/mitunet/experiments/models/mitunet_finetune_a6_mit_b4_tversky_8864_28E.pth"

print(f"device: {DEVICE}, torch: {torch.__version__}")

t0 = time.time()
aux = smp.Segformer(encoder_name="mit_b4", encoder_weights=None)
model = smp.Unet(encoder_name="mit_b4", encoder_weights=None,
                 in_channels=3, classes=1, decoder_attention_type="scse")
model.encoder = aux.encoder
sd = torch.load(WEIGHTS, map_location=DEVICE, weights_only=False)
model.load_state_dict(sd)
model.to(DEVICE).eval()
print(f"load: {time.time()-t0:.1f}s, params: {sum(p.numel() for p in model.parameters())/1e6:.1f} M")

transform = A.Compose([
    A.Resize(512, 512),
    A.Normalize(mean=(0.485,0.456,0.406), std=(0.229,0.224,0.225)),
    ToTensorV2(),
])

results = {}
for img_path in ["samples/synth_clean.png", "samples/hf_00.png", "samples/hf_01.png"]:
    image = cv2.imread(img_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    H, W = image.shape[:2]
    aug = transform(image=image_rgb)
    x = aug["image"].unsqueeze(0).to(DEVICE)
    t0 = time.time()
    with torch.no_grad():
        logits = model(x)
        prob = torch.sigmoid(logits)
        mask = (prob > 0.5).float().squeeze().cpu().numpy().astype(np.uint8)
    dt = time.time() - t0

    # Resize back to original
    mask_full = cv2.resize(mask, (W, H), interpolation=cv2.INTER_NEAREST)
    out_p = f"out/{os.path.splitext(os.path.basename(img_path))[0]}.mitunet.png"
    cv2.imwrite(out_p, mask_full * 255)

    # Compare wall-pixel ratio with OpenCV adaptive (from existing tools.py)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    th = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                               cv2.THRESH_BINARY_INV, 35, 10)
    cv_ratio = float((th > 0).mean())
    mit_ratio = float(mask_full.mean())  # already 0/1

    results[img_path] = {
        "mitunet_seconds": round(dt, 2),
        "image_size": [W, H],
        "mitunet_wall_ratio": round(mit_ratio, 4),
        "opencv_adaptive_wall_ratio": round(cv_ratio, 4),
        "out_mask": out_p,
    }
    print(f"{img_path}: mit {dt:.1f}s wall_ratio={mit_ratio:.3f} (vs cv adaptive {cv_ratio:.3f})")

with open("out/round3_mitunet.json", "w") as f:
    json.dump(results, f, indent=2)
print("WROTE out/round3_mitunet.json")
