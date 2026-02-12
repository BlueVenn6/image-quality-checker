# Image Quality Checker (Batch) / 图片质量检测工具（批量）

A tiny open-source Python tool to **batch check image assets** and export a report.

一个开源的 Python 小工具，用于**批量检查图片素材**并导出报告。

---

## What it checks / 检测内容

- **Real file format** by reading file signatures (magic bytes), not file extensions  
  **真实文件格式**：读取文件头（魔数），不依赖扩展名
- **Resolution** (width × height)  
  **分辨率**（宽 × 高）
- **JPEG quality estimate** (heuristic; derived from quantization tables)  
  **JPEG 压缩质量估算**（经验值；基于量化表）
- **File size**  
  **文件大小**
- **Extension mismatch** detection (e.g. `.png` that is actually JPEG)  
  **扩展名与真实格式不符**检测（例如“假 PNG”）
- Exports `quality_report.txt` into the scanned folder  
  在扫描目录输出 `quality_report.txt`

---

## Supported formats / 支持格式

JPEG, PNG, WEBP, BMP, TIFF

---

## Quick start / 快速开始

```bash
git clone https://github.com/BlueVenn6/image-quality-checker.git
cd image-quality-checker
pip install -r requirements.txt
python check_image_quality.py "YOUR_IMAGE_FOLDER"
```

Replace `"YOUR_IMAGE_FOLDER"` with a real path on your computer.  
把 `"YOUR_IMAGE_FOLDER"` 替换为你电脑上的真实图片文件夹路径。

---

## Requirements / 环境要求

- Python 3.8+
- Dependency: Pillow

Install / 安装：
```bash
pip install -r requirements.txt
```

---

## Usage / 使用方法

### Option A: Windows Batch Scripts (recommended for non-technical users) / Windows 批处理脚本（推荐非技术用户）

#### `run_windows_standard.bat`
Simple runner with minimal user interaction:
- **Double-click**: Scans the current folder  
  **双击运行**：扫描当前文件夹
- **Drag-and-drop**: Drag a folder onto the .bat file to scan it  
  **拖放**：将文件夹拖到 .bat 文件上进行扫描

#### `run_windows_lang.bat`
Interactive runner with language selection:
- Prompts user to choose English or Chinese / 提示用户选择英文或中文
- Asks for path to scan (defaults to current directory) / 询问扫描路径（默认当前目录）
- Installs dependencies automatically / 自动安装依赖
- Pauses at the end to review results / 结束时暂停以查看结果

**Important / 重要**: When editing .bat files on Windows, save with **ANSI encoding or UTF-8 without BOM** to avoid character encoding issues. Most text editors have this option under "Save As" → "Encoding".  
**重要**：在 Windows 上编辑 .bat 文件时，请使用 **ANSI 编码或 UTF-8 无 BOM** 保存，以避免字符编码问题。大多数文本编辑器在"另存为"→"编码"中都有此选项。

#### Legacy `run_windows.bat`
The original Windows runner (preserved for compatibility).

### Option B: Command line (recommended for advanced users) / 命令行（推荐高级用户）

#### Scan a folder / 扫描文件夹

**Windows examples（注意带空格/中文路径要加引号）**
```bat
python check_image_quality.py "D:\images"
python check_image_quality.py "D:\素材\上架图片\第1批"
```

**macOS / Linux examples**
```bash
python check_image_quality.py "/Users/yourname/images"
python check_image_quality.py "/home/yourname/images"
```

> `/path/to/images` is just a placeholder used in documentation.  
> `/path/to/images` 只是文档里的占位符示例，并不是真实路径。

#### Scan a single file / 扫描单文件
**Windows**
```bat
python check_image_quality.py "D:\images\test.jpg"
```

**macOS / Linux**
```bash
python check_image_quality.py "/Users/yourname/images/test.jpg"
```

---

## Output / 输出说明

- Console output prints details per image (resolution, size, mode, extension, real format, etc.)  
  控制台逐张输出：分辨率、大小、颜色模式、扩展名、真实格式等
- A summary section lists warnings (low resolution, low JPEG quality, format mismatch, etc.)  
  最后汇总警告：分辨率偏低、JPEG 质量偏低、格式不匹配等
- Report file: `quality_report.txt` (saved in the scanned folder)  
  报告文件：`quality_report.txt`（保存在扫描目录）

---

## Notes / 说明

- JPEG “quality” is an estimate derived from quantization tables. It is **not an exact encoder quality setting**.  
  JPEG“质量”是根据量化表推断的区间值，**不是编码器的精确 quality 参数**。
- Intended for quick screening of asset packs / stock images / mixed-format folders.  
  适合用于快速筛查素材包、图库图片、混合格式文件夹。

---

## Keywords / 关键词（for search）
image quality checker, jpeg quality estimate, format mismatch detector, magic bytes, file signature, batch image audit, Pillow

---
## CLI usage

```bash
# Human-readable report (default, auto-detect language)
python check_image_quality.py [PATH]

# JSON output (for scripts/CI, keys always in English)
python check_image_quality.py [PATH] --json

# CSV output (keys always in English)
python check_image_quality.py [PATH] --csv

# Recursive scan
python check_image_quality.py [PATH] -r

# Custom thresholds (default: 1600x1600, min-jpeg-quality 8.0)
python check_image_quality.py [PATH] --min-resolution 4000x4000 --min-jpeg-quality 5

# Force language (en=English, zh=Chinese)
python check_image_quality.py [PATH] --lang en
python check_image_quality.py [PATH] --lang zh

# Pause before exit (useful for Windows double-click)
python check_image_quality.py [PATH] --pause
```

### Language Selection / 语言选择

The CLI interface language is determined by precedence:

1. **`--lang` flag** (highest priority)  
   `--lang` 参数（最高优先级）
2. **`IQC_LANG` environment variable**  
   环境变量 `IQC_LANG`
3. **System locale** (auto-detect from OS)  
   系统语言（从操作系统自动检测）
4. **Default: Chinese** (fallback)  
   默认值：中文（后备）

Examples / 示例:
```bash
# Use English regardless of system locale
export IQC_LANG=en
python check_image_quality.py ./images

# Use Chinese
export IQC_LANG=zh
python check_image_quality.py ./images

# Override with --lang flag
python check_image_quality.py ./images --lang en
```

**Note**: JSON and CSV outputs **always use English keys** for automation compatibility.  
**注意**：JSON 和 CSV 输出的键名**始终使用英文**，以便自动化工具使用。

### Exit Codes / 退出码

| Code | Meaning / 含义 |
|------|--------------|
| 0 | All files passed / 所有文件通过 |
| 1 | Warnings found / 发现警告 |
| 2 | Runtime error / 运行时错误 |

## MCP server (for AI agents)

Install MCP dependencies:

```bash
pip install -r requirements-mcp.txt
```

Run server (stdio transport):

```bash
python mcp_server.py
```

Exposed tools:
- `image_quality_check_file` — check single image
- `image_quality_scan_folder` — batch scan folder with thresholds

## License

MIT