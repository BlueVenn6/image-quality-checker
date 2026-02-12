"""
Image Quality Checker CLI
==========================
i18n-enabled wrapper around image_quality_core.py
Supports English and Chinese output with configurable thresholds.
"""

import argparse
import json
import csv
import os
import sys
import locale
from pathlib import Path

try:
    from image_quality_core import (
        check_image, scan_folder, generate_warnings, SUPPORTED_EXTENSIONS
    )
except ImportError:
    print("Error: image_quality_core.py must be in the same directory")
    sys.exit(2)


# ── Language Selection ────────────────────────────────────────────────

def detect_language(lang_flag: str = None) -> str:
    """
    Determine interface language.
    Precedence: --lang flag > IQC_LANG env > system locale > default zh
    """
    if lang_flag:
        return lang_flag
    
    env_lang = os.environ.get('IQC_LANG', '').lower()
    if env_lang in ('en', 'zh'):
        return env_lang
    
    # Try system locale
    try:
        # Use getlocale() instead of deprecated getdefaultlocale()
        sys_locale = locale.getlocale()[0]
        if sys_locale:
            if sys_locale.startswith('en'):
                return 'en'
            elif sys_locale.startswith('zh'):
                return 'zh'
    except:
        pass
    
    return 'zh'  # default


# ── Translations ──────────────────────────────────────────────────────

TRANSLATIONS = {
    'en': {
        'title': 'Image Quality Check Report',
        'scan_path': 'Scan path',
        'file_count': 'Files checked',
        'resolution': 'Resolution',
        'file_size': 'File size',
        'color_mode': 'Color mode',
        'extension': 'Extension',
        'real_format': 'Real format',
        'jpeg_quality': 'JPEG quality',
        'genuine_png': 'Genuine PNG lossless format',
        'uncompressed_size': 'Uncompressed size',
        'warning_format_mismatch': 'Warning: Extension is {} but actual format is {}!',
        'warning_low_resolution': 'Low resolution, recommended {}x{} or higher for commercial use',
        'summary': 'Summary',
        'warnings_found': 'Warnings found',
        'recommendation': 'Recommendation: Address these issues before publishing.',
        'all_passed': 'All files passed quality check, suitable for commercial use.',
        'report_saved': 'Report saved to',
        'report_save_failed': 'Failed to save report',
        'error_cannot_open': 'Cannot open',
        'error_path_not_found': 'Path not found',
        'error_no_images': 'No image files found in',
        'bytes': 'bytes',
        'mb': 'MB',
        'pixels': 'pixels',
    },
    'zh': {
        'title': '图片质量检测报告',
        'scan_path': '扫描路径',
        'file_count': '检测文件数',
        'resolution': '分辨率',
        'file_size': '文件大小',
        'color_mode': '颜色模式',
        'extension': '扩展名',
        'real_format': '实际格式',
        'jpeg_quality': 'JPEG质量',
        'genuine_png': '真正的PNG无损格式',
        'uncompressed_size': '未压缩大小',
        'warning_format_mismatch': '警告: 扩展名是 {} 但实际是 {}!',
        'warning_low_resolution': '分辨率偏低，建议商用素材至少 {}x{}',
        'summary': '汇总',
        'warnings_found': '发现问题',
        'recommendation': '建议: 在上架销售前解决以上问题。',
        'all_passed': '所有文件检测通过，可以用于商用素材包。',
        'report_saved': '报告已保存到',
        'report_save_failed': '报告保存失败',
        'error_cannot_open': '无法打开',
        'error_path_not_found': '路径不存在',
        'error_no_images': '没有找到图片文件',
        'bytes': '字节',
        'mb': 'MB',
        'pixels': '像素',
    }
}


def t(key: str, lang: str) -> str:
    """Get translated string."""
    return TRANSLATIONS.get(lang, TRANSLATIONS['zh']).get(key, key)


# ── Output Functions ──────────────────────────────────────────────────

