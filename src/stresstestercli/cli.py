import asyncio
import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .caller import review_batch
from .models import CodeReview

app = typer.Typer()


def make_table(results):
    t = Table("File", "Verdict", "Score", "Top Issue")
    emoji = {"pass": "[green]✓", "warn": "[yellow]⚠", "fail": "[red]✗"}

    for fname, r in results:
        if isinstance(r, Exception):
            t.add_row(fname, "[red]error", "-", str(r))
        else:
            t.add_row(
                fname,
                emoji.get(r.verdict, r.verdict),
                str(r.score),
                r.issues[0] if r.issues else "-",
            )
    return t


@app.command()
def review(
    path: Path = typer.Argument(...),
    concurrency: int = typer.Option(5, "--concurrency"),
    output_json: bool = typer.Option(
        False,
        "--output-json",
        help="Write results to review_results.json",
    ),
):
    files = list(path.glob("**/*.py"))
    snippets = [f.read_text(encoding="utf-8")[:2000] for f in files]
    results = asyncio.run(review_batch(snippets, concurrency))
    pairs = list(zip([str(f) for f in files], results))

    Console().print(make_table(pairs))

    if output_json:
        payload = [
            {
                "file": fname,
                "result": (
                    r.model_dump()
                    if isinstance(r, CodeReview)
                    else {"error": str(r)}
                ),
            }
            for fname, r in pairs
        ]
        Path("review_results.json").write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )


def main():
    app()