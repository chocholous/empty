"""Generate a synthetic floor plan with known ground truth (rooms, areas, scale)."""
from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict

import cv2
import numpy as np


@dataclass
class Room:
    name: str
    x_m: float
    y_m: float
    w_m: float
    h_m: float

    @property
    def area_m2(self) -> float:
        return self.w_m * self.h_m


def render(rooms: list[Room], out_png: str, out_gt: str, px_per_m: int = 50,
           wall_px: int = 6, margin_px: int = 40, with_dims: bool = True) -> None:
    max_x = max(r.x_m + r.w_m for r in rooms)
    max_y = max(r.y_m + r.h_m for r in rooms)
    W = int(max_x * px_per_m) + 2 * margin_px
    H = int(max_y * px_per_m) + 2 * margin_px
    img = np.full((H, W, 3), 255, np.uint8)

    def to_px(x_m: float, y_m: float) -> tuple[int, int]:
        return int(margin_px + x_m * px_per_m), int(margin_px + y_m * px_per_m)

    for r in rooms:
        x1, y1 = to_px(r.x_m, r.y_m)
        x2, y2 = to_px(r.x_m + r.w_m, r.y_m + r.h_m)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), wall_px)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.putText(img, r.name, (cx - 60, cy - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
        if with_dims:
            label = f"{r.w_m:.2f}x{r.h_m:.2f}"
            cv2.putText(img, label, (cx - 50, cy + 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (60, 60, 60), 1, cv2.LINE_AA)

    bar_y = H - 18
    bar_x1 = margin_px
    bar_x2 = bar_x1 + px_per_m
    cv2.line(img, (bar_x1, bar_y), (bar_x2, bar_y), (0, 0, 0), 2)
    cv2.line(img, (bar_x1, bar_y - 5), (bar_x1, bar_y + 5), (0, 0, 0), 2)
    cv2.line(img, (bar_x2, bar_y - 5), (bar_x2, bar_y + 5), (0, 0, 0), 2)
    cv2.putText(img, "1 m", (bar_x2 + 6, bar_y + 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    cv2.imwrite(out_png, img)

    gt = {
        "px_per_m": px_per_m,
        "margin_px": margin_px,
        "image_size": [W, H],
        "rooms": [
            {**asdict(r), "area_m2": r.area_m2,
             "bbox_px": [
                 *to_px(r.x_m, r.y_m),
                 *to_px(r.x_m + r.w_m, r.y_m + r.h_m),
             ]}
            for r in rooms
        ],
        "total_area_m2": sum(r.area_m2 for r in rooms),
    }
    with open(out_gt, "w") as f:
        json.dump(gt, f, indent=2)


if __name__ == "__main__":
    os.makedirs("samples", exist_ok=True)
    rooms = [
        Room("kitchen",  0.0, 0.0, 3.5, 4.0),
        Room("living",   3.5, 0.0, 5.0, 4.0),
        Room("bath",     0.0, 4.0, 2.5, 3.0),
        Room("bed1",     2.5, 4.0, 3.5, 3.0),
        Room("bed2",     6.0, 4.0, 2.5, 3.0),
    ]
    render(rooms, "samples/synth_clean.png", "samples/synth_clean.gt.json")
    render(rooms, "samples/synth_nodims.png", "samples/synth_nodims.gt.json",
           with_dims=False)
    print("Generated samples/synth_clean.png + .gt.json")
    print("Generated samples/synth_nodims.png + .gt.json")
