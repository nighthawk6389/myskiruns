#!/usr/bin/env python3
"""Debug script: draw trail hotspot positions on the trail map image."""

from PIL import Image, ImageDraw, ImageFont
import math

# Peak regions (percentage-based) from ImageMap.tsx
PEAK_REGIONS = {
    'snowshed':        {'cx': 8,  'cy': 55, 'w': 10, 'h': 40},
    'sunrise':         {'cx': 18, 'cy': 50, 'w': 10, 'h': 40},
    'ramshead':        {'cx': 30, 'cy': 40, 'w': 12, 'h': 45},
    'snowdon':         {'cx': 44, 'cy': 35, 'w': 14, 'h': 50},
    'skye-peak':       {'cx': 62, 'cy': 28, 'w': 16, 'h': 55},
    'killington-peak': {'cx': 78, 'cy': 20, 'w': 16, 'h': 60},
    'bear-mountain':   {'cx': 92, 'cy': 32, 'w': 12, 'h': 50},
}

# All trails from trails.ts
TRAILS = [
    # SNOWSHED
    ('snowshed-slope', 'Snowshed', 'snowshed'),
    ('yodeler', 'Yodeler', 'snowshed'),
    ('idler', 'Idler', 'snowshed'),
    ('snow-play', 'Snow Play', 'snowshed'),
    ('snowshed-crossover', 'Crossover', 'snowshed'),
    # SUNRISE
    ('sun-dog', 'Sun Dog', 'sunrise'),
    ('rendezvous', 'Rendezvous', 'sunrise'),
    ('bear-cub', 'Bear Cub', 'sunrise'),
    ('bear-view', 'Bear View', 'sunrise'),
    ('sunrise-connector', 'Sunrise Connector', 'sunrise'),
    # RAMSHEAD
    ('easy-street', 'Easy Street', 'ramshead'),
    ('swirl', 'Swirl', 'ramshead'),
    ('treezy', 'Treezy', 'ramshead'),
    ('squeeze-play', 'Squeeze Play', 'ramshead'),
    ('ramshead-run', 'Ramshead Run', 'ramshead'),
    ('ramshead-liftline', 'Ramshead Liftline', 'ramshead'),
    ('header', 'Header', 'ramshead'),
    ('vagabond', 'Vagabond', 'ramshead'),
    ('caper', 'Caper', 'ramshead'),
    ('timberline', 'Timberline', 'ramshead'),
    ('start-park', 'Start Park', 'ramshead'),
    # SNOWDON
    ('great-northern', 'Great Northern', 'snowdon'),
    ('bunny-buster', 'Bunny Buster', 'snowdon'),
    ('chute', 'Chute', 'snowdon'),
    ('conclusion', 'Conclusion', 'snowdon'),
    ('upper-fis', 'Upper FIS', 'snowdon'),
    ('mountain-run', 'Mountain Run', 'snowdon'),
    ('mountain-training', 'Mtn Training Station', 'snowdon'),
    ('snowdon-liftline', 'Snowdon Liftline', 'snowdon'),
    ('upper-snowdon', 'Upper Snowdon', 'snowdon'),
    ('lower-snowdon', 'Lower Snowdon', 'snowdon'),
    ('bittersweet', 'Bittersweet', 'snowdon'),
    ('sass', 'Sass', 'snowdon'),
    ('northstar', 'Northstar', 'snowdon'),
    ('royal-flush', 'Royal Flush', 'snowdon'),
    ('upper-northbrook', 'Upper Northbrook', 'snowdon'),
    ('lower-northbrook', 'Lower Northbrook', 'snowdon'),
    ('snowdon-glades', 'Snowdon Glades', 'snowdon'),
    # SKYE PEAK
    ('skyelark', 'Skyelark', 'skye-peak'),
    ('upper-skyelark', 'Upper Skyelark', 'skye-peak'),
    ('skyeburst', 'Skyeburst', 'skye-peak'),
    ('upper-skyeburst', 'Upper Skyeburst', 'skye-peak'),
    ('skye-hawk', 'Skye Hawk', 'skye-peak'),
    ('skyebits', 'Skyebits', 'skye-peak'),
    ('cruise-control', 'Cruise Control', 'skye-peak'),
    ('mouse-trap', 'Mouse Trap', 'skye-peak'),
    ('somewhere', 'Somewhere', 'skye-peak'),
    ('breakaway', 'Breakaway', 'skye-peak'),
    ('touch-down', 'Touch Down', 'skye-peak'),
    ('patsys', "Patsy's", 'skye-peak'),
    ('twister', 'Twister', 'skye-peak'),
    ('catwalk', 'Catwalk', 'skye-peak'),
    ('upper-catwalk', 'Upper Catwalk', 'skye-peak'),
    ('great-eastern', 'Great Eastern', 'skye-peak'),
    ('home-stretch', 'Home Stretch', 'skye-peak'),
    ('lower-home-stretch', 'Lower Home Stretch', 'skye-peak'),
    ('juggernaut', 'Juggernaut', 'skye-peak'),
    ('vertigo', 'Vertigo', 'skye-peak'),
    ('upper-vertigo', 'Upper Vertigo', 'skye-peak'),
    ('ovation', 'Ovation', 'skye-peak'),
    ('needles-eye', "Needle's Eye", 'skye-peak'),
    ('panic-button', 'Panic Button', 'skye-peak'),
    ('dream-maker', 'Dream Maker', 'skye-peak'),
    ('dream-maker-headwall', 'Dream Maker Headwall', 'skye-peak'),
    ('highline', 'Highline', 'skye-peak'),
    ('pipe-dream', 'Pipe Dream', 'skye-peak'),
    ('valley-plunge', 'Valley Plunge', 'skye-peak'),
    ('field-goal', 'Field Goal', 'skye-peak'),
    ('roundabout', 'Roundabout', 'skye-peak'),
    ('roundabout-glade', 'Roundabout Glade', 'skye-peak'),
    ('tin-man', 'Tin Man', 'skye-peak'),
    ('skye-peak-liftline', 'Skye Peak Liftline', 'skye-peak'),
    ('great-bear', 'Great Bear', 'skye-peak'),
    ('upper-great-bear', 'Upper Great Bear', 'skye-peak'),
    ('woodward-peace-park', 'Woodward Peace Park', 'skye-peak'),
    # KILLINGTON PEAK
    ('superstar', 'Superstar', 'killington-peak'),
    ('cascade', 'Cascade', 'killington-peak'),
    ('downdraft', 'Downdraft', 'killington-peak'),
    ('double-dipper', 'Double Dipper', 'killington-peak'),
    ('big-dipper-glade', 'Big Dipper Glade', 'killington-peak'),
    ('flume', 'Flume', 'killington-peak'),
    ('escapade', 'Escapade', 'killington-peak'),
    ('east-fall', 'East Fall', 'killington-peak'),
    ('upper-east-fall', 'Upper East Fall', 'killington-peak'),
    ('rime', 'Rime', 'killington-peak'),
    ('reason', 'Reason', 'killington-peak'),
    ('julio', 'Julio', 'killington-peak'),
    ('high-road', 'High Road', 'killington-peak'),
    ('north-way', 'North Way', 'killington-peak'),
    ('great-eastern-kp', 'Great Eastern (K.P.)', 'killington-peak'),
    ('fis', 'FIS', 'killington-peak'),
    ('lower-fis', 'Lower FIS', 'killington-peak'),
    ('solitude', 'Solitude', 'killington-peak'),
    ('k1-gondola-run', 'K-1 Gondola Run', 'killington-peak'),
    ('anarchy', 'Anarchy', 'killington-peak'),
    ('upper-canyon', 'Upper Canyon', 'killington-peak'),
    ('lower-canyon', 'Lower Canyon', 'killington-peak'),
    ('old-superstar', 'Old Superstar', 'killington-peak'),
    ('killington-liftline', 'Killington Liftline', 'killington-peak'),
    ('superstar-glade', 'Superstar Glade', 'killington-peak'),
    ('header-kp', 'Header', 'killington-peak'),
    ('mouse-run', 'Mouse Run', 'killington-peak'),
    ('low-road', 'Low Road', 'killington-peak'),
    ('the-mall', 'The Mall', 'killington-peak'),
    # BEAR MOUNTAIN
    ('outer-limits', 'Outer Limits', 'bear-mountain'),
    ('devils-fiddle', "Devil's Fiddle", 'bear-mountain'),
    ('wildfire', 'Wildfire', 'bear-mountain'),
    ('bear-claw', 'Bear Claw', 'bear-mountain'),
    ('growler', 'Growler', 'bear-mountain'),
    ('centerpiece', 'Centerpiece', 'bear-mountain'),
    ('spacewalk', 'Spacewalk', 'bear-mountain'),
    ('bear-trax', 'Bear Trax', 'bear-mountain'),
    ('falls-brook', 'Falls Brook', 'bear-mountain'),
    ('skye-burst-bear', 'Skyeburst', 'bear-mountain'),
    ('bear-mountain-liftline', 'Bear Mtn Liftline', 'bear-mountain'),
    ('the-stash', 'The Stash', 'bear-mountain'),
    ('lil-stash', "Lil' Stash", 'bear-mountain'),
    ('lower-wildfire', 'Lower Wildfire', 'bear-mountain'),
    ('bear-run', 'Bear Run', 'bear-mountain'),
]


