"""Generate an optimized favicon from aura-logo.png.

Outputs:
  - public/favicon.ico  (multi-size: 16, 32, 48)
  - public/favicon.png  (32x32 PNG, used by index.html as <link rel="icon">)

The original aura-logo.png is preserved for the in-app header logo
which needs higher resolution.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
SRC = PUBLIC / "aura-logo.png"
ICO = PUBLIC / "favicon.ico"
PNG = PUBLIC / "favicon.png"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Source image not found: {SRC}")

    img = Image.open(SRC).convert("RGBA")
    sizes = [16, 32, 48]
    base = Image.new("RGBA", (max(sizes), max(sizes)), (0, 0, 0, 0))
    thumb = img.copy()
    thumb.thumbnail((max(sizes), max(sizes)), Image.LANCZOS)
    offset = ((max(sizes) - thumb.width) // 2, (max(sizes) - thumb.height) // 2)
    base.paste(thumb, offset, thumb)

    ico_frames = [base.resize((s, s), Image.LANCZOS) for s in sizes]
    ico_frames[0].save(ICO, format="ICO", sizes=[(s, s) for s in sizes], append_images=ico_frames[1:])
    print(f"Wrote {ICO} ({ICO.stat().st_size} bytes)")

    base.resize((32, 32), Image.LANCZOS).save(PNG, format="PNG", optimize=True)
    print(f"Wrote {PNG} ({PNG.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
