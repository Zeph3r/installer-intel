from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from installer_intel.analyzers import analyze_exe, analyze_msi
from installer_intel.models import InstallPlan

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


def _write_json(plan: InstallPlan, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(plan.model_dump_json(indent=2), encoding="utf-8")


def _print_summary(plan: InstallPlan) -> None:
    console.print(Panel.fit(f"[bold]installer-intel[/bold]\n{plan.input_path}", title="Analyze Result"))

    console.print(f"[bold]Type:[/bold] {plan.installer_type}  (confidence {plan.confidence:.2f})")
    console.print(f"[bold]File:[/bold] {plan.file_type}")

    if plan.metadata:
        meta_table = Table(title="Metadata", show_lines=True)
        meta_table.add_column("Key", style="bold")
        meta_table.add_column("Value")
        for k, v in plan.metadata.items():
            meta_table.add_row(str(k), "" if v is None else str(v))
        console.print(meta_table)

    if plan.install_candidates:
        t = Table(title="Install candidates", show_lines=True)
        t.add_column("Confidence", justify="right")
        t.add_column("Command")
        for c in plan.install_candidates:
            t.add_row(f"{c.confidence:.2f}", c.command)
        console.print(t)

    if plan.uninstall_candidates:
        t = Table(title="Uninstall candidates", show_lines=True)
        t.add_column("Confidence", justify="right")
        t.add_column("Command")
        for c in plan.uninstall_candidates:
            t.add_row(f"{c.confidence:.2f}", c.command)
        console.print(t)

    if plan.detection_rules:
        t = Table(title="Detection rules", show_lines=True)
        t.add_column("Confidence", justify="right")
        t.add_column("Kind")
        t.add_column("Value")
        for d in plan.detection_rules:
            t.add_row(f"{d.confidence:.2f}", d.kind, d.value)
        console.print(t)

    if plan.notes:
        console.print(Panel("\n".join(f"- {n}" for n in plan.notes), title="Notes"))


@app.command()
def analyze(
    path: Path = typer.Argument(..., help="Path to installer (.msi or .exe)"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Output JSON path (default: ./installplan.json)"),
) -> None:
    p = Path(path)
    if not p.exists():
        raise typer.BadParameter(f"File not found: {p}")

    ext = p.suffix.lower().lstrip(".")

    if ext == "msi":
        plan = analyze_msi(str(p))
    elif ext == "exe":
        plan = analyze_exe(str(p))
    else:
        raise typer.BadParameter("Unsupported file type. Provide a .msi or .exe")

    out_path = out or Path("installplan.json")
    _write_json(plan, out_path)
    _print_summary(plan)
    console.print(f"[green]Wrote:[/green] {out_path.resolve()}")


@app.command()
def schema() -> None:
    """
    Print the JSON schema for the InstallPlan model.
    """
    from installer_intel.models import InstallPlan as _InstallPlan

    console.print_json(data=_InstallPlan.model_json_schema())


if __name__ == "__main__":
    app()