def seeded_random(seed):
    s = seed
    def next_val():
        nonlocal s
        s = (s * 16807 + 0) % 2147483647
        return (s - 1) / 2147483646
    return next_val


def hash_string(s):
    h = 0
    for ch in s:
        h = ((h << 5) - h + ord(ch)) & 0xFFFFFFFF
        # Convert to signed 32-bit
        if h >= 0x80000000:
            h -= 0x100000000
        h = h & 0xFFFFFFFF
    # abs
    if h >= 0x80000000:
        return 0x100000000 - h
    return h


def generate_hotspot_positions():
    positions = {}
    # Group trails by peak
    peak_trails = {}
    for tid, tname, tpeak in TRAILS:
        peak_trails.setdefault(tpeak, []).append((tid, tname))

    for peak_id, trail_list in peak_trails.items():
        region = PEAK_REGIONS.get(peak_id)
        if not region:
            continue
        for index, (tid, tname) in enumerate(trail_list):
            rng = seeded_random(hash_string(tid))
            cols = math.ceil(math.sqrt(len(trail_list)))
            row = index // cols
            col = index % cols
            rows = math.ceil(len(trail_list) / cols)

            x = region['cx'] - region['w'] / 2 + (col / max(cols - 1, 1)) * region['w'] + (rng() - 0.5) * 2
            y = region['cy'] - region['h'] / 2 + (row / max(rows - 1, 1)) * region['h'] + (rng() - 0.5) * 2

            x = max(2, min(98, x))
            y = max(5, min(95, y))
            positions[tid] = (x, y, tname)

    return positions


