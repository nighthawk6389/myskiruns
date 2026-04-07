#!/usr/bin/env python3
"""Step 4: Trail identification — match extracted polylines to trail names.

Uses Claude Vision API to read text labels on the trail map and match
numbered polyline overlays to known trail names.

Usage:
    python 04_identify_trails.py --prepare   # Generate annotated patches only
    python 04_identify_trails.py --identify  # Run LLM identification (requires ANTHROPIC_API_KEY)
    python 04_identify_trails.py             # Both steps
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR / "output"
PATCHES_DIR = OUTPUT_DIR / "patches"
IMAGE_PATH = OUTPUT_DIR / "trailmap_300dpi.png"
POLYLINES_PATH = OUTPUT_DIR / "extracted_polylines.json"
META_PATH = OUTPUT_DIR / "image_meta.json"
OVERRIDES_PATH = SCRIPT_DIR / "manual_overrides.json"
IDENTIFICATIONS_PATH = OUTPUT_DIR / "trail_identifications.json"

# Known trail data from trails.ts
TRAILS_BY_PEAK = {
    "snowshed": {
        "region": {"x_pct": (0, 16), "y_pct": (30, 100)},
        "trails": [
            {"id": "snowshed-slope", "name": "Snowshed", "difficulty": "green"},
            {"id": "yodeler", "name": "Yodeler", "difficulty": "green"},
            {"id": "idler", "name": "Idler", "difficulty": "green"},
            {"id": "snow-play", "name": "Snow Play", "difficulty": "green"},
            {"id": "snowshed-crossover", "name": "Crossover", "difficulty": "green"},
        ],
    },
    "sunrise": {
        "region": {"x_pct": (10, 25), "y_pct": (25, 100)},
        "trails": [
            {"id": "sun-dog", "name": "Sun Dog", "difficulty": "green"},
            {"id": "rendezvous", "name": "Rendezvous", "difficulty": "green"},
            {"id": "bear-cub", "name": "Bear Cub", "difficulty": "green"},
            {"id": "bear-view", "name": "Bear View", "difficulty": "blue"},
            {"id": "sunrise-connector", "name": "Sunrise Connector", "difficulty": "green"},
        ],
    },
    "ramshead": {
        "region": {"x_pct": (18, 38), "y_pct": (15, 100)},
        "trails": [
            {"id": "easy-street", "name": "Easy Street", "difficulty": "green"},
            {"id": "swirl", "name": "Swirl", "difficulty": "green"},
            {"id": "treezy", "name": "Treezy", "difficulty": "green"},
            {"id": "squeeze-play", "name": "Squeeze Play", "difficulty": "green"},
            {"id": "ramshead-run", "name": "Ramshead Run", "difficulty": "green"},
            {"id": "ramshead-liftline", "name": "Ramshead Liftline", "difficulty": "blue"},
            {"id": "header", "name": "Header", "difficulty": "blue"},
            {"id": "vagabond", "name": "Vagabond", "difficulty": "blue"},
            {"id": "caper", "name": "Caper", "difficulty": "blue"},
            {"id": "timberline", "name": "Timberline", "difficulty": "blue"},
            {"id": "start-park", "name": "Start Park", "difficulty": "green"},
        ],
    },
    "snowdon": {
        "region": {"x_pct": (30, 52), "y_pct": (10, 100)},
        "trails": [
            {"id": "great-northern", "name": "Great Northern", "difficulty": "blue"},
            {"id": "bunny-buster", "name": "Bunny Buster", "difficulty": "green"},
            {"id": "chute", "name": "Chute", "difficulty": "black"},
            {"id": "conclusion", "name": "Conclusion", "difficulty": "double-black"},
            {"id": "upper-fis", "name": "Upper FIS", "difficulty": "green"},
            {"id": "mountain-run", "name": "Mountain Run", "difficulty": "green"},
            {"id": "mountain-training", "name": "Mountain Training Station", "difficulty": "green"},
            {"id": "snowdon-liftline", "name": "Snowdon Liftline", "difficulty": "blue"},
            {"id": "upper-snowdon", "name": "Upper Snowdon", "difficulty": "blue"},
            {"id": "lower-snowdon", "name": "Lower Snowdon", "difficulty": "blue"},
            {"id": "bittersweet", "name": "Bittersweet", "difficulty": "blue"},
            {"id": "sass", "name": "Sass", "difficulty": "blue"},
            {"id": "northstar", "name": "Northstar", "difficulty": "black"},
            {"id": "royal-flush", "name": "Royal Flush", "difficulty": "black"},
            {"id": "upper-northbrook", "name": "Upper Northbrook", "difficulty": "blue"},
            {"id": "lower-northbrook", "name": "Lower Northbrook", "difficulty": "green"},
            {"id": "snowdon-glades", "name": "Snowdon Glades", "difficulty": "black"},
        ],
    },
    "skye-peak": {
        "region": {"x_pct": (42, 72), "y_pct": (5, 100)},
        "trails": [
            {"id": "skyelark", "name": "Skyelark", "difficulty": "blue"},
            {"id": "upper-skyelark", "name": "Upper Skyelark", "difficulty": "blue"},
            {"id": "skyeburst", "name": "Skyeburst", "difficulty": "blue"},
            {"id": "upper-skyeburst", "name": "Upper Skyeburst", "difficulty": "blue"},
            {"id": "skye-hawk", "name": "Skye Hawk", "difficulty": "blue"},
            {"id": "cruise-control", "name": "Cruise Control", "difficulty": "blue"},
            {"id": "mouse-trap", "name": "Mouse Trap", "difficulty": "blue"},
            {"id": "somewhere", "name": "Somewhere", "difficulty": "blue"},
            {"id": "breakaway", "name": "Breakaway", "difficulty": "blue"},
            {"id": "touch-down", "name": "Touch Down", "difficulty": "blue"},
            {"id": "patsys", "name": "Patsy's", "difficulty": "blue"},
            {"id": "twister", "name": "Twister", "difficulty": "blue"},
            {"id": "catwalk", "name": "Catwalk", "difficulty": "blue"},
            {"id": "great-eastern", "name": "Great Eastern", "difficulty": "green"},
            {"id": "home-stretch", "name": "Home Stretch", "difficulty": "green"},
            {"id": "juggernaut", "name": "Juggernaut", "difficulty": "green"},
            {"id": "vertigo", "name": "Vertigo", "difficulty": "double-black"},
            {"id": "ovation", "name": "Ovation", "difficulty": "double-black"},
            {"id": "needles-eye", "name": "Needle's Eye", "difficulty": "black"},
            {"id": "panic-button", "name": "Panic Button", "difficulty": "black"},
            {"id": "dream-maker", "name": "Dream Maker", "difficulty": "black"},
            {"id": "highline", "name": "Highline", "difficulty": "black"},
            {"id": "pipe-dream", "name": "Pipe Dream", "difficulty": "blue"},
            {"id": "valley-plunge", "name": "Valley Plunge", "difficulty": "blue"},
            {"id": "roundabout", "name": "Roundabout", "difficulty": "blue"},
            {"id": "great-bear", "name": "Great Bear", "difficulty": "blue"},
        ],
    },
    "killington-peak": {
        "region": {"x_pct": (60, 88), "y_pct": (0, 100)},
        "trails": [
            {"id": "superstar", "name": "Superstar", "difficulty": "black"},
            {"id": "cascade", "name": "Cascade", "difficulty": "double-black"},
            {"id": "downdraft", "name": "Downdraft", "difficulty": "double-black"},
            {"id": "double-dipper", "name": "Double Dipper", "difficulty": "double-black"},
            {"id": "flume", "name": "Flume", "difficulty": "black"},
            {"id": "escapade", "name": "Escapade", "difficulty": "black"},
            {"id": "east-fall", "name": "East Fall", "difficulty": "black"},
            {"id": "rime", "name": "Rime", "difficulty": "black"},
            {"id": "reason", "name": "Reason", "difficulty": "black"},
            {"id": "julio", "name": "Julio", "difficulty": "black"},
            {"id": "high-road", "name": "High Road", "difficulty": "blue"},
            {"id": "north-way", "name": "North Way", "difficulty": "blue"},
            {"id": "great-eastern-kp", "name": "Great Eastern (K.P.)", "difficulty": "green"},
            {"id": "fis", "name": "FIS", "difficulty": "black"},
            {"id": "solitude", "name": "Solitude", "difficulty": "blue"},
            {"id": "k1-gondola-run", "name": "K-1 Gondola Run", "difficulty": "blue"},
            {"id": "upper-canyon", "name": "Upper Canyon", "difficulty": "black"},
            {"id": "lower-canyon", "name": "Lower Canyon", "difficulty": "black"},
            {"id": "old-superstar", "name": "Old Superstar", "difficulty": "black"},
            {"id": "killington-liftline", "name": "Killington Liftline", "difficulty": "black"},
            {"id": "header-kp", "name": "Header", "difficulty": "blue"},
            {"id": "mouse-run", "name": "Mouse Run", "difficulty": "blue"},
            {"id": "low-road", "name": "Low Road", "difficulty": "green"},
            {"id": "the-mall", "name": "The Mall", "difficulty": "green"},
        ],
    },
    "bear-mountain": {
        "region": {"x_pct": (80, 100), "y_pct": (10, 100)},
        "trails": [
            {"id": "outer-limits", "name": "Outer Limits", "difficulty": "double-black"},
            {"id": "devils-fiddle", "name": "Devil's Fiddle", "difficulty": "double-black"},
            {"id": "wildfire", "name": "Wildfire", "difficulty": "black"},
            {"id": "bear-claw", "name": "Bear Claw", "difficulty": "blue"},
            {"id": "bear-trax", "name": "Bear Trax", "difficulty": "blue"},
            {"id": "falls-brook", "name": "Falls Brook", "difficulty": "blue"},
            {"id": "bear-mountain-liftline", "name": "Bear Mountain Liftline", "difficulty": "black"},
            {"id": "the-stash", "name": "The Stash", "difficulty": "black"},
            {"id": "lower-wildfire", "name": "Lower Wildfire", "difficulty": "blue"},
            {"id": "bear-run", "name": "Bear Run", "difficulty": "blue"},
        ],
    },
}

# Map difficulty to expected extracted color
DIFFICULTY_TO_COLOR = {
    "green": "green",
    "blue": "blue",
    "black": "black",
    "double-black": "magenta",
}

COLOR_MAP_BGR = {
    "green": (0, 200, 0),
    "blue": (255, 80, 0),
    "magenta": (255, 0, 255),
    "black": (100, 100, 100),
}


def load_data():
    meta = json.loads(META_PATH.read_text())
    polylines = json.loads(POLYLINES_PATH.read_text())
    return meta, polylines


def polyline_centroid_pct(polyline: dict, img_w: int, img_h: int) -> tuple:
    """Get centroid of a polyline as percentage of image dimensions."""
    pts = polyline["points"]
    if not pts:
        return (50, 50)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx = sum(xs) / len(xs) / img_w * 100
    cy = sum(ys) / len(ys) / img_h * 100
    return (cx, cy)


def polylines_in_region(polylines: list, region: dict,
                        img_w: int, img_h: int) -> list:
    """Filter polylines whose centroid falls within a peak region."""
    x_lo, x_hi = region["x_pct"]
    y_lo, y_hi = region["y_pct"]
    result = []
    for p in polylines:
        cx, cy = polyline_centroid_pct(p, img_w, img_h)
        if x_lo <= cx <= x_hi and y_lo <= cy <= y_hi:
            result.append(p)
    return result


def prepare_patches(img: np.ndarray, polylines: list, meta: dict):
    """Create annotated image patches per peak region for LLM identification."""
    PATCHES_DIR.mkdir(parents=True, exist_ok=True)
    img_w, img_h = meta["width"], meta["height"]
    accepted = polylines["accepted"]

    patch_info = {}

    for peak_id, peak_data in TRAILS_BY_PEAK.items():
        region = peak_data["region"]
        region_polylines = polylines_in_region(accepted, region, img_w, img_h)

        if not region_polylines:
            print(f"  {peak_id}: no polylines in region, skipping")
            continue

        # Crop image to region (with padding)
        x_lo = max(0, int(region["x_pct"][0] / 100 * img_w) - 100)
        x_hi = min(img_w, int(region["x_pct"][1] / 100 * img_w) + 100)
        y_lo = max(0, int(region["y_pct"][0] / 100 * img_h) - 100)
        y_hi = min(img_h, int(region["y_pct"][1] / 100 * img_h) + 100)

        crop = img[y_lo:y_hi, x_lo:x_hi].copy()

        # Draw numbered polylines on the crop
        for idx, trail in enumerate(region_polylines):
            color = COLOR_MAP_BGR.get(trail["color"], (255, 255, 255))
            pts = np.array(trail["points"], dtype=np.int32)
            # Offset to crop coordinates
            pts[:, 0] -= x_lo
            pts[:, 1] -= y_lo

            cv2.polylines(crop, [pts], isClosed=False, color=color,
                          thickness=4, lineType=cv2.LINE_AA)

            # Number label at midpoint
            mid = pts[len(pts) // 2]
            label = str(idx)
            cv2.putText(crop, label, (mid[0] + 8, mid[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3)
            cv2.putText(crop, label, (mid[0] + 8, mid[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 1)

        # Scale down if too large (max 2000px on longest side)
        max_dim = max(crop.shape[:2])
        if max_dim > 2000:
            scale = 2000 / max_dim
            crop = cv2.resize(crop, (int(crop.shape[1] * scale),
                                     int(crop.shape[0] * scale)))

        patch_path = PATCHES_DIR / f"patch_{peak_id}.jpg"
        cv2.imwrite(str(patch_path), crop, [cv2.IMWRITE_JPEG_QUALITY, 92])

        # Build trail list for the prompt
        trail_names = [f"{t['id']} ({t['name']}, {t['difficulty']})"
                       for t in peak_data["trails"]]

        patch_info[peak_id] = {
            "patch_path": str(patch_path),
            "num_polylines": len(region_polylines),
            "polyline_ids": [t["id"] for t in region_polylines],
            "polyline_colors": [t["color"] for t in region_polylines],
            "expected_trails": trail_names,
            "region": region,
        }
        print(f"  {peak_id}: {len(region_polylines)} polylines, "
              f"{len(peak_data['trails'])} expected trails")

    # Save patch info
    info_path = OUTPUT_DIR / "patch_info.json"
    info_path.write_text(json.dumps(patch_info, indent=2))
    print(f"\nPatch info saved to {info_path}")
    return patch_info


def identify_with_llm(patch_info: dict):
    """Use Claude Vision API to identify trails in each patch."""
    try:
        import anthropic
    except ImportError:
        print("ERROR: anthropic package not installed. Run: pip install anthropic")
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Set it to use LLM identification.")
        print("You can still use manual_overrides.json for manual identification.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    identifications = {}

    for peak_id, info in patch_info.items():
        print(f"\n  Identifying {peak_id}...")

        # Read patch image
        patch_path = info["patch_path"]
        with open(patch_path, "rb") as f:
            img_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Build prompt
        trail_list = "\n".join(f"  - {t}" for t in info["expected_trails"])
        color_list = []
        for i, (pid, col) in enumerate(zip(info["polyline_ids"], info["polyline_colors"])):
            color_list.append(f"  #{i}: {col} line")
        polyline_desc = "\n".join(color_list)

        prompt = f"""This is a section of the Killington ski resort trail map showing the {peak_id.replace('-', ' ').title()} area.

