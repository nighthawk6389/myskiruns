#!/usr/bin/env python3
"""Step 3b: SAM 2 interactive refinement for missed trails.

Interactive matplotlib UI where you click on trails the CV pipeline missed,
SAM 2 segments them, and you assign trail names.

Requirements:
    pip install sam2 torch

Usage:
    python 03b_sam_refine.py                # Interactive refinement session
    python 03b_sam_refine.py --resume       # Resume from saved progress
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"
POLYLINES_PATH = OUTPUT_DIR / "extracted_polylines.json"
REFINEMENTS_PATH = OUTPUT_DIR / "sam_refinements.json"

COLOR_MAP = {
    "green": (0, 0.78, 0),
    "blue": (0, 0.31, 1.0),
    "magenta": (1.0, 0, 1.0),
    "black": (0.4, 0.4, 0.4),
}


def check_sam2_available():
    """Check if SAM 2 is available and return the model."""
    try:
        # Try to import SAM 2
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        return True
    except ImportError:
        return False


def load_existing_polylines():
    """Load already-extracted polylines for overlay."""
    if not POLYLINES_PATH.exists():
        return []
    data = json.loads(POLYLINES_PATH.read_text())
    return data.get("accepted", [])


def load_refinements():
    """Load saved refinements from previous session."""
    if not REFINEMENTS_PATH.exists():
        return {"trails": [], "masks": []}
    return json.loads(REFINEMENTS_PATH.read_text())


def save_refinements(refinements):
    """Save refinements to disk."""
    REFINEMENTS_PATH.write_text(json.dumps(refinements, indent=2))


class SAMRefineUI:
    """Interactive matplotlib UI for SAM 2 trail refinement."""

    def __init__(self, img, predictor, existing_polylines, refinements):
        import matplotlib.pyplot as plt
        from matplotlib.widgets import TextBox

        self.img = img
        self.img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.predictor = predictor
        self.existing = existing_polylines
        self.refinements = refinements

        self.positive_points = []
        self.negative_points = []
        self.current_mask = None
        self.mode = "click"  # click, accept

        # Set up figure
        self.fig, self.ax = plt.subplots(1, 1, figsize=(16, 10))
        self.fig.subplots_adjust(bottom=0.15)
        self.ax.set_title(
            f"SAM 2 Refinement — {len(refinements.get('trails', []))} trails saved\n"
            "Left-click: add point | Shift+click: add point | Right-click: negative point\n"
            "Enter: accept | Escape: clear | S: save | Q: quit",
            fontsize=10,
        )
        self.ax.imshow(self.img_rgb)

        # Draw existing polylines
        for trail in self.existing:
            pts = trail["points"]
            color = COLOR_MAP.get(trail["color"], (1, 1, 1))
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            self.ax.plot(xs, ys, color=color, linewidth=1, alpha=0.3)

        # Draw previously refined trails
        for refined in refinements.get("trails", []):
            pts = refined["points"]
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            self.ax.plot(xs, ys, color="gold", linewidth=2, alpha=0.7)

        # Point markers
        self.pos_scatter = self.ax.scatter([], [], c="lime", s=50, zorder=5, marker="o")
        self.neg_scatter = self.ax.scatter([], [], c="red", s=50, zorder=5, marker="x")

        # Mask overlay
        self.mask_overlay = None

        # Text box for trail name
        ax_text = self.fig.add_axes([0.15, 0.02, 0.5, 0.04])
        self.text_box = TextBox(ax_text, "Trail ID: ", initial="")

        # Connect events
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("key_press_event", self.on_key)

        plt.show()

    def on_click(self, event):
        if event.inaxes != self.ax:
            return

        x, y = int(event.xdata), int(event.ydata)

        if event.button == 3:  # Right click = negative point
            self.negative_points.append([x, y])
        else:  # Left click = positive point
            self.positive_points.append([x, y])

        self.update_points_display()
        self.run_sam_prediction()

    def on_key(self, event):
        if event.key == "escape":
            self.clear_current()
        elif event.key == "enter":
            self.accept_mask()
        elif event.key == "s":
            save_refinements(self.refinements)
            print(f"Saved {len(self.refinements.get('trails', []))} refinements")
        elif event.key == "q":
            save_refinements(self.refinements)
            print("Saved and quitting.")
            import matplotlib.pyplot as plt
            plt.close(self.fig)
        elif event.key == "u":
            # Undo last point
            if self.positive_points:
                self.positive_points.pop()
            elif self.negative_points:
                self.negative_points.pop()
            self.update_points_display()
            if self.positive_points or self.negative_points:
                self.run_sam_prediction()
            else:
                self.clear_mask_overlay()

    def update_points_display(self):
        if self.positive_points:
            pos = np.array(self.positive_points)
            self.pos_scatter.set_offsets(pos)
        else:
            self.pos_scatter.set_offsets(np.empty((0, 2)))

        if self.negative_points:
            neg = np.array(self.negative_points)
            self.neg_scatter.set_offsets(neg)
        else:
            self.neg_scatter.set_offsets(np.empty((0, 2)))

        self.fig.canvas.draw_idle()

    def run_sam_prediction(self):
        """Run SAM 2 prediction with current points."""
        if not self.positive_points and not self.negative_points:
            return

        all_points = self.positive_points + self.negative_points
        labels = [1] * len(self.positive_points) + [0] * len(self.negative_points)

        point_coords = np.array(all_points)
        point_labels = np.array(labels)

        print("  Running SAM 2 prediction...")
        masks, scores, _ = self.predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            multimask_output=True,
        )

        # Take the highest-scoring mask
        best_idx = np.argmax(scores)
        self.current_mask = masks[best_idx]

        # Display mask overlay
        self.clear_mask_overlay()
        mask_display = np.zeros((*self.current_mask.shape, 4))
        mask_display[self.current_mask] = [1, 0.3, 0, 0.4]  # orange overlay
        self.mask_overlay = self.ax.imshow(mask_display, alpha=0.5)
        self.fig.canvas.draw_idle()
        print(f"  Mask area: {np.count_nonzero(self.current_mask)} pixels, "
              f"score: {scores[best_idx]:.3f}")

    def clear_mask_overlay(self):
        if self.mask_overlay is not None:
            self.mask_overlay.remove()
            self.mask_overlay = None

    def clear_current(self):
        self.positive_points = []
        self.negative_points = []
        self.current_mask = None
        self.clear_mask_overlay()
        self.update_points_display()
        self.fig.canvas.draw_idle()

    def accept_mask(self):
        """Accept current mask and prompt for trail name."""
        if self.current_mask is None:
            print("  No mask to accept. Click on a trail first.")
            return

        trail_id = self.text_box.text.strip()
        if not trail_id:
            print("  Enter a trail ID in the text box first, then press Enter.")
            return

        # Skeletonize the mask to get a polyline
        from skimage.morphology import skeletonize
        skeleton = skeletonize(self.current_mask)
        ys, xs = np.where(skeleton)

        if len(ys) < 3:
            print("  Mask too small to extract polyline.")
            return

        # Order points (simple: sort by y then follow skeleton)
        points = list(zip(xs.tolist(), ys.tolist()))
        # Simplify
        pts_array = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
        simplified = cv2.approxPolyDP(pts_array, 3.0, closed=False)
        points = [[int(p[0][0]), int(p[0][1])] for p in simplified]

        refined_trail = {
            "id": trail_id,
            "points": points,
            "color": "refined",
            "num_points": len(points),
        }

        if "trails" not in self.refinements:
            self.refinements["trails"] = []
        self.refinements["trails"].append(refined_trail)

        # Draw the accepted trail
        xs_plot = [p[0] for p in points]
        ys_plot = [p[1] for p in points]
        self.ax.plot(xs_plot, ys_plot, color="gold", linewidth=2, alpha=0.8)

        print(f"  Accepted: {trail_id} ({len(points)} points)")

        # Clear for next trail
        self.text_box.set_val("")
        self.clear_current()
        self.ax.set_title(
            f"SAM 2 Refinement — {len(self.refinements['trails'])} trails saved",
            fontsize=10,
        )
        self.fig.canvas.draw_idle()


def run_without_sam(img, existing_polylines, refinements):
    """Run the UI in manual point-placement mode (no SAM 2)."""
    import matplotlib.pyplot as plt
    from matplotlib.widgets import TextBox

    print("\nSAM 2 not available. Running in manual polyline tracing mode.")
    print("Left-click to add points. Enter to accept. Escape to clear.")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.subplots_adjust(bottom=0.15)
    ax.set_title("Manual Trail Tracing (no SAM 2)\nClick to add points | Enter: accept | Escape: clear | Q: quit")
    ax.imshow(img_rgb)

    # Draw existing
    for trail in existing_polylines:
        pts = trail["points"]
        color = COLOR_MAP.get(trail["color"], (1, 1, 1))
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.plot(xs, ys, color=color, linewidth=1, alpha=0.3)

    current_points = []
    scatter = ax.scatter([], [], c="lime", s=30, zorder=5)
    line, = ax.plot([], [], "g-", linewidth=2, alpha=0.7)

    ax_text = fig.add_axes([0.15, 0.02, 0.5, 0.04])
    text_box = TextBox(ax_text, "Trail ID: ", initial="")

    def on_click(event):
        if event.inaxes != ax or event.button != 1:
            return
        current_points.append([int(event.xdata), int(event.ydata)])
        pts = np.array(current_points)
        scatter.set_offsets(pts)
        line.set_data(pts[:, 0], pts[:, 1])
        fig.canvas.draw_idle()

    def on_key(event):
        nonlocal current_points
        if event.key == "escape":
            current_points = []
            scatter.set_offsets(np.empty((0, 2)))
            line.set_data([], [])
            fig.canvas.draw_idle()
        elif event.key == "enter":
            trail_id = text_box.text.strip()
            if not trail_id or not current_points:
                return
            refinements.setdefault("trails", []).append({
                "id": trail_id,
                "points": current_points.copy(),
                "color": "manual",
                "num_points": len(current_points),
            })
            ax.plot([p[0] for p in current_points], [p[1] for p in current_points],
                    color="gold", linewidth=2)
            print(f"  Saved: {trail_id} ({len(current_points)} points)")
            current_points = []
            scatter.set_offsets(np.empty((0, 2)))
            line.set_data([], [])
            text_box.set_val("")
            fig.canvas.draw_idle()
        elif event.key == "s":
            save_refinements(refinements)
            print(f"Saved {len(refinements.get('trails', []))} refinements")
        elif event.key == "q":
            save_refinements(refinements)
            plt.close(fig)

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--resume", action="store_true", help="Resume from saved progress")
    args = parser.parse_args()

    if not IMAGE_PATH.exists():
        print("ERROR: Run 01_convert_pdf.py first.")
        sys.exit(1)

    print("Loading image...")
    img = cv2.imread(str(IMAGE_PATH))
    print(f"  {img.shape[1]}x{img.shape[0]}")

    existing = load_existing_polylines()
    print(f"Loaded {len(existing)} existing polylines")

    refinements = load_refinements() if args.resume else {"trails": []}
    if args.resume:
        print(f"Resuming with {len(refinements.get('trails', []))} saved refinements")

    has_sam2 = check_sam2_available()

    if has_sam2:
        print("\nLoading SAM 2 (tiny model)...")
        from sam2.build_sam import build_sam2
        from sam2.sam2_image_predictor import SAM2ImagePredictor

        # Use tiny model for CPU
        sam2 = build_sam2("sam2_hiera_t", "sam2_hiera_tiny.pt")
        predictor = SAM2ImagePredictor(sam2)

        print("Computing image embedding (this takes ~30s on CPU)...")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        predictor.set_image(img_rgb)
        print("Embedding ready!")

        ui = SAMRefineUI(img, predictor, existing, refinements)
    else:
        print("\nSAM 2 not installed. Install with: pip install sam2 torch")
        print("Falling back to manual tracing mode...")
        run_without_sam(img, existing, refinements)

    # Save final state
    save_refinements(refinements)
    print(f"\nDone. {len(refinements.get('trails', []))} trails refined.")
    print(f"Saved to {REFINEMENTS_PATH}")


if __name__ == "__main__":
    main()
