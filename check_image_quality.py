"""
图片质量检测工具
===============
用法: 把这个脚本放到你的素材文件夹里，双击运行
或者命令行: python check_image_quality.py [文件夹路径]

它会检测每张图片的:
- 真实文件格式（不看扩展名，看实际二进制数据）
- 实际分辨率
- 如果是JPEG，估算压缩质量
- 文件大小
- 是否存在"扩展名与实际格式不符"的问题
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("需要安装 Pillow 库，请运行: pip install Pillow")
    input("按回车退出...")
    sys.exit(1)


def get_real_format(filepath):
    """通过读取文件头判断真实格式"""
    with open(filepath, 'rb') as f:
        header = f.read(16)
    
    if header[:3] == b'\xff\xd8\xff':
        return "JPEG"
    elif header[:4] == b'\x89PNG':
        return "PNG"
    elif header[:4] == b'RIFF' and header[8:12] == b'WEBP':
        return "WEBP"
    elif header[:2] == b'BM':
        return "BMP"
    elif header[:4] in (b'II\x2a\x00', b'MM\x00\x2a'):
        return "TIFF"
    else:
        return f"未知 (hex: {header[:8].hex()})"


def estimate_jpeg_quality(img):
    """通过量化表估算JPEG压缩质量"""
    if not hasattr(img, 'quantization') or not img.quantization:
        return None, None
    
    q0 = img.quantization[0]
    avg = sum(q0[i] for i in range(min(8, len(q0)))) / min(8, len(q0))
    
    if avg <= 1.5:
        return "95-100 (极高 - 几乎无损)", avg
    elif avg <= 3:
        return "90-95 (很高 - 优秀)", avg
    elif avg <= 5:
        return "85-90 (高 - 商用合格)", avg
    elif avg <= 8:
        return "75-85 (中高)", avg
    elif avg <= 16:
        return "60-75 (中等 - 有明显压缩痕迹)", avg
    else:
        return "<60 (低 - 不适合商用)", avg


def check_image(filepath):
    """检测单个图片文件"""
    file_size = os.path.getsize(filepath)
    filename = os.path.basename(filepath)
    extension = Path(filepath).suffix.lower()
    real_format = get_real_format(filepath)
    
    # 检查扩展名与实际格式是否匹配
    format_map = {
        '.jpg': 'JPEG', '.jpeg': 'JPEG',
        '.png': 'PNG',
        '.webp': 'WEBP',
        '.bmp': 'BMP',
        '.tiff': 'TIFF', '.tif': 'TIFF'
    }
    expected_format = format_map.get(extension, "未知")
    format_mismatch = (expected_format != real_format)
    
    try:
        img = Image.open(filepath)
    except Exception as e:
        return {
            'filename': filename,
            'error': str(e)
        }
    
    result = {
        'filename': filename,
        'extension': extension,
        'real_format': real_format,
        'format_mismatch': format_mismatch,
        'width': img.size[0],
        'height': img.size[1],
        'mode': img.mode,
        'file_size_mb': file_size / 1024 / 1024,
        'file_size_bytes': file_size,
    }
    
    if real_format == "JPEG":
        quality_est, avg_val = estimate_jpeg_quality(img)
        result['jpeg_quality'] = quality_est
        result['jpeg_q_avg'] = avg_val
    
    if real_format == "PNG":
        channels = 4 if img.mode == 'RGBA' else 3
        raw_size = img.size[0] * img.size[1] * channels
        result['is_genuine_png'] = True
        result['uncompressed_size_mb'] = raw_size / 1024 / 1024
    
    return result


def main():
    # 确定要扫描的文件夹
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = os.path.dirname(os.path.abspath(__file__))
    
    if not os.path.isdir(folder):
        # 如果传入的是文件而不是文件夹
        if os.path.isfile(folder):
            results = [check_image(folder)]
            folder = os.path.dirname(folder)
        else:
            print(f"路径不存在: {folder}")
            input("按回车退出...")
            return
    else:
        # 扫描文件夹中的所有图片
        extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif'}
        files = [
            os.path.join(folder, f) 
            for f in sorted(os.listdir(folder)) 
            if Path(f).suffix.lower() in extensions
        ]
        
        if not files:
            print(f"在 {folder} 中没有找到图片文件")
            input("按回车退出...")
            return
        
        results = [check_image(f) for f in files]
    
    # 输出报告
    print("=" * 70)
    print(f"  图片质量检测报告")
    print(f"  扫描路径: {folder}")
    print(f"  检测文件数: {len(results)}")
    print("=" * 70)
    
    warnings = []
    
    for r in results:
        if 'error' in r:
            print(f"\n❌ {r['filename']}: 无法打开 - {r['error']}")
            continue
        
        print(f"\n{'─' * 50}")
        print(f"📄 {r['filename']}")
        print(f"   分辨率:     {r['width']} x {r['height']} 像素")
        print(f"   文件大小:   {r['file_size_mb']:.2f} MB ({r['file_size_bytes']:,} bytes)")
        print(f"   颜色模式:   {r['mode']}")
        print(f"   扩展名:     {r['extension']}")
        print(f"   实际格式:   {r['real_format']}")
        
        # 格式不匹配警告
        if r['format_mismatch']:
            print(f"   ⚠️  警告: 扩展名是 {r['extension']} 但实际是 {r['real_format']}!")
            warnings.append(f"{r['filename']}: 假{r['extension']}，实际是{r['real_format']}")
        
        # JPEG质量
        if r.get('jpeg_quality'):
            print(f"   JPEG质量:   {r['jpeg_quality']}")
            if r.get('jpeg_q_avg', 999) > 8:
                warnings.append(f"{r['filename']}: JPEG质量偏低 ({r['jpeg_quality']})")
        
        # PNG信息
        if r.get('is_genuine_png'):
            print(f"   ✅ 真正的PNG无损格式")
            print(f"   未压缩大小: {r['uncompressed_size_mb']:.1f} MB")
        
        # 分辨率检查
        if r['width'] < 3000 or r['height'] < 3000:
            print(f"   ⚠️  分辨率偏低，建议商用素材至少 4000x4000")
            warnings.append(f"{r['filename']}: 分辨率 {r['width']}x{r['height']} 偏低")
    
    # 汇总
    print(f"\n{'=' * 70}")
    print(f"  汇总")
    print(f"{'=' * 70}")
    
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个问题:")
        for w in warnings:
            print(f"   • {w}")
        print(f"\n建议: 在上架销售前解决以上问题。")
    else:
        print(f"\n✅ 所有文件检测通过，可以用于商用素材包。")
    
    # 保存报告到文件
    report_path = os.path.join(folder, "quality_report.txt")
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"图片质量检测报告\n")
            f.write(f"扫描路径: {folder}\n")
            f.write(f"检测文件数: {len(results)}\n\n")
            for r in results:
                if 'error' in r:
                    f.write(f"{r['filename']}: 错误 - {r['error']}\n")
                    continue
                f.write(f"{r['filename']}\n")
                f.write(f"  分辨率: {r['width']}x{r['height']}\n")
                f.write(f"  大小: {r['file_size_mb']:.2f} MB\n")
                f.write(f"  扩展名: {r['extension']} / 实际: {r['real_format']}\n")
                if r['format_mismatch']:
                    f.write(f"  ⚠️ 格式不匹配!\n")
                if r.get('jpeg_quality'):
                    f.write(f"  JPEG质量: {r['jpeg_quality']}\n")
                if r.get('is_genuine_png'):
                    f.write(f"  ✅ 真正PNG\n")
                f.write(f"\n")
            
            if warnings:
                f.write(f"\n问题汇总:\n")
                for w in warnings:
                    f.write(f"  • {w}\n")
        
        print(f"\n📋 报告已保存到: {report_path}")
    except Exception as e:
        print(f"\n(报告保存失败: {e})")
    
    input("\n按回车退出...")


if __name__ == "__main__":
    main()
