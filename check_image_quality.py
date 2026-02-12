#!/usr/bin/env python3
"""
Image Quality Checker CLI with i18n support
============================================
Command-line interface that uses image_quality_core.py for checking images.
Supports English and Chinese localization for human-readable output.
JSON/CSV output keys remain in English for automation compatibility.
"""

import argparse
import csv
import json
import locale
import os
import sys
from pathlib import Path

try:
    import image_quality_core as core
except ImportError:
    print("ERROR: Cannot import image_quality_core.py - ensure it's in the same directory")
    sys.exit(2)


# ── Localization dictionaries ────────────────────────────────────────

MESSAGES = {
    'en': {
        'title': 'Image Quality Check Report',
        'scan_path': 'Scan path',
        'files_checked': 'Files checked',
        'filename': 'File',
        'resolution': 'Resolution',
        'file_size': 'File size',
        'color_mode': 'Color mode',
        'extension': 'Extension',
        'real_format': 'Real format',
        'jpeg_quality': 'JPEG quality',
        'genuine_png': '✅ Genuine PNG lossless format',
        'uncompressed_size': 'Uncompressed size',
        'warning_format_mismatch': '⚠️  Warning: Extension is {ext} but actual format is {fmt}!',
        'warning_format_mismatch_short': 'Format mismatch',
        'warning_low_jpeg': '⚠️  JPEG quality is low',
        'warning_low_resolution': '⚠️  Resolution is low, recommend at least {min_w}x{min_h} for commercial use',
        'error_cannot_open': '❌ {filename}: Cannot open - {error}',
        'error_cannot_open_short': 'Cannot open',
        'summary': 'Summary',
        'warnings_found': '⚠️  Found {count} issue(s):',
        'recommend_fix': 'Recommendation: Fix the above issues before publishing.',
        'all_passed': '✅ All files passed checks, ready for commercial use.',
        'report_saved': '📋 Report saved to: {path}',
        'report_save_failed': '(Report save failed: {error})',
        'no_files': 'No image files found in {folder}',
        'path_not_exist': 'Path does not exist: {path}',
        'press_enter': '\nPress Enter to exit...',
        'pillow_required': 'Pillow library is required, please run: pip install Pillow',
    },
    'zh': {
        'title': '图片质量检测报告',
        'scan_path': '扫描路径',
        'files_checked': '检测文件数',
        'filename': '文件',
        'resolution': '分辨率',
        'file_size': '文件大小',
        'color_mode': '颜色模式',
        'extension': '扩展名',
        'real_format': '实际格式',
        'jpeg_quality': 'JPEG质量',
        'genuine_png': '✅ 真正的PNG无损格式',
        'uncompressed_size': '未压缩大小',
        'warning_format_mismatch': '⚠️  警告: 扩展名是 {ext} 但实际是 {fmt}!',
        'warning_format_mismatch_short': '格式不匹配',
        'warning_low_jpeg': '⚠️  JPEG质量偏低',
        'warning_low_resolution': '⚠️  分辨率偏低，建议商用素材至少 {min_w}x{min_h}',
        'error_cannot_open': '❌ {filename}: 无法打开 - {error}',
        'error_cannot_open_short': '无法打开',
        'summary': '汇总',
        'warnings_found': '⚠️  发现 {count} 个问题:',
        'recommend_fix': '建议: 在上架销售前解决以上问题。',
        'all_passed': '✅ 所有文件检测通过，可以用于商用素材包。',
        'report_saved': '📋 报告已保存到: {path}',
        'report_save_failed': '(报告保存失败: {error})',
        'no_files': '在 {folder} 中没有找到图片文件',
        'path_not_exist': '路径不存在: {path}',
        'press_enter': '\n按回车退出...',
        'pillow_required': '需要安装 Pillow 库，请运行: pip install Pillow',
    }
}


# ── Language detection ───────────────────────────────────────────────

