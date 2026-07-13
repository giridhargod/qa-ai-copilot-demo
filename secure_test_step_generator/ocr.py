"""OCR stage: local-only analysis of a screenshot's pixels.

Produces two signals, both still raw/unsanitized text at this point:
- extract_text(): what pytesseract reads off the screenshot.
- detect_cursor_hint(): a best-effort guess at where the SnagIt
  cursor-preview overlay sits, described in plain text.

Nothing in this module sends image bytes anywhere -- pytesseract runs
locally against the installed Tesseract binary, and the cursor
heuristic is pure Pillow. Both outputs still need to pass through
sanitizer.py before reaching step_generator.py, since OCR'd text can
itself contain PII from the screenshot.
"""
import io

import pytesseract
from PIL import Image, ImageFilter

from . import config
from .models import CursorHint

# Cursor-glyph search parameters. Tuned for a small (16-32px), high
# contrast icon against a comparatively plain background -- the
# typical shape of a SnagIt cursor-preview overlay.
_WINDOW_SIZE = 24
_STRIDE = 8
_EDGE_THRESHOLD = 80
_MIN_EDGE_PIXELS = 6
_MAX_EDGE_PIXELS = 120
_MAX_SCAN_DIMENSION = 800  # downscale larger screenshots before scanning


def extract_text(image_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(image_bytes))
    return pytesseract.image_to_string(image)


def detect_cursor_hint(image_bytes: bytes) -> "CursorHint | None":
    """Best-effort, local-only heuristic for the SnagIt cursor-preview
    overlay's approximate location.

    This is NOT a trained or validated cursor detector. It looks for
    a small, isolated, high-edge-density region -- the rough visual
    signature of a small icon against a plainer background -- and
    only reports a hint when a candidate clears a conservative
    confidence floor (config.CURSOR_HINT_MIN_CONFIDENCE). Known
    limitation: it can be fooled by any other small high-contrast
    glyph (checkboxes, radio buttons, small logos). Treat the result
    as a corroborating hint for the AI stage, never as ground truth --
    when in doubt this function returns None rather than guessing.
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("L")

    scale = 1.0
    width, height = image.size
    if max(width, height) > _MAX_SCAN_DIMENSION:
        scale = _MAX_SCAN_DIMENSION / max(width, height)
        image = image.resize(
            (max(1, int(width * scale)), max(1, int(height * scale)))
        )

    edges = image.filter(ImageFilter.FIND_EDGES)

    # FIND_EDGES treats pixels outside the image as black when
    # convolving, so a uniform-colored image produces a false "edge"
    # ring all the way around its border. Crop that ring out before
    # scanning, or a plain screenshot with no cursor at all would
    # still register a false-positive hint in a top/left corner.
    margin = 3
    edges = edges.crop(
        (margin, margin, edges.width - margin, edges.height - margin)
    )
    scan_width, scan_height = edges.size
    pixels = edges.load()

    best_score = 0.0
    best_box = None

    for top in range(0, max(scan_height - _WINDOW_SIZE, 1), _STRIDE):
        for left in range(0, max(scan_width - _WINDOW_SIZE, 1), _STRIDE):
            edge_count = 0
            for y in range(top, min(top + _WINDOW_SIZE, scan_height)):
                for x in range(left, min(left + _WINDOW_SIZE, scan_width)):
                    if pixels[x, y] > _EDGE_THRESHOLD:
                        edge_count += 1

            if _MIN_EDGE_PIXELS <= edge_count <= _MAX_EDGE_PIXELS:
                score = edge_count / _MAX_EDGE_PIXELS
                if score > best_score:
                    best_score = score
                    best_box = (left, top, left + _WINDOW_SIZE, top + _WINDOW_SIZE)

    if best_box is None:
        return None

    confidence = min(0.9, best_score + 0.3)
    if confidence < config.CURSOR_HINT_MIN_CONFIDENCE:
        return None

    scan_cx = margin + (best_box[0] + best_box[2]) // 2
    scan_cy = margin + (best_box[1] + best_box[3]) // 2
    orig_cx = int(scan_cx / scale)
    orig_cy = int(scan_cy / scale)

    return CursorHint(
        description=(
            f"Possible cursor position near pixel ({orig_cx}, {orig_cy}) "
            f"of a {width}x{height} screenshot"
        ),
        confidence=round(confidence, 2),
    )
