#!/usr/bin/env python3
"""Generate/check SWIR progress SVGs from Titanium's v10.0 release criteria."""
from __future__ import annotations
import argparse, re
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "assets" / "readme"
ROADMAP = ROOT / "ROADMAP.md"
LEGACY = re.compile(r"(?:[█▓▒░]{4,}|\[(?:[#=\-]){6,}\])")

def state() -> tuple[int, int, float, str]:
    text = ROADMAP.read_text(encoding="utf-8")
    section = text.split("## Stable release criteria", 1)[1].split("## After v10.0", 1)[0]
    items = [line for line in section.splitlines() if re.match(r"^\d+\.\s", line)]
    done = sum("✅" in line for line in items)
    total = len(items)
    if total == 0:
        raise RuntimeError("No stable release criteria found")
    pct = done / total * 100.0
    status = "COMPLETE" if done == total else "IN PROGRESS"
    return done, total, pct, status

def card(done: int, total: int, pct: float, status: str) -> str:
    width = 1100 * done / total
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180" role="img" aria-labelledby="title desc"><title id="title">Titanium APK Builder v10.0 stable release criteria</title><desc id="desc">The named v10.0 stable release criteria are complete: {done} of {total}, {pct:.1f} percent. Future post-v10 work is outside this completed scope.</desc><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#02050A"/><stop offset="1" stop-color="#07111C"/></linearGradient><linearGradient id="fill" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient><pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#62E5FF" stroke-opacity=".05"/></pattern></defs><rect x="1" y="1" width="1198" height="178" rx="22" fill="url(#bg)" stroke="#62E5FF" stroke-opacity=".25"/><rect x="1" y="1" width="1198" height="178" rx="22" fill="url(#grid)"/><text x="50" y="38" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" letter-spacing="3">SWIR PROGRESS</text><text x="50" y="72" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="26" font-weight="800">Titanium APK Builder</text><text x="50" y="98" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="14">v10.0 stable release criteria</text><text x="1110" y="72" text-anchor="end" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="30" font-weight="800">{pct:.1f}%</text><text x="1110" y="98" text-anchor="end" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="13" font-weight="700">{status}</text><rect x="50" y="116" width="1100" height="18" rx="9" fill="#08131F" stroke="#62E5FF" stroke-opacity=".15"/><rect x="50" y="116" width="{width:g}" height="18" rx="9" fill="url(#fill)"/><text x="50" y="158" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">Stable release criteria: {done} / {total} complete · post-v10 work is a separate future scope</text></svg>\n'''

def mini(done: int, total: int, pct: float) -> str:
    width = 220 * done / total
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="72" viewBox="0 0 900 72" role="img" aria-labelledby="title desc"><title id="title">Titanium APK Builder compact v10.0 release progress</title><desc id="desc">Stable release criteria are {done} of {total} complete, {pct:.1f} percent.</desc><defs><linearGradient id="fill" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#0088FF"/><stop offset="1" stop-color="#62E5FF"/></linearGradient></defs><rect x="1" y="1" width="898" height="70" rx="16" fill="#02050A" stroke="#62E5FF" stroke-opacity=".24"/><text x="24" y="28" fill="#F4FAFF" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="700">Titanium APK Builder · v10.0 stable criteria</text><text x="24" y="51" fill="#8DA8B8" font-family="Segoe UI,Arial,sans-serif" font-size="12">Stable release criteria: {done} / {total}</text><rect x="590" y="27" width="220" height="14" rx="7" fill="#08131F"/><rect x="590" y="27" width="{width:g}" height="14" rx="7" fill="url(#fill)"/><text x="866" y="40" text-anchor="end" fill="#62E5FF" font-family="Segoe UI,Arial,sans-serif" font-size="14" font-weight="800">{pct:.1f}%</text></svg>\n'''

def outputs() -> tuple[str, str]:
    done, total, pct, status = state()
    return card(done, total, pct, status), mini(done, total, pct)

def check() -> int:
    expected_card, expected_mini = outputs()
    for name, expected in (("progress-card.svg", expected_card), ("progress-mini.svg", expected_mini)):
        ET.fromstring(expected)
        path = ASSET / name
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            print(f"stale or missing: {path}"); return 1
    template = ASSET / "progress-template.svg"
    if not template.exists(): print("missing progress-template.svg"); return 1
    ET.fromstring(template.read_text(encoding="utf-8"))
    for path in (ROOT / "README.md", ROADMAP):
        if LEGACY.search(path.read_text(encoding="utf-8")):
            print(f"legacy progress meter found: {path}"); return 1
    print("SWIR progress check: OK"); return 0

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--check", action="store_true"); a = p.parse_args()
    if not a.check:
        ASSET.mkdir(parents=True, exist_ok=True)
        c, m = outputs()
        (ASSET / "progress-card.svg").write_text(c, encoding="utf-8")
        (ASSET / "progress-mini.svg").write_text(m, encoding="utf-8")
    return check()

if __name__ == "__main__": raise SystemExit(main())
