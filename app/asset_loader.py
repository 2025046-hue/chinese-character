from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
FONT_DIR = ASSETS_DIR / "fonts"
CHAR_DIR = ASSETS_DIR / "characters"
FONT_DIR.mkdir(parents=True, exist_ok=True)
CHAR_DIR.mkdir(parents=True, exist_ok=True)


FONT_CANDIDATES = [
    "NotoSansSC-Regular.otf",
    "NotoSerifSC-Regular.otf",
    "NotoSansTC-Regular.otf",
    "NotoSansHK-Regular.otf",
    "NotoSansCJK-Regular.ttc",
    "SimHei.ttf",
    "SimSun.ttf",
]


def _char_filename(char: str) -> Path:
    code = f"u{ord(char):04x}"
    return CHAR_DIR / f"{code}.png"


def _select_font(size: int) -> ImageFont.FreeTypeFont:
    for name in FONT_CANDIDATES:
        path = FONT_DIR / name
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size)
            except Exception as e:
                print(f"[FONT] Failed to load {name}: {e}")

    raise RuntimeError(
        "No valid Chinese font found. "
        "Ensure fonts exist in assets/fonts/"
    )


def make_overlay_image(
    character: str,
    size: int = 400,
    font_size: int = 240
) -> Image.Image:

    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = _select_font(font_size)
    bbox = draw.textbbox((0, 0), character, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) / 2 - bbox[0]
    y = (size - h) / 2 - bbox[1]

    draw.text(
        (x, y),
        character,
        font=font,
        fill=(50, 50, 50, 120),
        stroke_width=2,
        stroke_fill=(30, 30, 30, 160)
    )

    img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    img = ImageEnhance.Brightness(img).enhance(0.9)

    return img


def get_overlay_photoimage(_, character: str, size: int = 400) -> Image.Image:
    path = _char_filename(character)

    if path.exists():
        try:
            img = Image.open(path).convert("RGBA")
            if img.size != (size, size):
                img = img.resize((size, size), Image.LANCZOS)
            return img
        except Exception as e:
            print("[IMG] Cache load failed:", e)

    img = make_overlay_image(
        character,
        size=size,
        font_size=int(size * 0.6),
    )

    try:
        img.save(path)
    except Exception as e:
        print("[IMG] Cache save failed:", e)

    return img