def detect_language(args_lang=None):
    """
    Determine language with precedence:
    1. --lang argument
    2. IQC_LANG environment variable
    3. System locale (basic detection)
    4. Default: zh (Chinese)
    """
    # Priority 1: CLI argument
    if args_lang:
        return args_lang
    
    # Priority 2: Environment variable
    env_lang = os.environ.get('IQC_LANG', '').lower()
    if env_lang in ('en', 'zh'):
        return env_lang
    
    # Priority 3: System locale
    try:
        # Use locale.getlocale() to avoid deprecation warning
        system_locale = locale.getlocale()[0]
        if system_locale:
            if system_locale.startswith('zh') or system_locale.startswith('ZH'):
                return 'zh'
            # For most other locales, default to English
            if system_locale.startswith('en') or system_locale.startswith('EN'):
                return 'en'
    except Exception:
        pass
    
    # Priority 4: Check LANG environment variable as fallback
    lang_env = os.environ.get('LANG', '').lower()
    if 'zh' in lang_env:
        return 'zh'
    if 'en' in lang_env:
        return 'en'
    
    # Default: Chinese
    return 'zh'


def msg(key, lang='en', **kwargs):
    """Get localized message with optional formatting."""
    text = MESSAGES.get(lang, MESSAGES['en']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


# ── Output functions ─────────────────────────────────────────────────

def output_human_readable(results, warnings, folder, lang):
    """Print human-readable report to console."""
    print("=" * 70)
    print(f"  {msg('title', lang)}")
    print(f"  {msg('scan_path', lang)}: {folder}")
    print(f"  {msg('files_checked', lang)}: {len(results)}")
    print("=" * 70)
    
    for r in results:
        if 'error' in r:
            print(msg('error_cannot_open', lang, filename=r['filename'], error=r['error']))
            continue
        
        print(f"\n{'─' * 50}")
        print(f"📄 {r['filename']}")
        print(f"   {msg('resolution', lang)}:     {r['width']} x {r['height']} 像素" if lang == 'zh' else f"   {msg('resolution', lang)}:     {r['width']} x {r['height']} pixels")
        print(f"   {msg('file_size', lang)}:   {r['file_size_mb']:.2f} MB ({r['file_size_bytes']:,} bytes)")
        print(f"   {msg('color_mode', lang)}:   {r['mode']}")
        print(f"   {msg('extension', lang)}:     {r['extension']}")
        print(f"   {msg('real_format', lang)}:   {r['real_format']}")
        
        # Format mismatch warning
        if r.get('format_mismatch'):
            print(f"   {msg('warning_format_mismatch', lang, ext=r['extension'], fmt=r['real_format'])}")
        
        # JPEG quality
        if r.get('jpeg_quality_label'):
            print(f"   {msg('jpeg_quality', lang)}:   {r['jpeg_quality_label']}")
        
        # PNG info
        if r.get('png_genuine'):
            print(f"   {msg('genuine_png', lang)}")
            print(f"   {msg('uncompressed_size', lang)}: {r['png_uncompressed_mb']:.1f} MB")
    
    # Summary
    print(f"\n{'=' * 70}")
    print(f"  {msg('summary', lang)}")
    print(f"{'=' * 70}")
    
    if warnings:
        print(f"\n{msg('warnings_found', lang, count=len(warnings))}")
        for w in warnings:
            display = f"{w['filename']}: {w['message']}"
            print(f"   • {display}")
        print(f"\n{msg('recommend_fix', lang)}")
    else:
        print(f"\n{msg('all_passed', lang)}")


def output_json(results):
    """Print JSON output to stdout (keys in English)."""
    print(json.dumps(results, indent=2, ensure_ascii=False))


def output_csv(results):
    """Print CSV output to stdout (keys in English)."""
    if not results:
        return
    
    # Determine all possible keys
    all_keys = set()
    for r in results:
        all_keys.update(r.keys())
    
    fieldnames = sorted(all_keys)
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)


