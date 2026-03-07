#!/usr/bin/env python3
"""
Step 1: OCR exploration - understand what text Tesseract can find on the map,
and how the trail labels appear (font, size, rotation, color).

This script:
1. Runs full-image OCR to see what Tesseract picks up
2. Uses Tesseract's word-level bounding boxes to locate text
3. Tries different preprocessing (grayscale, binarize, invert)
4. Outputs a visualization showing detected text positions
"""

import cv2
import numpy as np
import pytesseract
from pytesseract import Output
import json

MAP_PATH = "public/killington-trail-map.jpg"


def ocr_full_image(img, preprocess="none"):
    """Run Tesseract on the full image with word-level bounding boxes."""
    if preprocess == "gray":
        processed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif preprocess == "thresh":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    elif preprocess == "invert":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.bitwise_not(gray)
    elif preprocess == "adaptive":
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 15, 5)
    else:
        processed = img

    data = pytesseract.image_to_data(processed, output_type=Output.DICT,
                                      config='--psm 11 --oem 3')
    return data


def find_trail_names_in_ocr(data, known_trail_names):
    """Search OCR results for known trail names."""
    matches = []
    n = len(data['text'])
    texts = data['text']

    # Build word position map
    words = []
    for i in range(n):
        text = texts[i].strip()
        if len(text) < 2:
            continue
        conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
        words.append({
            'text': text,
            'conf': conf,
            'x': data['left'][i],
            'y': data['top'][i],
            'w': data['width'][i],
            'h': data['height'][i],
            'idx': i,
        })

    # Try to match known trail names (single word or multi-word)
    for trail_name in known_trail_names:
        name_words = trail_name.lower().split()

        for i, word in enumerate(words):
            word_text = word['text'].lower().strip('.,;:!?()-')

            # Single word match
            if len(name_words) == 1 and word_text == name_words[0]:
                cx = word['x'] + word['w'] / 2
                cy = word['y'] + word['h'] / 2
                matches.append({
                    'trail_name': trail_name,
                    'detected_text': word['text'],
                    'conf': word['conf'],
                    'x': word['x'], 'y': word['y'],
                    'w': word['w'], 'h': word['h'],
                    'cx': cx, 'cy': cy,
                })

            # Multi-word: check consecutive words
            elif len(name_words) > 1 and word_text == name_words[0]:
                if i + len(name_words) - 1 < len(words):
                    all_match = True
                    for j, nw in enumerate(name_words[1:], 1):
                        next_word = words[i + j]['text'].lower().strip('.,;:!?()-')
                        if next_word != nw:
                            all_match = False
                            break

                    if all_match:
                        last = words[i + len(name_words) - 1]
                        x = word['x']
                        y = min(word['y'], last['y'])
                        w = (last['x'] + last['w']) - word['x']
                        h = max(word['y'] + word['h'], last['y'] + last['h']) - y
                        matches.append({
                            'trail_name': trail_name,
                            'detected_text': ' '.join(words[i+j]['text'] for j in range(len(name_words))),
                            'conf': min(words[i+j]['conf'] for j in range(len(name_words))),
                            'x': x, 'y': y, 'w': w, 'h': h,
                            'cx': x + w / 2, 'cy': y + h / 2,
                        })

    return matches


def main():
    img = cv2.imread(MAP_PATH)
    h, w = img.shape[:2]
    print(f"Image: {w}x{h}")

    # Known trail names from trails.ts
    import re
    with open("src/data/trails.ts", 'r') as f:
        content = f.read()

    trail_names = []
    pattern = r"name:\s*'([^']+)'"
    for match in re.finditer(pattern, content):
        name = match.group(1)
        trail_names.append(name)

    print(f"Known trail names: {len(trail_names)}")
    for name in trail_names[:10]:
        print(f"  - {name}")
    print(f"  ... and {len(trail_names) - 10} more")

    # Try different preprocessing methods
    methods = ["none", "gray", "adaptive"]

    all_detected_words = {}
    all_matches = {}

    for method in methods:
        print(f"\n{'='*60}")
        print(f"OCR with preprocessing: {method}")
        print(f"{'='*60}")

        data = ocr_full_image(img, method)
        n = len(data['text'])
        words_found = sum(1 for i in range(n) if len(data['text'][i].strip()) >= 2)
        print(f"  Total text items: {n}, words (len>=2): {words_found}")

        # Show all detected words with reasonable confidence
        good_words = []
        for i in range(n):
            text = data['text'][i].strip()
            conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
            if len(text) >= 3 and conf >= 30:
                good_words.append({
                    'text': text,
                    'conf': conf,
                    'x_pct': round(data['left'][i] / w * 100, 1),
                    'y_pct': round(data['top'][i] / h * 100, 1),
                })

        print(f"  Good words (len>=3, conf>=30): {len(good_words)}")
        for gw in good_words[:30]:
            print(f"    '{gw['text']}' conf={gw['conf']} at ({gw['x_pct']}%, {gw['y_pct']}%)")

        all_detected_words[method] = good_words

        # Search for trail name matches
        matches = find_trail_names_in_ocr(data, trail_names)
        all_matches[method] = matches

        if matches:
            print(f"\n  TRAIL NAME MATCHES ({len(matches)}):")
            for m in matches:
                x_pct = round(m['cx'] / w * 100, 1)
                y_pct = round(m['cy'] / h * 100, 1)
                print(f"    '{m['trail_name']}' detected='{m['detected_text']}' "
                      f"conf={m['conf']} at ({x_pct}%, {y_pct}%)")
        else:
            print(f"\n  No trail name matches found")

    # Visualize detected words on map
    print("\n\nGenerating visualization of detected text...")
    viz = img.copy()

    # Use the best method (try "none" first)
    best_method = "none"
    data = ocr_full_image(img, best_method)
    n = len(data['text'])

    for i in range(n):
        text = data['text'][i].strip()
        conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
        if len(text) >= 3 and conf >= 30:
            x = data['left'][i]
            y = data['top'][i]
            bw = data['width'][i]
            bh = data['height'][i]
            color = (0, 255, 0) if conf >= 60 else (0, 255, 255)
            cv2.rectangle(viz, (x, y), (x + bw, y + bh), color, 2)
            cv2.putText(viz, f"{text}", (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    small = cv2.resize(viz, (w // 2, h // 2))
    cv2.imwrite("tools/ocr_detected_text.jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 90])
    print("Saved to tools/ocr_detected_text.jpg")

    # Save all detected words as JSON for further analysis
    with open("tools/ocr_results.json", 'w') as f:
        json.dump({
            'known_trails': trail_names,
            'detected_words': all_detected_words,
            'trail_matches': {k: [{**m, 'cx': round(m['cx']/w*100, 1), 'cy': round(m['cy']/h*100, 1)}
                                   for m in v] for k, v in all_matches.items()},
        }, f, indent=2)
    print("Saved OCR results to tools/ocr_results.json")


if __name__ == "__main__":
    main()
