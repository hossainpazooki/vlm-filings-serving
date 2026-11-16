import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium

FILINGS = Path(__file__).resolve().parents[1] / "fixtures" / "filings"
GEN = Path(__file__).resolve().parents[1] / "scripts" / "gen_fixtures.py"

def _pins() -> dict[str, str]:
    out = {}
    for line in (FILINGS / "SHA256SUMS").read_text().splitlines():
        h, name = line.split("  ")
        out[name] = h
    return out

def test_committed_filings_match_pins_and_nothing_unpinned():
    pins = _pins()
    on_disk = {p.name for p in FILINGS.glob("*.pdf")}
    assert on_disk == set(pins), (on_disk, set(pins))
    for name, h in pins.items():
        assert hashlib.sha256((FILINGS / name).read_bytes()).hexdigest() == h, name

def test_index_lists_every_object_with_its_hash_and_role():
    idx = json.loads((FILINGS / "index.json").read_text())["filings"]
    pins = _pins()
    assert {f["id"] + ".pdf" for f in idx} == set(pins)
    for f in idx:
        assert f["sha256"] == pins[f["id"] + ".pdf"]
        assert f["page_role"] in ("primary", "statement") and f["accepted"].endswith(("-04:00", "-05:00"))
        assert set(f) == {"id", "adsh", "cik", "form", "accepted", "page_role", "scale", "sha256"}

def test_filings_open_with_the_declared_page_counts_and_render_non_blank():
    for p in sorted(FILINGS.glob("*.pdf")):
        doc = pdfium.PdfDocument(str(p))
        expected = 1 if p.stem.endswith("-primary") else 2
        assert len(doc) == expected, (p.name, len(doc))
        arr = doc[0].render(scale=1).to_numpy()
        assert arr.min() < 255, p.name  # the filled rectangle and text leave ink
        doc.close()

def test_generator_is_deterministic(tmp_path: Path):
    # Hand-written PDF bytes reproduce exactly, so the pin doubles as a freshness check.
    src = GEN.read_text().replace('OUT = Path(__file__).resolve().parents[1] / "fixtures" / "filings"',
                                  f'OUT = Path({str(tmp_path)!r})')
    (tmp_path / "gen.py").write_text(src)
    subprocess.run([sys.executable, str(tmp_path / "gen.py")], check=True, capture_output=True)
    assert (tmp_path / "SHA256SUMS").read_text() == (FILINGS / "SHA256SUMS").read_text()
