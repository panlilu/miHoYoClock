#!/usr/bin/env python3
"""Generate Bitcoin icon CLK file from Wikipedia image.

CLK format: "CK" magic (0x4B43), uint16 width (LE), uint16 height (LE), raw RGB565.
"""
import struct
import sys
import os
import urllib.request
import ssl

WIDTH = 135
HEIGHT = 240
BTC_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/330px-Bitcoin.svg.png"

try:
    from PIL import Image
except ImportError:
    print("Pillow not installed. Run: pip install Pillow")
    sys.exit(1)


def rgb888_to_rgb565(r, g, b):
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def download_image():
    """Download Bitcoin logo from Wikipedia."""
    print(f"Downloading: {BTC_URL}")
    req = urllib.request.Request(BTC_URL, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    return Image.open(resp).convert("RGBA")


def generate():
    try:
        logo = download_image()
    except Exception as e:
        print(f"Download failed: {e}")
        print("Falling back to generated icon...")
        logo = None

    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))

    if logo:
        # Resize logo to fit within tube, maintaining aspect ratio
        logo.thumbnail((WIDTH - 30, HEIGHT - 50), Image.LANCZOS)
        # Center on black background
        ox = (WIDTH - logo.width) // 2
        oy = (HEIGHT - logo.height) // 2
        # Composite with alpha
        img.paste(logo, (ox, oy), logo)
    else:
        # Fallback: draw simple "B" symbol
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        cx, cy = WIDTH // 2, HEIGHT // 2
        r = 50
        orange = (247, 147, 26)
        draw.ellipse([cx-r, cy-r-10, cx+r, cy+r-10], outline=orange, width=5)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 65)
        except Exception:
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), "B", font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        draw.text((cx-tw//2, cy-th//2-10), "B", fill=orange, font=font)

    # Convert to CLK format
    pixels = img.load()
    output = bytearray()
    output.extend(struct.pack("<H", 0x4B43))  # CK magic
    output.extend(struct.pack("<HH", WIDTH, HEIGHT))

    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = pixels[x, y]
            output.extend(struct.pack("<H", rgb888_to_rgb565(r, g, b)))

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ips", "btc")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "btc.bmp")
    with open(out_path, "wb") as f:
        f.write(output)

    # Also save a preview PNG for inspection
    preview_path = os.path.join(out_dir, "preview.png")
    img.save(preview_path)
    print(f"Generated {out_path} ({len(output)} bytes, {WIDTH}x{HEIGHT})")
    print(f"Preview:   {preview_path}")


if __name__ == "__main__":
    generate()
