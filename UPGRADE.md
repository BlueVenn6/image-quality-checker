# v2.0.0 Upgrade Notes

## What changed

### New file structure
```
image_quality_core.py       ← Core logic (importable by CLI + MCP)
check_image_quality.py      ← CLI (upgraded with i18n support)
mcp_server.py               ← NEW: MCP server for AI agents
requirements.txt            ← Pillow only
requirements-mcp.txt        ← Pillow + mcp[cli] + pydantic
run_windows.bat             ← Legacy (preserved for compatibility)
run_windows_standard.bat    ← NEW: Standard Windows runner
run_windows_lang.bat        ← NEW: Interactive language selector
```

### Breaking changes
- `check_image_quality.py` now imports from `image_quality_core.py` — both files must be in the same directory
- The interactive `input("按回车退出...")` pause is **removed** by default (was blocking automation). Use `--pause` flag or Windows batch files for pause behavior
- Default `--min-resolution` changed from `3000x3000` to `1600x1600`

### i18n (Internationalization) Support
- CLI now supports English (`en`) and Chinese (`zh`) for human-readable output
- Language selection priority: `--lang` flag > `IQC_LANG` env var > system locale > default (zh)
- **Important:** JSON and CSV output keys **always remain in English** for automation compatibility
- Only human-readable console output and `quality_report.txt` are localized

```bash
# Examples
python check_image_quality.py [PATH] --lang en    # Force English
python check_image_quality.py [PATH] --lang zh    # Force Chinese
set IQC_LANG=en                                    # Windows env var
export IQC_LANG=en                                 # Linux/macOS env var
```

### New CLI features

```bash
# JSON output (for AI agents / scripts)
python check_image_quality.py ./images --json

# CSV output (for spreadsheets / pipelines)
python check_image_quality.py ./images --csv

# Custom thresholds (default changed to 1600x1600)
python check_image_quality.py ./images --min-resolution 1600x1600 --min-jpeg-quality 8.0

# Recursive scan
python check_image_quality.py ./images --recursive

# Skip writing quality_report.txt
python check_image_quality.py ./images --no-report

# Pause at end (for double-click use)
python check_image_quality.py ./images --pause

# Combine: strict thresholds + JSON + recursive
python check_image_quality.py ./images -r --json --min-resolution 4000x4000
```

### Windows Batch Files
- **`run_windows_standard.bat`** — Quick runner for drag-and-drop or double-click; runs without pause by default
- **`run_windows_lang.bat`** — Interactive language selector; prompts for language choice and path, runs with pause
- **Encoding note:** When creating or editing .bat files, save them as **ANSI** or **UTF-8 without BOM** to avoid garbled characters in `cmd.exe`

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
