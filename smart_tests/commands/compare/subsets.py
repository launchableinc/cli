from pathlib import Path
from typing import List, Tuple, Union

import typer
from tabulate import tabulate

app = typer.Typer()


@app.callback(invoke_without_command=True)
def subsets(
    ctx: typer.Context,
    file_before: Path = typer.Argument(None, help="First subset file to compare"),
    file_after: Path = typer.Argument(None, help="Second subset file to compare")
):
    """
    Compare two subset files and display changes in test order positions
    """
    if ctx.invoked_subcommand is None:
        if file_before is None or file_after is None:
            typer.echo("Error: Both file_before and file_after arguments are required")
            raise typer.Exit(1)

        if not file_before.exists():
            typer.echo(f"Error: File {file_before} does not exist", err=True)
            raise typer.Exit(1)

        if not file_after.exists():
            typer.echo(f"Error: File {file_after} does not exist", err=True)
            raise typer.Exit(1)

        # Read files and map test paths to their indices
        with open(file_before, 'r') as f:
            before_tests = f.read().splitlines()
        before_index_map = {test: idx for idx, test in enumerate(before_tests)}

        with open(file_after, 'r') as f:
            after_tests = f.read().splitlines()
        after_index_map = {test: idx for idx, test in enumerate(after_tests)}

        # List of tuples representing test order changes (before, after, diff, test)
        rows: List[Tuple[Union[int, str], Union[int, str], Union[int, str], str]] = []

        # Calculate order difference and add each test in file_after to changes
        for after_idx, test in enumerate(after_tests):
            if test in before_index_map:
                before_idx = before_index_map[test]
                diff = after_idx - before_idx
                rows.append((before_idx + 1, after_idx + 1, diff, test))
            else:
                rows.append(('-', after_idx + 1, 'NEW', test))

        # Add all deleted tests to changes
        for before_idx, test in enumerate(before_tests):
            if test not in after_index_map:
                rows.append((before_idx + 1, '-', 'DELETED', test))

        # Sort changes by the order diff
        rows.sort(key=lambda x: (0 if isinstance(x[2], str) else 1, x[2]))

        # Display results in a tabular format
        headers = ["Before", "After", "After - Before", "Test"]
        tabular_data = [
            (before, after, f"{diff:+}" if isinstance(diff, int) else diff, test)
            for before, after, diff, test in rows
        ]
        typer.echo(tabulate(tabular_data, headers=headers, tablefmt="github"))
