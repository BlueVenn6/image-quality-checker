#!/usr/bin/env python3
"""
Image Quality Checker (Batch) - CLI
====================================
Usage:
    python check_image_quality.py [PATH]
    python check_image_quality.py [PATH] --json
    python check_image_quality.py [PATH] --csv
    python check_image_quality.py [PATH] --min-resolution 4000x4000 --min-jpeg-quality 5
    python check_image_quality.py [PATH] --recursive --json

Exit codes:
    0  All files passed
    1  One or more warnings found
    2  Runtime error (path not found, etc.)
"""

import os
import sys

# ---- Double-click detection (MUST be before any risky imports) ----
# No args + attached to a real terminal = user double-clicked the file
_INTERACTIVE = (len(sys.argv) <= 1) and sys.stdin is not None
try:
    _INTERACTIVE = _INTERACTIVE and sys.stdin.isatty()
except Exception:
    _INTERACTIVE = False

# Add script's own directory to import path so image_quality_core is found
# regardless of what the working directory is when double-clicked
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)


def _pause_if_interactive():
    """Pause before exit so the window stays open on double-click."""
    if _INTERACTIVE:
        print("")
        input("Press Enter to exit...")


# ---- Wrap everything so import errors don't cause flash-close ----
try:
    import argparse
    import csv
    import io
    import json
    from pathlib import Path

    from image_quality_core import (
        check_image,
        generate_warnings,
        scan_folder,
        SUPPORTED_EXTENSIONS,
    )
except ImportError as e:
    print("Missing dependency: {}".format(e))
    print("")
    print("Make sure these files are in the same folder:")
    print("  - check_image_quality.py  (this file)")
    print("  - image_quality_core.py")
    print("")
    print("Then install requirements:")
    print("  pip install Pillow")
    _pause_if_interactive()
    sys.exit(2)
except Exception as e:
    print("Startup error: {}".format(e))
    _pause_if_interactive()
    sys.exit(2)


# -- Argument parsing ----------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="check_image_quality",
        description="Batch image quality checker: format sniffing, resolution, JPEG quality estimate.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="File or folder to scan (default: current directory)",
    )

    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument("--json", action="store_true", dest="output_json", help="Output results as JSON")
    fmt.add_argument("--csv", action="store_true", dest="output_csv", help="Output results as CSV")

    parser.add_argument(
        "--min-resolution",
        default="3000x3000",
        help="Minimum resolution WxH (default: 3000x3000)",
    )
    parser.add_argument(
        "--min-jpeg-quality",
        type=float,
        default=8.0,
        help="Max quantization avg before warning (lower=better, default: 8.0)",
    )

    parser.add_argument("--recursive", "-r", action="store_true", help="Scan subfolders recursively")
    parser.add_argument("--no-report", action="store_true", help="Skip writing quality_report.txt")

    return parser.parse_args(argv)


def parse_resolution(s):
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except (ValueError, AttributeError):
        print("Error: invalid resolution format '{}', expected WxH".format(s), file=sys.stderr)
        sys.exit(2)


# -- Output formatters ---------------------------------------------

