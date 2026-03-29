#!/usr/bin/env python3
"""Step 1: Convert trail map PDF to high-resolution PNG."""

import json
import sys
from pathlib import Path

import fitz  # PyMuPDF

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PDF_PATH = PROJECT_ROOT / "TrailMapForWeb-compressed.pdf"
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


def main():
    if not PDF_PATH.exists():
        print(f"ERROR: PDF not found at {PDF_PATH}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Converting {PDF_PATH.name} at {DPI} DPI...")
    png_bytes, width, height = convert_pdf(PDF_PATH, DPI)

    OUTPUT_IMAGE.write_bytes(png_bytes)
    print(f"Saved {OUTPUT_IMAGE} ({width}x{height}, {len(png_bytes) / 1024 / 1024:.1f} MB)")

    meta = {"width": width, "height": height, "dpi": DPI, "source": PDF_PATH.name}
    OUTPUT_META.write_text(json.dumps(meta, indent=2))
    print(f"Saved metadata to {OUTPUT_META}")


if __name__ == "__main__":
    main()
