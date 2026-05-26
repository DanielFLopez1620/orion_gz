#!/usr/bin/env python3
"""
Generate PNG emotion textures from orion_interaction_micro_ros's emotions.hpp.

Usage:
    gen_emotion_textures.py <path/to/emotions.hpp> <output_dir>

Output:
    emotion_0.png  (angry)    emotion_1.png  (disgust)
    emotion_2.png  (fear)     emotion_3.png  (happy)
    emotion_4.png  (neutral)  emotion_5.png  (sad)
    emotion_6.png  (surprise) emotion_7.png  (wink)

Index order matches emotion_color[] / epd_bitmap_allArray[] in emotions.hpp.

Bitmap format: 176x220 px, row-major, 22 bytes/row, MSB = leftmost pixel.
  bit=1 → emotion color (from emotion_color[i], RGB565)
  bit=0 → black background
"""

import re
import os
import sys

from PIL import Image

# Order matches epd_bitmap_allArray and emotion_color in emotions.hpp
EMOTION_NAMES = [
    'angry', 'disgust', 'fear', 'happy',
    'neutral', 'sad', 'surprise', 'wink',
]

BITMAP_WIDTH  = 176
BITMAP_HEIGHT = 220
BYTES_PER_ROW = BITMAP_WIDTH // 8  # 22


def rgb565_to_rgb8(color565: int):
    r = ((color565 >> 11) & 0x1F) * 255 // 31
    g = ((color565 >> 5)  & 0x3F) * 255 // 63
    b = ( color565        & 0x1F) * 255 // 31
    return (r, g, b)


def parse_emotions_hpp(filepath: str):
    with open(filepath, 'r') as f:
        content = f.read()

    # ── emotion_color[8] ──────────────────────────────────────────────────────
    m = re.search(r'emotion_color\s*\[8\]\s*=\s*\{([^}]+)\}', content)
    if not m:
        raise ValueError("Could not find emotion_color[8] in emotions.hpp")
    colors = [int(t, 16) for t in re.findall(r'0x[0-9A-Fa-f]+', m.group(1))]
    if len(colors) != 8:
        raise ValueError(f"Expected 8 emotion colors, found {len(colors)}")

    # ── bitmap arrays ─────────────────────────────────────────────────────────
    bitmaps = {}
    for name in EMOTION_NAMES:
        pat = rf"epd_bitmap_{name}\s*\[\]\s*PROGMEM\s*=\s*\{{([^}}]+)\}}"
        m = re.search(pat, content, re.DOTALL)
        if not m:
            raise ValueError(f"Could not find epd_bitmap_{name} in emotions.hpp")
        data = [int(t, 16) for t in re.findall(r'0x[0-9A-Fa-f]{2}', m.group(1))]
        expected = BYTES_PER_ROW * BITMAP_HEIGHT  # 4840
        if len(data) < expected:
            raise ValueError(
                f"epd_bitmap_{name}: expected >= {expected} bytes, got {len(data)}"
            )
        bitmaps[name] = data

    return bitmaps, colors


def render_png(bitmap_bytes, color565: int, out_path: str, rotate_landscape: bool = True):
    """Render a 1-bit bitmap to a colour PNG file.

    If rotate_landscape is True the image is rotated 90° counter-clockwise so
    that the portrait bitmap (176×220) becomes landscape (220×176), matching
    the physical robot screen orientation when displayed in Gazebo.
    """
    img = Image.new('RGBA', (BITMAP_WIDTH, BITMAP_HEIGHT), (0, 0, 0, 255))
    pixels = img.load()
    fg = rgb565_to_rgb8(color565) + (255,)

    for y in range(BITMAP_HEIGHT):
        for x in range(BITMAP_WIDTH):
            byte_idx   = y * BYTES_PER_ROW + x // 8
            bit_offset = 7 - (x % 8)          # MSB = leftmost pixel
            if bitmap_bytes[byte_idx] & (1 << bit_offset):
                pixels[x, y] = fg
            # else leave (0,0,0,255) — black background

    if rotate_landscape:
        img = img.rotate(90, expand=True)    # portrait 176×220 → landscape 220×176

    img.save(out_path)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    hpp_path = sys.argv[1]
    out_dir  = sys.argv[2]

    os.makedirs(out_dir, exist_ok=True)

    print(f"Parsing {hpp_path} ...")
    bitmaps, colors = parse_emotions_hpp(hpp_path)

    for i, name in enumerate(EMOTION_NAMES):
        out_path = os.path.join(out_dir, f"emotion_{i}.png")
        render_png(bitmaps[name], colors[i], out_path, rotate_landscape=True)
        r, g, b = [int(c) for c in (
            ((colors[i] >> 11) & 0x1F) * 255 // 31,
            ((colors[i] >> 5)  & 0x3F) * 255 // 63,
            ( colors[i]        & 0x1F) * 255 // 31,
        )]
        print(f"  emotion_{i}.png  ({name:8s})  RGB=({r:3d},{g:3d},{b:3d})")

    print(f"Done — {len(EMOTION_NAMES)} textures in '{out_dir}/'")


if __name__ == '__main__':
    main()