def output_json(results, warnings, folder):
    payload = {
        "scan_path": folder,
        "file_count": len(results),
        "warning_count": len(warnings),
        "results": results,
        "warnings": warnings,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def output_csv(results):
    if not results:
        return
    fieldnames = []
    seen = set()
    for r in results:
        for k in r.keys():
            if k not in seen:
                fieldnames.append(k)
                seen.add(k)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for r in results:
        writer.writerow(r)
    print(buf.getvalue(), end="")


def output_human(results, warnings, folder):
    print("=" * 70)
    print("  Image Quality Report")
    print("  Path: {}".format(folder))
    print("  Files: {}".format(len(results)))
    print("=" * 70)

    for r in results:
        if 'error' in r:
            print("\n[ERROR] {}: Cannot open - {}".format(r['filename'], r['error']))
            continue

        print("\n" + "-" * 50)
        print("  {}".format(r['filename']))
        print("   Resolution:  {} x {} px".format(r['width'], r['height']))
        print("   File size:   {:.2f} MB ({:,} bytes)".format(r['file_size_mb'], r['file_size_bytes']))
        print("   Color mode:  {}".format(r['mode']))
        print("   Extension:   {}".format(r['extension']))
        print("   Real format: {}".format(r['real_format']))

        if r.get('format_mismatch'):
            print("   [!] Mismatch: extension is {} but actual format is {}".format(
                r['extension'], r['real_format']))

        if r.get('jpeg_quality_label'):
            print("   JPEG quality: {}".format(r['jpeg_quality_label']))

        if r.get('png_genuine'):
            print("   Genuine PNG (lossless)")
            print("   Uncompressed: {:.1f} MB".format(r['png_uncompressed_mb']))

    print("\n" + "=" * 70)
    print("  Summary")
    print("=" * 70)

    if warnings:
        print("\n  {} issue(s) found:".format(len(warnings)))
        for w in warnings:
            print("   - {}: {}".format(w['filename'], w['message']))
        print("\n  Fix these before publishing.")
    else:
        print("\n  All files passed.")


def write_report(results, warnings, folder):
    report_path = os.path.join(folder, "quality_report.txt")
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("Image Quality Report\n")
            f.write("Path: {}\n".format(folder))
            f.write("Files: {}\n\n".format(len(results)))
            for r in results:
                if 'error' in r:
                    f.write("{}: error - {}\n\n".format(r['filename'], r['error']))
                    continue
                f.write("{}\n".format(r['filename']))
                f.write("  Resolution: {}x{}\n".format(r['width'], r['height']))
                f.write("  Size: {:.2f} MB\n".format(r['file_size_mb']))
                f.write("  Extension: {} / Actual: {}\n".format(r['extension'], r['real_format']))
                if r.get('format_mismatch'):
                    f.write("  [!] Format mismatch\n")
                if r.get('jpeg_quality_label'):
                    f.write("  JPEG quality: {}\n".format(r['jpeg_quality_label']))
                if r.get('png_genuine'):
                    f.write("  Genuine PNG\n")
                f.write("\n")
            if warnings:
                f.write("Issues:\n")
                for w in warnings:
                    f.write("  - {}: {}\n".format(w['filename'], w['message']))
        return report_path
    except Exception:
        return None


# -- Main ----------------------------------------------------------

def main(argv=None):
    args = parse_args(argv)
    min_w, min_h = parse_resolution(args.min_resolution)

    target = args.path or os.getcwd()

    if os.path.isfile(target):
        results = [check_image(target)]
        folder = os.path.dirname(os.path.abspath(target))
    elif os.path.isdir(target):
        results = scan_folder(target, recursive=args.recursive)
        folder = os.path.abspath(target)
    else:
        print("Error: path not found: {}".format(target), file=sys.stderr)
        sys.exit(2)

    if not results:
        if args.output_json:
            output_json([], [], folder)
        elif args.output_csv:
            pass
        else:
            print("No image files found in {}".format(folder))
        sys.exit(0)

    warnings = generate_warnings(
        results,
        min_width=min_w,
        min_height=min_h,
        min_jpeg_quality_avg=args.min_jpeg_quality,
    )

    if args.output_json:
        output_json(results, warnings, folder)
    elif args.output_csv:
        output_csv(results)
    else:
        output_human(results, warnings, folder)
        if not args.no_report:
            rp = write_report(results, warnings, folder)
            if rp:
                print("\nReport saved: {}".format(rp))

    sys.exit(1 if warnings else 0)


# -- Entry point ---------------------------------------------------

if __name__ == "__main__":
    if _INTERACTIVE:
        # Double-click mode: prompt for path, always pause before closing
        print("")
        print("  Image Quality Checker")
        print("  " + "-" * 40)
        print("")
        _path = input("  Enter folder or file path: ").strip().strip('"')
        if not _path:
            print("  No path entered.")
            _pause_if_interactive()
            sys.exit(0)
        try:
            main([_path])
        except SystemExit:
            pass
        except Exception as e:
            print("\n  Error: {}".format(e))
        _pause_if_interactive()
    else:
        # CLI / script / bat mode: run normally, no pause
        main()
