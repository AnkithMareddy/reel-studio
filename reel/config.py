"""Settings, all from environment variables (see .env.example)."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

STUDIO_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = Path(os.environ.get("STUDIO_DATA", STUDIO_DIR / "data")).resolve()


def _default_trips_dir() -> Path:
    """Where to look for trip itineraries when TRIPS_DIR is not set.

    The studio used to live inside the tagalong repo as `studio/`, so the default was
    `../trips` — the bot's own trip folder. As a standalone repo that path points outside
    the checkout entirely, so `./trips` is the default now.

    The sibling layout is still honoured when it is actually there, because running this
    next to a tagalong clone is a genuinely useful setup: the studio then titles each
    day's edit from the real plan and knows where every shot was filmed.
    """
    here = STUDIO_DIR / "trips"
    if here.is_dir():
        return here
    sibling = STUDIO_DIR.parent / "tagalong" / "trips"
    if sibling.is_dir():
        return sibling
    legacy = STUDIO_DIR.parent / "trips"   # the old in-repo layout
    if legacy.is_dir():
        return legacy
    return here


TRIPS_DIR = Path(os.environ.get("TRIPS_DIR") or _default_trips_dir()).resolve()
TIMEZONE = os.environ.get("STUDIO_TZ", "Europe/Dublin")  # Dublin and London share the same offset

PASSWORD = os.environ.get("STUDIO_PASSWORD", "")
SECRET = os.environ.get("STUDIO_SECRET", "") or (PASSWORD + "::reel-studio")

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = os.environ.get("STUDIO_MODEL", "claude-opus-5-5")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
PUBLIC_URL = os.environ.get("PUBLIC_URL", "") or (
    f"https://{os.environ['RAILWAY_PUBLIC_DOMAIN']}" if os.environ.get("RAILWAY_PUBLIC_DOMAIN") else ""
)

# Keep the original camera files after they've been cut into shots? Off by default:
# originals are huge and the shots keep everything the editor needs.
KEEP_ORIGINALS = os.environ.get("KEEP_ORIGINALS", "0") == "1"
# Long side of the stored shots. 2560 leaves room to crop 9:16 out of 16:9 footage sharply.
MEZZ_LONG_SIDE = int(os.environ.get("MEZZ_LONG_SIDE", "2560"))
MEZZ_CRF = int(os.environ.get("MEZZ_CRF", "20"))
THREADS = int(os.environ.get("FFMPEG_THREADS", "0"))  # 0 = ffmpeg decides
PRESET = os.environ.get("X264_PRESET", "medium")
# Hardware video decoding (Apple Silicon/Intel Macs): much faster analysis of 4K HEVC.
HWACCEL = os.environ.get("HWACCEL", "videotoolbox" if __import__("sys").platform == "darwin" else "")


def _font(env, *candidates):
    if os.environ.get(env):
        return os.environ[env]
    for c in candidates:
        p = Path(c)
        if p.exists():
            return str(p)
    found = shutil.which("fc-match")
    if found:
        import subprocess

        name = candidates[-1] if not str(candidates[-1]).startswith("/") else "DejaVu Sans"
        out = subprocess.run(["fc-match", "-f", "%{file}", name], capture_output=True, text=True)
        if out.stdout:
            return out.stdout
    return ""


FONTS_DIR = STUDIO_DIR / "fonts"
FONT_SERIF = _font(
    "FONT_SERIF",
    FONTS_DIR / "PlayfairDisplay.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif",
)
FONT_SANS = _font(
    "FONT_SANS",
    FONTS_DIR / "Montserrat.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans:bold",
)
FONT_MONO = _font(
    "FONT_MONO",
    FONTS_DIR / "SpaceMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "monospace",
)

FONT_VCR = _font(
    "FONT_VCR",
    FONTS_DIR / "VT323.ttf",
    FONTS_DIR / "SpaceMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "monospace",
)


def path(*parts) -> Path:
    p = DATA_DIR.joinpath(*parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def rel(p: str | os.PathLike) -> str:
    """Store paths relative to DATA_DIR so the volume can be remounted elsewhere."""
    return str(Path(p).resolve().relative_to(DATA_DIR))


def abs_(r: str) -> Path:
    return DATA_DIR / r
