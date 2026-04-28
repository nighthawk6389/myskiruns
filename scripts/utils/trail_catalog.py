"""Canonical trail catalog for the Killington map.

Single source of truth for: which trails exist on the map, how they are
grouped into peak regions (with pixel-percentage bounds for cropping), and how
trail-difficulty maps to the extracted polyline color.

Imported by:
- scripts/04_identify_trails.py    (LLM-based naming)
- scripts/02b_extract_text.py      (OCR-based naming)
- scripts/utils/ocr_match.py       (OCR -> trail-name fuzzy matching)
"""

# Map difficulty to expected extracted polyline color
DIFFICULTY_TO_COLOR = {
    "green": "green",
    "blue": "blue",
    "black": "black",
    "double-black": "magenta",
}

# BGR colors used to draw trails in overlays / annotated patches
COLOR_MAP_BGR = {
    "green": (0, 200, 0),
    "blue": (255, 80, 0),
    "magenta": (255, 0, 255),
    "black": (100, 100, 100),
}

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


def all_trails() -> list[dict]:
    """Flatten the catalog: returns every trail with peak_id added.

    Useful for OCR fuzzy matching where peak context is unknown up front.
    """
    out = []
    for peak_id, peak_data in TRAILS_BY_PEAK.items():
        for trail in peak_data["trails"]:
            entry = dict(trail)
            entry["peak_id"] = peak_id
            out.append(entry)
    return out
