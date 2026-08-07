"""YouTube cookies helper.

Usage:
  python scripts/rotate_cookies.py --from chrome
  python scripts/rotate_cookies.py --file path/to/exported.txt

The script always writes the output to aura-backend/youtube_cookies.txt
(overwriting any previous file) and verifies the file with `yt-dlp`.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "aura-backend"
DEST = BACKEND / "youtube_cookies.txt"


def export_from_browser(browser: str) -> Path:
    """Use the yt-dlp CLI's --cookies-from-browser to dump cookies to a temp file."""
    tmp = BACKEND / "temp" / f"cookies_{browser}.txt"
    tmp.parent.mkdir(exist_ok=True, parents=True)
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--cookies-from-browser", browser,
        "--no-warnings",
        "--skip-download",
        "--print", "id",  # just need to trigger the cookie export
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"yt-dlp failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    # yt-dlp actually writes to the path passed in --cookies, not --cookies-from-browser.
    # So we re-run with --cookies pointing at our tmp file.
    cmd2 = [
        sys.executable, "-m", "yt_dlp",
        "--cookies-from-browser", browser,
        "--cookies", str(tmp),
        "--no-warnings",
        "--skip-download",
        "--print", "id",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    result = subprocess.run(cmd2, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"yt-dlp failed to dump cookies:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    if not tmp.exists() or tmp.stat().st_size < 50:
        print(f"Cookie file looks empty: {tmp}", file=sys.stderr)
        sys.exit(1)
    return tmp


def import_file(src: Path) -> Path:
    """Copy a manually exported cookies.txt into place."""
    if not src.exists():
        print(f"Source file not found: {src}", file=sys.stderr)
        sys.exit(1)
    tmp = BACKEND / "temp" / f"cookies_imported_{src.name}"
    tmp.parent.mkdir(exist_ok=True, parents=True)
    shutil.copy2(src, tmp)
    return tmp


def validate_cookies(cookies_file: Path) -> None:
    """Run yt-dlp in dry-run mode to make sure the cookies actually work."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--cookies", str(cookies_file),
        "--no-warnings",
        "--skip-download",
        "--print", "%(title)s",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0 or not result.stdout.strip():
        print(f"Validation FAILED. yt-dlp output:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"✓ Cookies valid. Test lookup returned: {result.stdout.strip()!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rotate Aura's YouTube cookies.txt")
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--from", dest="browser", help="Browser to extract from (chrome, firefox, edge, …)")
    src.add_argument("--file", type=Path, help="Path to an existing cookies.txt")
    args = parser.parse_args()

    if args.browser:
        new = export_from_browser(args.browser)
    else:
        new = import_file(args.file)

    validate_cookies(new)
    shutil.copy2(new, DEST)
    print(f"✓ Wrote {DEST} ({DEST.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
