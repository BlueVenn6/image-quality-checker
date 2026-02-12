#!/usr/bin/env python3
"""
Image Quality Checker — MCP Server
====================================
Exposes image quality checking as MCP tools for AI agents.

Install:
    pip install mcp[cli] Pillow

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
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

from image_quality_core import (
    check_image,
    scan_folder,
    generate_warnings,
)

# ── Server init ──────────────────────────────────────────────────

mcp = FastMCP("image_quality_mcp")


# ── Input models ─────────────────────────────────────────────────

class CheckImageInput(BaseModel):
    """Input for checking a single image file."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    path: str = Field(
        ...,
        description="Absolute path to an image file (JPEG, PNG, WEBP, BMP, TIFF)",
        min_length=1,
    )


class ScanFolderInput(BaseModel):
    """Input for batch-scanning a folder of images."""
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    path: str = Field(
        ...,
        description="Absolute path to a folder containing image files",
        min_length=1,
    )
    recursive: bool = Field(
        default=False,
        description="Whether to scan subfolders recursively",
    )
    min_width: int = Field(
        default=3000,
        description="Minimum acceptable image width in pixels",
        ge=1,
    )
    min_height: int = Field(
        default=3000,
        description="Minimum acceptable image height in pixels",
        ge=1,
    )
    min_jpeg_quality_avg: float = Field(
        default=8.0,
        description="Maximum quantization table average before flagging (lower = better quality, 8.0 = medium-high threshold)",
        ge=0.0,
    )


# ── Tools ────────────────────────────────────────────────────────

@mcp.tool(
    name="image_quality_check_file",
    annotations={
        "title": "Check Single Image Quality",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def check_file(params: CheckImageInput) -> str:
    """Check a single image file for quality issues.

    Detects real file format via magic bytes, measures resolution,
    estimates JPEG compression quality from quantization tables,
    and flags extension mismatches.

    Args:
        params (CheckImageInput): Contains:
            - path (str): Absolute path to an image file

    Returns:
        str: JSON object with image metadata and quality findings
    """
    if not os.path.isfile(params.path):
        return json.dumps({"error": f"File not found: {params.path}"})

    result = check_image(params.path)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool(
    name="image_quality_scan_folder",
    annotations={
        "title": "Batch Scan Folder for Image Quality",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def scan_folder_tool(params: ScanFolderInput) -> str:
    """Batch-scan a folder of images and return quality report with warnings.

    Scans all supported image files (JPEG, PNG, WEBP, BMP, TIFF) in a folder.
    For each file: detects real format via magic bytes, measures resolution,
    estimates JPEG quality, and flags issues based on configurable thresholds.

    Args:
        params (ScanFolderInput): Contains:
            - path (str): Absolute path to folder
            - recursive (bool): Scan subfolders (default: False)
            - min_width (int): Minimum width in px (default: 3000)
            - min_height (int): Minimum height in px (default: 3000)
            - min_jpeg_quality_avg (float): Quantization threshold (default: 8.0)

    Returns:
        str: JSON object with:
            - scan_path (str): Scanned folder path
            - file_count (int): Number of files scanned
            - warning_count (int): Number of issues found
            - pass (bool): True if no warnings
            - results (list): Per-file quality data
            - warnings (list): Issues found with filename, type, message
    """
    if not os.path.isdir(params.path):
        return json.dumps({"error": f"Folder not found: {params.path}"})

    results = scan_folder(params.path, recursive=params.recursive)

    if not results:
        return json.dumps({
            "scan_path": params.path,
            "file_count": 0,
            "warning_count": 0,
            "pass": True,
            "results": [],
            "warnings": [],
        })

    warnings = generate_warnings(
        results,
        min_width=params.min_width,
        min_height=params.min_height,
        min_jpeg_quality_avg=params.min_jpeg_quality_avg,
    )

    payload = {
        "scan_path": params.path,
        "file_count": len(results),
        "warning_count": len(warnings),
        "pass": len(warnings) == 0,
        "results": results,
        "warnings": warnings,
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)


# ── Entry point ──────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
