# ocr2text

Pull the text out of screenshots and images from the shell. Standard library only, one dependency-free command.

I wrote this because copying text out of phone screenshots by hand — for tracing work, receipts, error dialogs — was eating whole afternoons.

## Install

```bash
git clone https://github.com/mahdihasan-bd/screenshot-ocr-cli
cd screenshot-ocr-cli
python -m venv .venv && . .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e .
```

## Use

```bash
$ ocr2text screenshot.png
FIFA
WE ARE 26.
CANADA
MOROCCO
...

$ cat shot.png | ocr2text -
$ ocr2text a.png b.png --json          # one JSON object per image
$ ocr2text menu.jpg --lang ben         # OCR.space language code
```

`--json` prints `{"image": ..., "ok": true, "text": ...}`. A failed image is reported and the exit code is `1`, so it composes with `&&` and CI.

## API key

The free `helloworld` key is the default but rate-limits quickly. For real use:

```bash
export OCRSPACE_API_KEY=xxxxxxxxxxxxxxxx     # https://ocr.space/ocrapi/freekey
```

## Use it as a library

```python
from ocr2text.api import ocr_file, ocr_b64

ocr_file("receipt.png")           # str of recognised text
ocr_b64(data_url_from_clipboard)  # same, straight from a data URL
```

`OcrError` covers empty or oversized input (>5 MB), network failures and API errors.

## Notes and limits

- Images only; no PDF support.
- 5 MB per image, checked before upload.
- Text in Bangla works with `--lang ben` but accuracy depends on the source image quality.

## Licence

MIT
