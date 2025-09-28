
"""
png_to_mc_pixelart.py
Convert an input image (PNG/JPG/...) into Minecraft pixel art by mapping pixels
to the nearest block color (16 concrete colors by default) and producing a
`.mcfunction` file containing /setblock commands.

Usage examples:
  python png_to_mc_pixelart.py input.png --width 64 --out pixelart.mcfunction --startx 100 --starty 64 --startz 100 --blocktype concrete --preview preview.png
"""

import argparse
from PIL import Image
import numpy as np
import math

# 16 concrete color palette (minecraft concrete) - approximate RGB triples
CONCRETE_PALETTE = {
    "white":        (209, 213, 214),
    "orange":       (240, 118, 19),
    "magenta":      (189, 68, 179),
    "light_blue":   (58, 175, 217),
    "yellow":       (249, 198, 39),
    "lime":         (112, 185, 25),
    "pink":         (237, 141, 172),
    "gray":         (62, 68, 71),
    "light_gray":   (142, 142, 134),
    "cyan":         (21, 137, 142),
    "purple":       (121, 42, 172),
    "blue":         (53, 57, 157),
    "brown":        (100, 58, 36),
    "green":        (73, 91, 36),
    "red":          (161, 39, 34),
    "black":        (20, 21, 25),
}

WOOL_PALETTE = {
    # alternate palette if you prefer wool - approximate values
    "white": (234,236,237), "orange": (241,118,20), "magenta": (238,77,201), "light_blue": (128,199,248),
    "yellow": (250,198,39), "lime": (112,185,25), "pink": (242,141,170), "gray": (57,57,57),
    "light_gray": (151,151,151), "cyan": (20,137,140), "purple": (107,50,168), "blue": (44,46,143),
    "brown": (96,59,31), "green": (73,91,36), "red": (176,46,38), "black": (12,12,12)
}

PALETTES = {
    "concrete": CONCRETE_PALETTE,
    "wool": WOOL_PALETTE,
}

def nearest_color(rgb, palette_arr):
    # rgb: (3,), palette_arr shape: (N,3)
    diffs = palette_arr - np.array(rgb, dtype=np.int16)
    dists = np.sum(diffs.astype(np.int32) ** 2, axis=1)
    idx = int(np.argmin(dists))
    return idx

def offset_token(offset):
    # Format offset for Minecraft relative coordinate: 0 -> "~", 5 -> "~5", -2 -> "~-2"
    if offset == 0:
        return "~"
    return "~" + str(offset)

def make_mcfunction(commands, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for cmd in commands:
            f.write(cmd + "\n")
    print(f"Saved {len(commands)} commands to {out_path}")

def build_setblock_cmd(xoff, y, zoff, block_fullname):
    return f"setblock {offset_token(xoff)} {y} {offset_token(zoff)} {block_fullname} replace"

def main():
    p = argparse.ArgumentParser(description="Convert PNG to Minecraft pixel art (.mcfunction).")
    p.add_argument("infile", help="Input image file (png/jpg/...)")
    p.add_argument("--width", "-W", type=int, default=64, help="Target pixel width in blocks (keeps aspect ratio)")
    p.add_argument(
        "--out", "-o",
        default=r"C:\Users\amiib\AppData\Roaming\.minecraft\saves\Pixel Art\datapacks\pixelartpack\data\pixelart\function\pixelart.mcfunction",
        help="Output .mcfunction file"
)

    p.add_argument("--startx", type=int, default=0, help="Relative start X offset (will use ~startx)")
    p.add_argument("--starty", type=int, default=64, help="Absolute or relative Y? We'll use absolute Y in the command.")
    p.add_argument("--startz", type=int, default=0, help="Relative start Z offset (will use ~startz)")
    p.add_argument("--blocktype", choices=list(PALETTES.keys()), default="concrete", help="Block family to use for mapping (concrete or wool)")
    p.add_argument("--flipy", action="store_true", help="Flip vertically so top of image becomes positive Z (useful for orientation)")
    p.add_argument("--preview", help="Save a preview PNG (shows mapped colors) e.g. preview.png")
    p.add_argument("--max-commands", type=int, default=100000, help="Abort if commands exceed this (safety)")
    args = p.parse_args()

    # Load image
    im = Image.open(args.infile).convert("RGBA")
    # Remove full transparency by replacing with white (or treat as transparent -> skip)
    bg = Image.new("RGBA", im.size, (255,255,255,255))
    im = Image.alpha_composite(bg, im).convert("RGB")

    # Resize preserving aspect ratio to target width
    w0, h0 = im.size
    target_w = args.width
    target_h = int(round((target_w * h0) / w0))
    im_small = im.resize((target_w, target_h), Image.LANCZOS)

    # Choose palette
    palette = PALETTES[args.blocktype]
    palette_names = list(palette.keys())
    palette_colors = np.array([palette[n] for n in palette_names], dtype=np.int16)

    pixels = np.array(im_small)  # shape (H, W, 3)
    H, W = pixels.shape[0], pixels.shape[1]

    # Map each pixel to nearest palette color
    mapped_idxs = np.zeros((H, W), dtype=np.int32)
    for y in range(H):
        # vectorized distance calc across palette
        row = pixels[y]
        # compute distances to each palette color for the whole row
        # shape row (W,3), palette_colors (N,3) -> expand to (W,N,3)
        # But easier loop by pixel (W small), or vectorize per row
        for x in range(W):
            rgb = row[x]
            mapped_idxs[y, x] = nearest_color(rgb, palette_colors)

    # Build commands place blocks in X (width) and Z (height) plane
    commands = []
    # iterate rows top-to-bottom. Minecraft orientation: pick mapping: x increases right, z increases forward
    # If user wants top-of-image mapped to negative z or positive z they can flip with --flipy
    for row_idx in range(H):
        y = args.starty
        if args.flipy:
            z_offset_row = row_idx
        else:
            z_offset_row = H - 1 - row_idx  # so top of image corresponds to positive z (common desire)
        for col_idx in range(W):
            palette_idx = int(mapped_idxs[row_idx, col_idx])
            block_color_name = palette_names[palette_idx]
            block_fullname = f"minecraft:{block_color_name}_{args.blocktype}"  # e.g. minecraft:white_concrete
            xoff = args.startx + col_idx
            zoff = args.startz + z_offset_row
            cmd = build_setblock_cmd(xoff, y, zoff, block_fullname)
            commands.append(cmd)

            if len(commands) > args.max_commands:
                raise SystemExit(f"Aborting: command count exceeded max-commands ({args.max_commands}).")

    make_mcfunction(commands, args.out)

    if args.preview:
        # Create a preview image using palette colors (each pixel becomes 1x1 block color)
        preview = Image.new("RGB", (W, H))
        for y in range(H):
            for x in range(W):
                color = tuple(palette_colors[int(mapped_idxs[y, x])].tolist())
                preview.putpixel((x, y), color)
        preview = preview.resize((W*8, H*8), Image.NEAREST)  # make it easier to see
        preview.save(args.preview)
        print(f"Saved preview: {args.preview}")

    print("Done. To use the .mcfunction file:")
    print("  - Place it in a datapack functions folder (e.g. datapacks/<pack>/data/<namespace>/functions/<name>.mcfunction)")
    print("  - Run in-game with: /function <namespace>:<name>")
    print("Or open the .mcfunction in a command block chain or paste into console (beware very large commands lists).")

if __name__ == "__main__":
    main()
