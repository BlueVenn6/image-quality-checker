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

### Option A: Run by double-click (Windows) / 双击运行（Windows）
1. Copy `check_image_quality.py` into your image folder  
   把脚本复制到素材图片文件夹中
2. Double-click to run  
   双击运行
3. It will scan that folder and write `quality_report.txt`  
   会扫描该文件夹并生成 `quality_report.txt`

### Option B: Command line (recommended) / 命令行（推荐）

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
# Human-readable report (default)
python check_image_quality.py [PATH]

# JSON output (for scripts/CI)
python check_image_quality.py [PATH] --json

# CSV output
python check_image_quality.py [PATH] --csv

# Recursive scan
python check_image_quality.py [PATH] -r

# Custom thresholds (default: 1600x1600)
python check_image_quality.py [PATH] --min-resolution 1600x1600 --min-jpeg-quality 8.0

# Pause at end (useful for double-click runs)
python check_image_quality.py [PATH] --pause
```

### Language Switching / 语言切换

The CLI supports English and Chinese for human-readable output. JSON/CSV keys always remain in English for automation.

**Language priority:**
1. `--lang en` or `--lang zh` command-line flag
2. `IQC_LANG` environment variable (set to `en` or `zh`)
3. System locale detection
4. Default: Chinese (zh)

**Examples:**
```bash
# Force English output
python check_image_quality.py [PATH] --lang en

# Force Chinese output
python check_image_quality.py [PATH] --lang zh

# Use environment variable (Windows)
set IQC_LANG=en
python check_image_quality.py [PATH]

# Use environment variable (Linux/macOS)
export IQC_LANG=en
python check_image_quality.py [PATH]
```

**Windows batch files:**
- `run_windows_standard.bat` — Quick runner for drag-and-drop or double-click
- `run_windows_lang.bat` — Interactive language selector with prompts

**Important for Windows users:** When creating or editing .bat files, save them with **ANSI encoding** or **UTF-8 without BOM**. Files with UTF-8 BOM may cause `cmd.exe` to display garbled characters.

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