# v2.0.0 Upgrade Notes

## What changed

### New file structure
```
image_quality_core.py     ← Core logic (importable by CLI + MCP)
check_image_quality.py    ← CLI (upgraded)
mcp_server.py             ← NEW: MCP server for AI agents
requirements.txt          ← Pillow only
requirements-mcp.txt      ← Pillow + mcp[cli] + pydantic
run_windows.bat           ← Preserved
```

### Breaking changes
- `check_image_quality.py` now imports from `image_quality_core.py` — both files must be in the same directory
- The interactive `input("按回车退出...")` pause is **removed** (was blocking automation). Windows users still have `run_windows.bat` with `pause`

### New CLI features

```bash
# JSON output (for AI agents / scripts)
python check_image_quality.py ./images --json

# CSV output (for spreadsheets / pipelines)
python check_image_quality.py ./images --csv

# Custom thresholds
python check_image_quality.py ./images --min-resolution 4000x4000 --min-jpeg-quality 5

# Recursive scan
python check_image_quality.py ./images --recursive

# Skip writing quality_report.txt
python check_image_quality.py ./images --no-report

# Combine: strict thresholds + JSON + recursive
python check_image_quality.py ./images -r --json --min-resolution 4000x4000
```

### Exit codes (for CI/CD)
| Code | Meaning |
|------|---------|
| 0 | All files passed |
| 1 | Warnings found |
| 2 | Runtime error |

### MCP server (for Claude Desktop / Cursor / AI agents)

```bash
# Install MCP dependencies
pip install -r requirements-mcp.txt

# Run server (stdio transport)
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

Two tools exposed:
- `image_quality_check_file` — single file check
- `image_quality_scan_folder` — batch scan with configurable thresholds

### What stayed the same
- Human-readable output still works by default (just run without flags)
- Same detection logic: magic bytes, JPEG quantization table estimation, format mismatch
- Same supported formats: JPEG, PNG, WEBP, BMP, TIFF
- `run_windows.bat` still works for double-click use
- MIT license
