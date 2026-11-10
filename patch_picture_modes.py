#!/usr/bin/env python3
"""
patch_picture_modes.py
Calibrates and optimizes picture mode presets across all input sources (Media, HDMI, ATV, AV)
for TP.SK508.PB801 / HiSilicon Hi3751V350 combo boards.

Fixes:
- Unlocks Backlight, Noise Reduction, and Color Temperature switching in Picture Modes.
- Normalizes blown-out Contrast (was 100/100, crushing highlights).
- Tames neon oversaturation in Dynamic/Vivid modes (was 70/100).
- Eliminates artificial edge-ringing halos (Sharpness reduced from 60 to natural 45-50).
- Optimizes Backlight distribution:
    * Standard: 90% (Comfortable everyday viewing)
    * Dynamic: 100% (High ambient light)
    * Soft / Movie: 75% (Dark room cinema viewing with warm filmic D65 color temp)
    * User: 90% (Full manual control unlocked)
"""

import sys
import re

def patch_cfg(cfg_path):
    with open(cfg_path, 'r', encoding='latin-1') as f:
        cfg = f.read()

    cfg = cfg.replace('ConfigBacklight = N', 'ConfigBacklight = Y;')
    cfg = cfg.replace('BacklightEnable = 0;', 'BacklightEnable = 1;')
    cfg = cfg.replace('NrEnable = 0;', 'NrEnable = 1;')
    cfg = cfg.replace('ColorTempEnable = 0;', 'ColorTempEnable = 1;')

    with open(cfg_path, 'w', encoding='latin-1') as f:
        f.write(cfg)
    print(f"[OK] Patched {cfg_path}")

def patch_db(db_path):
    with open(db_path, 'r', encoding='latin-1') as f:
        db = f.read()

    # Format: Brightness, Contrast, Color, Sharpness, Tint, Backlight, NR, ColorTemp
    db = re.sub(r'PicImage_([a-zA-Z0-9]+)_standard\s*=\s*[^;]+;', r'PicImage_\1_standard = 50, 84, 50, 50, 50, 90, 2, 0;', db)
    db = re.sub(r'PicImage_([a-zA-Z0-9]+)_dynamic\s*=\s*[^;]+;',  r'PicImage_\1_dynamic = 50, 88, 56, 50, 50, 100, 2, 1;', db)
    db = re.sub(r'PicImage_([a-zA-Z0-9]+)_softness\s*=\s*[^;]+;', r'PicImage_\1_softness = 50, 80, 50, 45, 50, 75, 2, 2;', db)
    db = re.sub(r'PicImage_([a-zA-Z0-9]+)_user\s*=\s*[^;]+;',     r'PicImage_\1_user = 50, 84, 50, 50, 50, 90, 2, 0;', db)
    db = re.sub(r'PicImage_([a-zA-Z0-9]+)_vivid\s*=\s*[^;]+;',    r'PicImage_\1_vivid = 50, 88, 56, 50, 50, 95, 2, 1;', db)

    with open(db_path, 'w', encoding='latin-1') as f:
        f.write(db)
    print(f"[OK] Patched {db_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: patch_picture_modes.py <cfg.ini> <db.ini>")
        sys.exit(1)
    patch_cfg(sys.argv[1])
    patch_db(sys.argv[2])

