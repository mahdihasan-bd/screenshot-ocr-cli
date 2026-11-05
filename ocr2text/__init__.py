"""ocr2text — dump the text out of screenshots from the shell.

    $ ocr2text shot.png
    $ cat shot.png | ocr2text - --lang eng

Uses the OCR.space HTTP API. Set OCRSPACE_API_KEY (the free "helloworld" key works
for light use, but rate-limits fast).
"""

__version__ = "0.1.0"
