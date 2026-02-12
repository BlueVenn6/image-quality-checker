"""
Image Quality Checker — Core Logic
===================================
Shared module used by both CLI and MCP server.
No side effects, no I/O to stdout — pure functions that return data.
"""

import os
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:
    raise ImportError("Pillow is required: pip install Pillow")


# ── Format detection ──────────────────────────────────────────────

MAGIC_SIGNATURES = [
    (b'\xff\xd8\xff',                    "JPEG"),
    (b'\x89PNG',                          "PNG"),
    # WEBP: RIFF....WEBP
    (None,                                "WEBP"),   # handled specially
    (b'BM',                               "BMP"),
    (b'II\x2a\x00',                       "TIFF"),
    (b'MM\x00\x2a',                       "TIFF"),
]

EXTENSION_MAP = {
    '.jpg': 'JPEG', '.jpeg': 'JPEG',
    '.png': 'PNG',
    '.webp': 'WEBP',
    '.bmp': 'BMP',
    '.tiff': 'TIFF', '.tif': 'TIFF',
}

SUPPORTED_EXTENSIONS = set(EXTENSION_MAP.keys())


def get_real_format(filepath: str) -> str:
    """Detect real file format by reading magic bytes."""
    with open(filepath, 'rb') as f:
        header = f.read(16)

    if header[:3] == b'\xff\xd8\xff':
        return "JPEG"
    if header[:4] == b'\x89PNG':
        return "PNG"
    if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return "WEBP"
    if header[:2] == b'BM':
        return "BMP"
    if header[:4] in (b'II\x2a\x00', b'MM\x00\x2a'):
        return "TIFF"
    return f"UNKNOWN (hex: {header[:8].hex()})"


# ── JPEG quality estimation ──────────────────────────────────────

def estimate_jpeg_quality(img: Image.Image) -> tuple[Optional[str], Optional[float]]:
    """Estimate JPEG compression quality from quantization tables."""
    if not hasattr(img, 'quantization') or not img.quantization:
        return None, None

    q0 = img.quantization[0]
    avg = sum(q0[i] for i in range(min(8, len(q0)))) / min(8, len(q0))

    if avg <= 1.5:
        label = "95-100 (very high — near lossless)"
    elif avg <= 3:
        label = "90-95 (high — excellent)"
    elif avg <= 5:
        label = "85-90 (high — commercial grade)"
    elif avg <= 8:
        label = "75-85 (medium-high)"
    elif avg <= 16:
        label = "60-75 (medium — visible compression)"
    else:
        label = "<60 (low — not suitable for commercial use)"

    return label, round(avg, 2)


# ── Single-file check ────────────────────────────────────────────

def check_image(filepath: str) -> dict:
    """Check a single image file. Returns a dict of findings."""
    file_size = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    extension = Path(filepath).suffix.lower()
    real_format = get_real_format(filepath)

    expected_format = EXTENSION_MAP.get(extension, "UNKNOWN")
    format_mismatch = (expected_format != real_format)

    try:
        img = Image.open(filepath)
    except Exception as e:
        return {
            'filename': filename,
            'path': str(filepath),
            'error': str(e),
        }

    result = {
        'filename': filename,
        'path': str(filepath),
        'extension': extension,
        'real_format': real_format,
        'format_mismatch': format_mismatch,
        'width': img.size[0],
        'height': img.size[1],
        'mode': img.mode,
        'file_size_bytes': file_size,
        'file_size_mb': round(file_size / 1024 / 1024, 2),
    }

    if real_format == "JPEG":
        quality_label, avg_val = estimate_jpeg_quality(img)
        result['jpeg_quality_label'] = quality_label
        result['jpeg_quality_avg'] = avg_val

    if real_format == "PNG":
        channels = 4 if img.mode == 'RGBA' else 3
        raw_size = img.size[0] * img.size[1] * channels
        result['png_genuine'] = True
        result['png_uncompressed_mb'] = round(raw_size / 1024 / 1024, 1)

    return result


# ── Batch scan ───────────────────────────────────────────────────

def scan_folder(folder: str, recursive: bool = False) -> list[dict]:
    """Scan a folder for image files and check each one."""
    folder = os.path.abspath(folder)

    if recursive:
        files = []
        for root, _dirs, filenames in os.walk(folder):
            for fn in sorted(filenames):
                if Path(fn).suffix.lower() in SUPPORTED_EXTENSIONS:
                    files.append(os.path.join(root, fn))
    else:
        files = [
            os.path.join(folder, f)
            for f in sorted(os.listdir(folder))
            if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    return [check_image(f) for f in files]


# ── Warning generation ───────────────────────────────────────────

def generate_warnings(
    results: list[dict],
    min_width: int = 3000,
    min_height: int = 3000,
    min_jpeg_quality_avg: float = 8.0,
) -> list[dict]:
    """
    Generate warnings based on configurable thresholds.
    Returns list of {filename, type, message} dicts.
    """
    warnings = []

    for r in results:
        if 'error' in r:
            warnings.append({
                'filename': r['filename'],
                'type': 'error',
                'message': f"Cannot open: {r['error']}",
            })
            continue

        if r.get('format_mismatch'):
            warnings.append({
                'filename': r['filename'],
                'type': 'format_mismatch',
                'message': f"Extension {r['extension']} but actual format is {r['real_format']}",
            })

        if r.get('jpeg_quality_avg') is not None and r['jpeg_quality_avg'] > min_jpeg_quality_avg:
            warnings.append({
                'filename': r['filename'],
                'type': 'low_jpeg_quality',
                'message': f"JPEG quality low ({r['jpeg_quality_label']})",
            })

        if r.get('width', 99999) < min_width or r.get('height', 99999) < min_height:
            warnings.append({
                'filename': r['filename'],
                'type': 'low_resolution',
                'message': f"Resolution {r['width']}x{r['height']} below {min_width}x{min_height}",
            })

    return warnings
