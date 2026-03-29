#!/usr/bin/env python3
"""Step 1: Convert trail map PDF to high-resolution PNG."""

import json
import sys
from pathlib import Path

import fitz  # PyMuPDF

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PDF_PATH = PROJECT_ROOT / "TrailMapForWeb-compressed.pdf"
JPG_PATH = PROJECT_ROOT / "public" / "killington-trail-map.jpg"
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_IMAGE = OUTPUT_DIR / "trailmap_300dpi.png"
OUTPUT_META = OUTPUT_DIR / "image_meta.json"

DPI = 300


def convert_pdf(pdf_path: Path, dpi: int = DPI) -> tuple:
    """Render first page of PDF at given DPI. Returns (image_bytes, width, height)."""
    doc = fitz.open(str(pdf_path))
    page = doc[0]
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    png_bytes = pix.tobytes("png")
    return png_bytes, pix.w, pix.h


def upscale_jpg(jpg_path: Path) -> tuple:
    """Load a JPG and save as PNG. Returns (png_bytes, width, height)."""
    import cv2
    img = cv2.imread(str(jpg_path))
    if img is None:
        print(f"ERROR: Could not read {jpg_path}")
        sys.exit(1)
    h, w = img.shape[:2]
    success, png_bytes = cv2.imencode(".png", img)
    return png_bytes.tobytes(), w, h


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if PDF_PATH.exists():
        print(f"Converting {PDF_PATH.name} at {DPI} DPI...")
        png_bytes, width, height = convert_pdf(PDF_PATH, DPI)
        source = PDF_PATH.name
    elif JPG_PATH.exists():
        print(f"PDF not found. Using existing image {JPG_PATH.name}...")
        png_bytes, width, height = upscale_jpg(JPG_PATH)
        source = JPG_PATH.name
    else:
        print(f"ERROR: No trail map found. Place PDF at {PDF_PATH}")
        print(f"       or JPG at {JPG_PATH}")
        sys.exit(1)

    OUTPUT_IMAGE.write_bytes(png_bytes)
    print(f"Saved {OUTPUT_IMAGE} ({width}x{height}, {len(png_bytes) / 1024 / 1024:.1f} MB)")

    meta = {"width": width, "height": height, "dpi": DPI, "source": source}
    OUTPUT_META.write_text(json.dumps(meta, indent=2))
    print(f"Saved metadata to {OUTPUT_META}")


if __name__ == "__main__":
    main()