Numbered colored lines have been overlaid on the map. Each numbered line represents a detected ski trail.

The numbered overlaid lines are:
{polyline_desc}

The known trails in this area are:
{trail_list}

For each numbered overlay line, identify which trail it corresponds to by reading the text labels on the map and matching them to the overlay lines spatially.

Respond with ONLY a JSON object mapping line numbers to trail IDs. For lines that don't match any known trail (noise, lift lines, boundaries), use "unknown". Example:
{{"0": "trail-id-here", "1": "unknown", "2": "another-trail-id"}}

Important:
- Match based on the text labels visible on the map, not just color
- Green lines = easy trails, Blue lines = intermediate, Magenta lines = expert/double-black, Gray lines = black/advanced
- Some overlay lines may be fragments of the same trail
- Some lines may be lift lines or boundaries, mark those as "unknown"
"""

        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": img_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }],
            )

            response_text = response.content[0].text
            # Try to extract JSON from the response
            # Handle potential markdown code blocks
            if "```" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]

            mapping = json.loads(response_text)
            identifications[peak_id] = {
                "mapping": mapping,
                "polyline_ids": info["polyline_ids"],
            }
            print(f"    Matched {sum(1 for v in mapping.values() if v != 'unknown')}"
                  f" / {len(mapping)} polylines")

        except Exception as e:
            print(f"    ERROR: {e}")
            identifications[peak_id] = {"error": str(e), "polyline_ids": info["polyline_ids"]}

    return identifications


def apply_overrides(identifications: dict) -> dict:
    """Apply manual overrides from manual_overrides.json."""
    if not OVERRIDES_PATH.exists():
        return identifications

    overrides = json.loads(OVERRIDES_PATH.read_text())
    for polyline_id, trail_id in overrides.items():
        for peak_id, peak_data in identifications.items():
            mapping = peak_data.get("mapping", {})
            polyline_ids = peak_data.get("polyline_ids", [])
            for idx_str, pid in enumerate(polyline_ids):
                if pid == polyline_id:
                    mapping[str(idx_str)] = trail_id
                    print(f"  Override: {polyline_id} → {trail_id}")

    return identifications


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true", help="Only prepare patches")
    parser.add_argument("--identify", action="store_true", help="Only run LLM identification")
    args = parser.parse_args()

    meta, polylines = load_data()
    print(f"Loaded {len(polylines['accepted'])} accepted polylines")

    if args.identify and not args.prepare:
        # Load existing patch info
        info_path = OUTPUT_DIR / "patch_info.json"
        if not info_path.exists():
            print("ERROR: Run with --prepare first")
            sys.exit(1)
        patch_info = json.loads(info_path.read_text())
    else:
        print("\nPreparing annotated patches...")
        img = cv2.imread(str(IMAGE_PATH))
        patch_info = prepare_patches(img, polylines, meta)

    if args.prepare and not args.identify:
        print("\nPatches ready. Run with --identify to use LLM, or set up manual_overrides.json")
        return

    # Run LLM identification
    print("\nRunning LLM identification...")
    identifications = identify_with_llm(patch_info)
    identifications = apply_overrides(identifications)

    IDENTIFICATIONS_PATH.write_text(json.dumps(identifications, indent=2))
    print(f"\nIdentifications saved to {IDENTIFICATIONS_PATH}")


if __name__ == "__main__":
    main()
