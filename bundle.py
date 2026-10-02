#!/usr/bin/env python3
"""Bundle each report page + styles.css into single, portable HTML files.

The working copy keeps CSS in styles.css (linked) so the pages stay short and
editable. A linked relative stylesheet doesn't travel well, so this script
inlines styles.css into a <style> block in each page.

Usage:
    python3 bundle.py                      # every top-level *.html -> dist/<same name>
    python3 bundle.py path/to/output.html  # index.html only, custom output path (legacy)

Multi-page reports (e.g. index.html + evidence.html): pages link to each other
by relative filename, so bundles keep their original names and must travel
together in the same folder. Emailing one bundled page alone breaks its
cross-page links.

Run it from the repo root. It does not modify the source files.

NOTE ON THE PDF BUTTON: the PDF export of the final Google Doc is embedded in
index.html as base64 (PDF_B64 / PDF_NAME), so it survives bundling intact.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSS = ROOT / "styles.css"
LINK_RE = re.compile(r'<link rel="stylesheet" href="styles\.css(?:\?[^"]*)?">')


def bundle(page: Path, out: Path, css: str) -> bool:
    html = page.read_text(encoding="utf-8")
    matches = LINK_RE.findall(html)
    if len(matches) != 1:
        print(f"error: found {len(matches)} stylesheet links in {page.name}; expected exactly one", file=sys.stderr)
        return False
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(LINK_RE.sub(lambda _m: f"<style>\n{css}\n</style>", html, count=1), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
    return True


def main() -> int:
    if not CSS.exists():
        print(f"error: expected {CSS.name} next to this script", file=sys.stderr)
        return 1
    css = CSS.read_text(encoding="utf-8")
    if len(sys.argv) > 1:
        return 0 if bundle(ROOT / "index.html", Path(sys.argv[1]), css) else 1
    pages = sorted(p for p in ROOT.glob("*.html"))
    if not pages:
        print("error: no .html pages found", file=sys.stderr)
        return 1
    ok = all(bundle(p, ROOT / "dist" / p.name, css) for p in pages)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