def print_human_readable(results: list, warnings: list, folder: str, lang: str, min_width: int, min_height: int):
    """Print human-readable report to console."""
    print("=" * 70)
    print(f"  {t('title', lang)}")
    print(f"  {t('scan_path', lang)}: {folder}")
    print(f"  {t('file_count', lang)}: {len(results)}")
    print("=" * 70)
    
    for r in results:
        if 'error' in r:
            print(f"\n❌ {r['filename']}: {t('error_cannot_open', lang)} - {r['error']}")
            continue
        
        print(f"\n{'─' * 50}")
        print(f"📄 {r['filename']}")
        print(f"   {t('resolution', lang)}:     {r['width']} x {r['height']} {t('pixels', lang)}")
        print(f"   {t('file_size', lang)}:   {r['file_size_mb']:.2f} {t('mb', lang)} ({r['file_size_bytes']:,} {t('bytes', lang)})")
        print(f"   {t('color_mode', lang)}:   {r['mode']}")
        print(f"   {t('extension', lang)}:     {r['extension']}")
        print(f"   {t('real_format', lang)}:   {r['real_format']}")
        
        if r.get('format_mismatch'):
            print(f"   ⚠️  {t('warning_format_mismatch', lang).format(r['extension'], r['real_format'])}")
        
        if r.get('jpeg_quality_label'):
            print(f"   {t('jpeg_quality', lang)}:   {r['jpeg_quality_label']}")
        
        if r.get('png_genuine'):
            print(f"   ✅ {t('genuine_png', lang)}")
            print(f"   {t('uncompressed_size', lang)}: {r['png_uncompressed_mb']:.1f} {t('mb', lang)}")
        
        # Resolution warning
        if r['width'] < min_width or r['height'] < min_height:
            print(f"   ⚠️  {t('warning_low_resolution', lang).format(min_width, min_height)}")
    
    # Summary
    print(f"\n{'=' * 70}")
    print(f"  {t('summary', lang)}")
    print(f"{'=' * 70}")
    
    if warnings:
        print(f"\n⚠️  {t('warnings_found', lang)}: {len(warnings)}")
        for w in warnings:
            msg = w['message']
            print(f"   • {w['filename']}: {msg}")
        print(f"\n{t('recommendation', lang)}")
    else:
        print(f"\n✅ {t('all_passed', lang)}")


def output_json(results: list, warnings: list):
    """Output results as JSON (always in English)."""
    data = {
        'results': results,
        'warnings': warnings,
        'total_files': len(results),
        'total_warnings': len(warnings),
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))


def output_csv(results: list, warnings: list):
    """Output results as CSV (always in English)."""
    writer = csv.writer(sys.stdout)
    
    # Write results
    writer.writerow(['filename', 'path', 'width', 'height', 'real_format', 'extension', 
                     'format_mismatch', 'file_size_mb', 'jpeg_quality_label', 'jpeg_quality_avg'])
    
    for r in results:
        if 'error' in r:
            writer.writerow([r['filename'], r.get('path', ''), 'ERROR', 'ERROR', 
                           r['error'], '', '', '', '', ''])
        else:
            writer.writerow([
                r['filename'],
                r['path'],
                r['width'],
                r['height'],
                r['real_format'],
                r['extension'],
                r.get('format_mismatch', False),
                r['file_size_mb'],
                r.get('jpeg_quality_label', ''),
                r.get('jpeg_quality_avg', ''),
            ])
    
    # Write warnings section
    writer.writerow([])
    writer.writerow(['WARNINGS'])
    writer.writerow(['filename', 'type', 'message'])
    for w in warnings:
        writer.writerow([w['filename'], w['type'], w['message']])


