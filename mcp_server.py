#!/usr/bin/env python3
"""
Image Quality Checker - MCP Server
====================================
Exposes image quality checking as MCP tools for AI agents.

Install:
    pip install -r requirements-mcp.txt

Run (stdio, for Claude Desktop / Cursor):
    python mcp_server.py

Configure in Claude Desktop (claude_desktop_config.json):
    {
      "mcpServers": {
        "image_quality": {
          "command": "python",
          "args": ["/absolute/path/to/mcp_server.py"]
        }
      }
    }
"""

import json
import os
import sys

# Ensure image_quality_core.py can be found regardless of working directory.
# Claude Desktop runs this from its own directory, not the script's.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from mcp.server.fastmcp import FastMCP

from image_quality_core import (
    check_image,
    scan_folder,
    generate_warnings,
)

# -- Server init ---------------------------------------------------

mcp = FastMCP("image_quality_mcp")


# -- Tools ---------------------------------------------------------

@mcp.tool()
async def image_quality_check_file(path: str) -> str:
    """Check a single image file for quality issues.

    Detects real file format via magic bytes, measures resolution,
    estimates JPEG compression quality from quantization tables,
    and flags extension mismatches.

    Args:
        path: Absolute path to an image file (JPEG, PNG, WEBP, BMP, TIFF)

    Returns:
        JSON object with image metadata and quality findings.
    """
    if not os.path.isfile(path):
        return json.dumps({"error": "File not found: {}".format(path)})

    result = check_image(path)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
async def image_quality_scan_folder(
    path: str,
    recursive: bool = False,
    min_width: int = 3000,
    min_height: int = 3000,
    min_jpeg_quality_avg: float = 8.0,
) -> str:
    """Batch-scan a folder of images and return quality report with warnings.

    Scans all supported image files (JPEG, PNG, WEBP, BMP, TIFF) in a folder.
    For each file: detects real format via magic bytes, measures resolution,
    estimates JPEG quality, and flags issues based on configurable thresholds.

    Args:
        path: Absolute path to a folder containing image files.
        recursive: Whether to scan subfolders recursively. Default False.
        min_width: Minimum acceptable image width in pixels. Default 3000.
        min_height: Minimum acceptable image height in pixels. Default 3000.
        min_jpeg_quality_avg: Maximum quantization table average before flagging
            (lower = better quality, 8.0 = medium-high threshold). Default 8.0.

    Returns:
        JSON object with scan_path, file_count, warning_count, pass (bool),
        results (per-file data), and warnings (issues found).
    """
    if not os.path.isdir(path):
        return json.dumps({"error": "Folder not found: {}".format(path)})

    results = scan_folder(path, recursive=recursive)

    if not results:
        return json.dumps({
            "scan_path": path,
            "file_count": 0,
            "warning_count": 0,
            "pass": True,
            "results": [],
            "warnings": [],
        })

    warns = generate_warnings(
        results,
        min_width=min_width,
        min_height=min_height,
        min_jpeg_quality_avg=min_jpeg_quality_avg,
    )

    payload = {
        "scan_path": path,
        "file_count": len(results),
        "warning_count": len(warns),
        "pass": len(warns) == 0,
        "results": results,
        "warnings": warns,
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


# -- Entry point ---------------------------------------------------

if __name__ == "__main__":
    mcp.run()
