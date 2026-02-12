# Image Quality Checker

A small open-source Python tool to **batch-audit image assets** before publishing. Detects format mismatches, resolution issues, and JPEG compression quality -- then writes a report.

## What it checks

- **Real file format** via magic bytes (not file extensions)
- **Resolution** (width x height)
- **JPEG compression quality** (heuristic from quantization tables)
- **File size**
- **Extension mismatch** (e.g. a `.png` that is actually JPEG)

Supported formats: JPEG, PNG, WEBP, BMP, TIFF

## Quick start

```bash
git clone https://github.com/BlueVenn6/image-quality-checker.git
cd image-quality-checker
pip install -r requirements.txt
python check_image_quality.py /path/to/your/images
```

### Windows (no terminal)

Double-click `run_windows.bat`, paste your folder path, and read the report.

## CLI usage

```bash
# Human-readable report (default)
python check_image_quality.py /path/to/images

# JSON output (for scripts / AI agents / CI)
python check_image_quality.py /path/to/images --json

# CSV output (for spreadsheets / data pipelines)
python check_image_quality.py /path/to/images --csv

# Recursive scan (include subfolders)
python check_image_quality.py /path/to/images --recursive

# Custom thresholds
python check_image_quality.py /path/to/images --min-resolution 4000x4000 --min-jpeg-quality 5

# Skip writing quality_report.txt
python check_image_quality.py /path/to/images --no-report

# Combine flags
python check_image_quality.py /path/to/images -r --json --min-resolution 4000x4000
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | All files passed |
| 1 | Warnings found |
| 2 | Runtime error |

## MCP server (for AI agents)

The repo includes an MCP server so AI agents (Claude Desktop, Cursor, etc.) can call the checker directly.

```bash
pip install -r requirements-mcp.txt
python mcp_server.py
```

**Claude Desktop config** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "image_quality": {
      "command": "python",
      "args": ["/absolute/path/to/mcp_server.py"]
    }
  }
}
```

Exposed tools:

- `image_quality_check_file` -- check a single image
- `image_quality_scan_folder` -- batch scan with configurable thresholds

## File structure

```
image_quality_core.py     Core logic (shared by CLI + MCP)
check_image_quality.py    CLI entry point
mcp_server.py             MCP server for AI agents
run_windows.bat           Double-click launcher for Windows
requirements.txt          Pillow only
requirements-mcp.txt      Pillow + mcp[cli] + pydantic
```

## Requirements

- Python 3.8+
- Pillow

## License

MIT