def write_report_file(results: list, warnings: list, folder: str, lang: str, min_width: int, min_height: int):
    """Write quality_report.txt in the scanned folder (localized)."""
    report_path = os.path.join(folder, "quality_report.txt")
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"{t('title', lang)}\n")
            f.write(f"{t('scan_path', lang)}: {folder}\n")
            f.write(f"{t('file_count', lang)}: {len(results)}\n\n")
            
            for r in results:
                if 'error' in r:
                    f.write(f"{r['filename']}: {t('error_cannot_open', lang)} - {r['error']}\n")
                    continue
                
                f.write(f"{r['filename']}\n")
                f.write(f"  {t('resolution', lang)}: {r['width']}x{r['height']}\n")
                f.write(f"  {t('file_size', lang)}: {r['file_size_mb']:.2f} {t('mb', lang)}\n")
                f.write(f"  {t('extension', lang)}: {r['extension']} / {t('real_format', lang)}: {r['real_format']}\n")
                
                if r.get('format_mismatch'):
                    f.write(f"  ⚠️ {t('warning_format_mismatch', lang).format(r['extension'], r['real_format'])}\n")
                
                if r.get('jpeg_quality_label'):
                    f.write(f"  {t('jpeg_quality', lang)}: {r['jpeg_quality_label']}\n")
                
                if r.get('png_genuine'):
                    f.write(f"  ✅ {t('genuine_png', lang)}\n")
                
                if r['width'] < min_width or r['height'] < min_height:
                    f.write(f"  ⚠️ {t('warning_low_resolution', lang).format(min_width, min_height)}\n")
                
                f.write("\n")
            
            if warnings:
                f.write(f"\n{t('warnings_found', lang)}:\n")
                for w in warnings:
                    f.write(f"  • {w['filename']}: {w['message']}\n")
        
        print(f"\n📋 {t('report_saved', lang)}: {report_path}")
    except Exception as e:
        print(f"\n({t('report_save_failed', lang)}: {e})")


# ── Main Entry Point ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Image Quality Checker - Batch check image assets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default=None,
        help='Path to image file or folder (default: current directory)'
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
        help='Minimum JPEG quality avg value (default: 8.0, lower is better)'
    )
    
    parser.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='Recursively scan subdirectories'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Skip writing quality_report.txt'
    )
    
    parser.add_argument(
        '--lang',
        choices=['en', 'zh'],
        help='Interface language (en=English, zh=Chinese). Default: auto-detect'
    )
    
    parser.add_argument(
        '--pause',
        action='store_true',
        help='Wait for user input before exiting (useful for double-click)'
    )
    
    args = parser.parse_args()
    
    # Determine language
    lang = detect_language(args.lang)
    
    # Parse resolution threshold
    try:
        min_width, min_height = map(int, args.min_resolution.split('x'))
    except:
        print(f"Error: Invalid --min-resolution format. Use WIDTHxHEIGHT (e.g., 1600x1600)")
        sys.exit(2)
    
    # Determine target path
    target_path = args.path if args.path else os.getcwd()
    
    if not os.path.exists(target_path):
        print(f"{t('error_path_not_found', lang)}: {target_path}")
        if args.pause:
            input("\nPress Enter to exit...")
        sys.exit(2)
    
    # Handle single file vs folder
    if os.path.isfile(target_path):
        results = [check_image(target_path)]
        folder = os.path.dirname(os.path.abspath(target_path))
    elif os.path.isdir(target_path):
        results = scan_folder(target_path, recursive=args.recursive)
        folder = os.path.abspath(target_path)
        
        if not results:
            print(f"{t('error_no_images', lang)} {target_path}")
            if args.pause:
                input("\nPress Enter to exit...")
            sys.exit(2)
    else:
        print(f"{t('error_path_not_found', lang)}: {target_path}")
        if args.pause:
            input("\nPress Enter to exit...")
        sys.exit(2)
    
    # Generate warnings based on thresholds
    warnings = generate_warnings(
        results,
        min_width=min_width,
        min_height=min_height,
        min_jpeg_quality_avg=args.min_jpeg_quality
    )
    
    # Output based on format
    if args.json:
        output_json(results, warnings)
    elif args.csv:
        output_csv(results, warnings)
    else:
        print_human_readable(results, warnings, folder, lang, min_width, min_height)
        
        # Write report file unless --no-report
        if not args.no_report:
            write_report_file(results, warnings, folder, lang, min_width, min_height)
    
    # Pause if requested
    if args.pause and not (args.json or args.csv):
        if lang == 'zh':
            input("\n按回车退出...")
        else:
            input("\nPress Enter to exit...")
    
    # Exit with appropriate code
    if warnings:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(2)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
