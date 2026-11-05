"""Image -> text against the OCR.space API. Standard library only."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
import uuid

ENDPOINT = "https://api.ocr.space/parse/image"
DEFAULT_KEY = "helloworld"
MAX_BYTES = 5 * 1024 * 1024


class OcrError(RuntimeError):
    pass


def _multipart(fields: dict[str, str], filename: str, blob: bytes) -> tuple[bytes, str]:
    boundary = "----ocr2text" + uuid.uuid4().hex
    out = bytearray()
    for name, value in fields.items():
        out += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode()
    ctype = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    out += (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode()
    out += blob + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def ocr_bytes(blob: bytes, filename: str = "image.png", lang: str = "eng", engine: int = 2) -> str:
    """Return the recognised text of an image."""
    if not blob:
        raise OcrError("empty image")
    if len(blob) > MAX_BYTES:
        raise OcrError(f"image is {len(blob)} bytes, the API accepts {MAX_BYTES}")

    fields = {
        "apikey": os.environ.get("OCRSPACE_API_KEY", DEFAULT_KEY),
        "language": lang,
        "OCREngine": str(engine),
        "scale": "true",
        "isOverlayRequired": "false",
    }
    body, ctype = _multipart(fields, filename, blob)
    req = urllib.request.Request(ENDPOINT, data=body, headers={"Content-Type": ctype})

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        raise OcrError(f"HTTP {exc.code}: {exc.read()[:200]!r}") from exc
    except urllib.error.URLError as exc:
        raise OcrError(f"network error: {exc.reason}") from exc

    if payload.get("IsErroredOnProcessing"):
        raise OcrError("; ".join(payload.get("ErrorMessage") or ["unknown API error"]))

    return "\n".join(r.get("ParsedText", "") for r in payload.get("ParsedResults") or []).strip()


def ocr_file(path: str, **kwargs) -> str:
    with open(path, "rb") as fh:
        return ocr_bytes(fh.read(), os.path.basename(path), **kwargs)


def ocr_b64(data: str) -> str:
    """OCR a base64 data URL (what img tags and clipboard tools hand you)."""
    if "," not in data:
        raise OcrError("expected a data URL like data:image/png;base64,...")
    header, payload = data.split(",", 1)
    ext = "png" if "png" in header else "jpg"
    return ocr_bytes(base64.b64decode(payload), f"inline.{ext}")
