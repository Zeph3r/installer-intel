"""
Banner module for the installer-intel CLI.

Displays a branded startup banner with ASCII art logo, tagline,
version, and GitHub attribution using Rich for colored output.

Smart detection: banner is only shown when output is a TTY,
not in CI, and --quiet was not passed.
"""

from __future__ import annotations

import os
import sys
from typing import Optional

from installer_intel import __version__


def should_show_banner(quiet: bool = False) -> bool:
    """
    Determine whether the banner should be shown.

    Banner is suppressed when:
    - quiet is True (user passed --quiet/-q)
    - stdout is not a terminal (e.g. output is piped)
    - CI environment variable is set (e.g. GitHub Actions, GitLab CI)

    Args:
        quiet: True if user passed --quiet/-q.

    Returns:
        True if the banner should be displayed, False otherwise.
    """
    if quiet:
        return False
    if not sys.stdout.isatty():
        return False
    ci = os.environ.get("CI", "").strip().lower()
    if ci in ("true", "1", "yes"):
        return False
    return True


def show_banner(version: Optional[str] = None) -> None:
    """
    Print the installer-intel CLI banner to stdout.

    Uses Rich for colored output. If version is not provided,
    uses installer_intel.__version__ (single source of truth).

    Args:
        version: Optional version string. If None, uses installer_intel.__version__.
    """
    from rich.console import Console
    from rich.style import Style

    if version is None:
        version = __version__

    console = Console()

    # Clean Minimal ASCII art logo (block characters)
    logo_lines = [
        "",
        "",
        "▄▄ ▄▄  ▄▄  ▄▄▄▄ ▄▄▄▄▄▄ ▄▄▄  ▄▄    ▄▄    ▄▄▄▄▄ ▄▄▄▄        ▄▄ ▄▄  ▄▄ ▄▄▄▄▄▄ ▄▄▄▄▄ ▄▄    ",
        "██ ███▄██ ███▄▄   ██  ██▀██ ██    ██    ██▄▄  ██▄█▄   ▄▄▄ ██ ███▄██   ██   ██▄▄  ██    ",
        "██ ██ ▀██ ▄▄██▀   ██  ██▀██ ██▄▄▄ ██▄▄▄ ██▄▄▄ ██ ██       ██ ██ ▀██   ██   ██▄▄▄ ██▄▄▄ ",
        "",
        "",
    ]

    # Banner text: cyan / bright blue
    banner_style = Style(color="cyan", bold=False)
    for line in logo_lines:
        console.print(line, style=banner_style)

    # Tagline: white, dim
    tagline = "Package Intelligence for Windows Installers"
    console.print(tagline, style=Style(color="white", dim=True))
    console.print()

    # Version and GitHub: dim gray
    dim_gray = Style(dim=True)
    console.print(f"  v{version}", style=dim_gray)
    console.print("  @Zeph3r on GitHub", style=dim_gray)
    console.print("  https://github.com/Zeph3r/installer-intel", style=dim_gray)
    console.print()
