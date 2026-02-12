# v2.0.0 Upgrade Notes

## What changed

### New file structure
```
image_quality_core.py              ← Core logic (importable by CLI + MCP)
check_image_quality.py             ← CLI (upgraded with i18n support)
mcp_server.py                      ← MCP server for AI agents
requirements.txt                   ← Pillow only
requirements-mcp.txt               ← Pillow + mcp[cli] + pydantic
run_windows.bat                    ← Legacy Windows runner (preserved)
run_windows_standard.bat           ← NEW: Simple Windows runner
run_windows_lang.bat               ← NEW: Interactive language selector
```

### Breaking changes
- `check_image_quality.py` now imports from `image_quality_core.py` — both files must be in the same directory
- The interactive `input("按回车退出...")` pause is **removed by default** (was blocking automation). Use `--pause` flag when needed (e.g., for double-click usage)
- Default minimum resolution changed from 3000x3000 to **1600x1600** — this reflects modern web standards (e.g., Retina displays at 2x scaling from 800x800 base) and common marketplace requirements. For high-end commercial use (large prints, 4K displays), use `--min-resolution 4000x4000`

### New CLI features

#### i18n Support (English + Chinese)
```bash
# Language selection precedence: --lang > IQC_LANG env > locale > default zh
python check_image_quality.py ./images --lang en
python check_image_quality.py ./images --lang zh

# Use environment variable
export IQC_LANG=en
python check_image_quality.py ./images
```

**Important**: JSON and CSV outputs **always use English keys** for automation compatibility, regardless of language setting.

#### Pause flag
```bash
# Wait for user input before exiting (useful for double-click)
python check_image_quality.py ./images --pause
```

#### Updated thresholds
```bash
# Default resolution: 1600x1600 (was 3000x3000)
python check_image_quality.py ./images

# Custom thresholds
python check_image_quality.py ./images --min-resolution 4000x4000 --min-jpeg-quality 5
```

#### Other features (from v2.0.0)

```bash
# Recursive scan
python check_image_quality.py ./images --recursive

# Skip writing quality_report.txt
python check_image_quality.py ./images --no-report

# Combine: strict thresholds + JSON + recursive
python check_image_quality.py ./images -r --json --min-resolution 4000x4000
```

### Windows Runners

#### `run_windows_standard.bat` (NEW)
- Minimal robust runner for double-click or drag-and-drop
- Changes to script directory automatically
- Optional dependency installation (commented by default)
- No blocking prompts (can uncomment pause if needed)

#### `run_windows_lang.bat` (NEW)
- Interactive language selector (English or Chinese)
- Prompts for scan path with default to current directory
- Automatically installs dependencies
- Uses `--pause` flag to keep window open

**Important**: Save .bat files with **ANSI encoding or UTF-8 without BOM** to prevent character encoding issues on Windows.

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
