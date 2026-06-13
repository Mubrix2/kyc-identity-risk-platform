# scripts/generate_sample_id_images.py
"""
Generate fictional ID card images for OCR testing and dashboard demo.
Not real documents — text rendered via PIL, matches ocr_engine regex patterns.

Usage: python scripts/generate_sample_id_images.py
"""
# scripts/generate_sample_id_images.py
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = Path("data/sample_ids")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    {"filename": "clean_match.png",   "name": "ADEKUNLE OKAFOR",  "dob": "14/03/1990", "nin": "12345678901", "blur": False},
    {"filename": "mismatch_name.png", "name": "CHIOMA EZE",       "dob": "22/07/1988", "nin": "98765432109", "blur": False},
    {"filename": "low_quality.png",   "name": "IBRAHIM MOHAMMED", "dob": "05/11/1995", "nin": "55566677788", "blur": True},
]


def _load_font(size: int):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()  # last resort — may reduce OCR accuracy


def render_id_card(name, dob, nin, blur=False) -> Image.Image:
    # Larger canvas + larger font — Tesseract needs reasonable pixel
    # height per character (~30px+) to read punctuation reliably.
    img = Image.new("RGB", (1000, 600), color="white")
    draw = ImageDraw.Draw(img)

    title_font = _load_font(28)
    label_font = _load_font(32)

    draw.rectangle([15, 15, 985, 585], outline="black", width=3)
    draw.text((50, 50),  "FEDERAL REPUBLIC OF NIGERIA", fill="black", font=title_font)
    draw.text((50, 100), "NATIONAL IDENTITY CARD",      fill="black", font=title_font)
    draw.text((50, 220), f"NAME: {name}", fill="black", font=label_font)
    draw.text((50, 300), f"DOB: {dob}",   fill="black", font=label_font)
    draw.text((50, 380), f"NIN: {nin}",   fill="black", font=label_font)

    return img.filter(ImageFilter.GaussianBlur(radius=2)) if blur else img


if __name__ == "__main__":
    for s in SAMPLES:
        path = OUTPUT_DIR / s["filename"]
        render_id_card(s["name"], s["dob"], s["nin"], s["blur"]).save(path)
        print(f"✅ {path}")