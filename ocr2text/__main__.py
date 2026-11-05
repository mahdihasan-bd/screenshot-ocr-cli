"""CLI: ocr2text IMAGE... | ocr2text -"""

from __future__ import annotations

import argparse
import json
import sys

from .api import OcrError, ocr_file


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ocr2text", description="Extract text from screenshots")
    ap.add_argument("images", nargs="+", help="image paths, or - to read one image from stdin")
    ap.add_argument("--lang", default="eng", help="OCR language code (default: eng)")
    ap.add_argument("--json", action="store_true", help="print JSON, one object per image")
    args = ap.parse_args(argv)

    failures = 0
    for path in args.images:
        try:
            if path == "-":
                import tempfile
                from pathlib import Path

                blob = sys.stdin.buffer.read()
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                    tmp.write(blob)
                    text = ocr_file(tmp.name, lang=args.lang)
                Path(tmp.name).unlink(missing_ok=True)
            else:
                text = ocr_file(path, lang=args.lang)
        except (OcrError, OSError) as exc:
            failures += 1
            if args.json:
                print(json.dumps({"image": path, "ok": False, "error": str(exc)}))
            else:
                print(f"{path}: {exc}", file=sys.stderr)
            continue

        if args.json:
            print(json.dumps({"image": path, "ok": True, "text": text}))
        else:
            if len(args.images) > 1:
                print(f"--- {path} ---")
            print(text)

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
