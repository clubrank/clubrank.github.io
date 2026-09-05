#!/usr/bin/env python3
"""Headerbilder aus dem Projektordner nach docs/ übernehmen.

    python3 bilder.py

Legt einfach eine Datei im Projektordner ab und ruf das Skript auf:

    clubrank_fußball.png     ->  docs/header-fussball.jpg
    clubrank_handball.png    ->  docs/header-handball.jpg
    clubrank_basketball.png  ->  docs/header-basketball.jpg
    clubrank_home.png        ->  docs/header.jpg        (Startseite)

Die Bilder werden dabei auf 1800 px Breite gebracht und als JPEG gespeichert.
Ein unbearbeitetes PNG wiegt schnell zwei Megabyte -- als JPEG sind es rund
250 KB, und der Header lädt bei jedem Seitenaufruf mit.

Gewandelt wird mit `sips`, das auf macOS mitgeliefert wird.
"""
from __future__ import annotations

import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
BREITE = 1800
QUALITAET = 82

# Dateiname (ohne "clubrank_") -> Zieldatei in docs/
ZIELE = {
    "fussball": "header-fussball.jpg",
    "handball": "header-handball.jpg",
    "basketball": "header-basketball.jpg",
    "home": "header.jpg",
    "start": "header.jpg",
    "alle": "header.jpg",
}


def schluessel(name: str) -> str:
    """"clubrank_fußball" -> "fussball" (ß und Umlaute vereinheitlichen)."""
    text = name.lower().removeprefix("clubrank_").removeprefix("clubrank-")
    text = text.replace("ß", "ss").replace("ä", "ae").replace("ö", "oe")
    text = text.replace("ü", "ue")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return text.replace("fussball", "fussball")


def main() -> int:
    DOCS.mkdir(parents=True, exist_ok=True)
    quellen = sorted(p for p in ROOT.iterdir()
                     if p.is_file()
                     and p.suffix.lower() in (".png", ".jpg", ".jpeg")
                     and p.stem.lower().startswith("clubrank"))
    if not quellen:
        print("Keine Datei clubrank_*.png im Projektordner gefunden.", file=sys.stderr)
        print("Erwartet werden: " + ", ".join(f"clubrank_{k}" for k in
                                              ("fussball", "handball", "basketball", "home")),
              file=sys.stderr)
        return 1

    fehler = 0
    for quelle in quellen:
        ziel_name = ZIELE.get(schluessel(quelle.stem))
        if not ziel_name:
            print(f"  ?  {quelle.name}: kein Ziel bekannt — übersprungen",
                  file=sys.stderr)
            continue
        ziel = DOCS / ziel_name
        ergebnis = subprocess.run(
            ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(QUALITAET),
             "--resampleWidth", str(BREITE), str(quelle), "--out", str(ziel)],
            capture_output=True, text=True)
        if ergebnis.returncode != 0 or not ziel.exists():
            print(f"  !  {quelle.name}: {ergebnis.stderr.strip()[:120]}", file=sys.stderr)
            fehler += 1
            continue
        vorher = quelle.stat().st_size / 1024
        nachher = ziel.stat().st_size / 1024
        print(f"  ok {quelle.name} -> docs/{ziel_name} "
              f"({vorher:.0f} KB -> {nachher:.0f} KB)", file=sys.stderr)
    return 1 if fehler else 0


if __name__ == "__main__":
    raise SystemExit(main())