def write_report_file(results, warnings, folder, lang):
    """Write quality_report.txt in the scanned folder."""
    report_path = os.path.join(folder, "quality_report.txt")
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"{msg('title', lang)}\n")
            f.write(f"{msg('scan_path', lang)}: {folder}\n")
            f.write(f"{msg('files_checked', lang)}: {len(results)}\n\n")
            
            for r in results:
                if 'error' in r:
                    f.write(f"{r['filename']}: {msg('error_cannot_open_short', lang)} - {r['error']}\n")
                    continue
                
                f.write(f"{r['filename']}\n")
                f.write(f"  {msg('resolution', lang)}: {r['width']}x{r['height']}\n")
                f.write(f"  {msg('file_size', lang)}: {r['file_size_mb']:.2f} MB\n")
                f.write(f"  {msg('extension', lang)}: {r['extension']} / {msg('real_format', lang)}: {r['real_format']}\n")
                
                if r.get('format_mismatch'):
                    f.write(f"  ⚠️ {msg('warning_format_mismatch_short', lang)}!\n")
                
                if r.get('jpeg_quality_label'):
                    f.write(f"  {msg('jpeg_quality', lang)}: {r['jpeg_quality_label']}\n")
                
                if r.get('png_genuine'):
                    f.write(f"  {msg('genuine_png', lang)}\n")
                
                f.write(f"\n")
            
            if warnings:
                f.write(f"\n{msg('summary', lang)}:\n")
                for w in warnings:
                    f.write(f"  • {w['filename']}: {w['message']}\n")
        
        print(f"\n{msg('report_saved', lang, path=report_path)}")
    except Exception as e:
        print(f"\n{msg('report_save_failed', lang, error=str(e))}")


# ── Main CLI logic ───────────────────────────────────────────────────

def parse_resolution(res_str):
    """Parse resolution string like '1600x1600' into (width, height)."""
    parts = res_str.lower().split('x')
    if len(parts) != 2:
        raise ValueError(f"Invalid resolution format: {res_str}")
    return int(parts[0]), int(parts[1])


def main():
    parser = argparse.ArgumentParser(
        description='Image Quality Checker - Batch check image files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default=None,
        help='Path to folder or single image file (default: current directory)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON (keys in English)'
    )
    parser.add_argument(
        '--csv',
        action='store_true',
        help='Output results as CSV (keys in English)'
    )
    parser.add_argument(
        '--min-resolution',
        default='1600x1600',
        help='Minimum resolution threshold (default: 1600x1600)'
    )
    parser.add_argument(
        '--min-jpeg-quality',
        type=float,
        default=8.0,
        help='Minimum JPEG quality average threshold (default: 8.0)'
    )
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Scan folders recursively'
    )
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Skip writing quality_report.txt'
    )
    parser.add_argument(
        '--lang',
        choices=['en', 'zh'],
        help='Language for human-readable output (en=English, zh=Chinese)'
    )
    parser.add_argument(
        '--pause',
        action='store_true',
        help='Pause at the end (useful for double-click runs)'
    )
    
    args = parser.parse_args()
    
    # Determine language
    lang = detect_language(args.lang)
    
    # Determine path to scan
    if args.path:
        target_path = args.path
    else:
        target_path = os.getcwd()
    
    target_path = os.path.abspath(target_path)
    
    # Parse resolution threshold
    try:
        min_width, min_height = parse_resolution(args.min_resolution)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    
    # Check if path exists
    if not os.path.exists(target_path):
        if not (args.json or args.csv):
            print(msg('path_not_exist', lang, path=target_path))
        if args.pause:
            input(msg('press_enter', lang))
        sys.exit(2)
    
    # Scan files
    try:
        if os.path.isfile(target_path):
            # Single file
            results = [core.check_image(target_path)]
            folder = os.path.dirname(target_path)
        elif os.path.isdir(target_path):
            # Folder scan
            results = core.scan_folder(target_path, recursive=args.recursive)
            folder = target_path
            
            if not results:
                if not (args.json or args.csv):
                    print(msg('no_files', lang, folder=folder))
                if args.pause:
                    input(msg('press_enter', lang))
                sys.exit(0)
        else:
            if not (args.json or args.csv):
                print(msg('path_not_exist', lang, path=target_path))
            if args.pause:
                input(msg('press_enter', lang))
            sys.exit(2)
    except Exception as e:
        print(f"Error scanning: {e}", file=sys.stderr)
        if args.pause:
            input(msg('press_enter', lang))
        sys.exit(2)
    
    # Generate warnings with thresholds
    warnings = core.generate_warnings(
        results,
        min_width=min_width,
        min_height=min_height,
        min_jpeg_quality_avg=args.min_jpeg_quality
    )
    
    # Output based on format
    if args.json:
        output_json(results)
    elif args.csv:
        output_csv(results)
    else:
        # Human-readable output
        output_human_readable(results, warnings, folder, lang)
        
        # Write report file
        if not args.no_report:
            write_report_file(results, warnings, folder, lang)
    
    # Pause if requested
    if args.pause:
        input(msg('press_enter', lang))
    
    # Exit code
    if warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