def main():
    img = Image.open('/home/user/myskiruns/public/killington-trail-map.jpg')
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Try to get a small font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception:
        font = ImageFont.load_default()

    positions = generate_hotspot_positions()

    # Color by peak for visual grouping
    peak_colors = {
        'snowshed': (255, 255, 0),       # yellow
        'sunrise': (255, 165, 0),         # orange
        'ramshead': (0, 255, 0),          # green
        'snowdon': (0, 200, 255),         # cyan
        'skye-peak': (255, 100, 100),     # red/pink
        'killington-peak': (255, 0, 255), # magenta
        'bear-mountain': (255, 255, 255), # white
    }

    for tid, tname, tpeak in TRAILS:
        if tid not in positions:
            continue
        px, py, name = positions[tid]
        # Convert percentage to pixel
        ix = int(px / 100 * w)
        iy = int(py / 100 * h)

        color = peak_colors.get(tpeak, (255, 255, 255))

        # Draw dot (radius 4)
        r = 4
        draw.ellipse([ix - r, iy - r, ix + r, iy + r], fill=color, outline=(0, 0, 0))

        # Draw name with dark outline for readability
        tx, ty = ix + 6, iy - 7
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    draw.text((tx + dx, ty + dy), name, fill=(0, 0, 0), font=font)
        draw.text((tx, ty), name, fill=color, font=font)

    # Draw peak region rectangles for reference
    for peak_id, region in PEAK_REGIONS.items():
        cx, cy, rw, rh = region['cx'], region['cy'], region['w'], region['h']
        x1 = int((cx - rw / 2) / 100 * w)
        y1 = int((cy - rh / 2) / 100 * h)
        x2 = int((cx + rw / 2) / 100 * w)
        y2 = int((cy + rh / 2) / 100 * h)
        color = peak_colors.get(peak_id, (255, 255, 255))
        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
        # Label the region
        draw.text((x1 + 4, y1 + 4), peak_id, fill=color, font=font)

    out_path = '/home/user/myskiruns/debug_trail_overlay.jpg'
    img.save(out_path, quality=95)
    print(f"Saved to {out_path} ({w}x{h})")


if __name__ == '__main__':
    main()
