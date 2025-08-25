import typer

from . import subset

app = typer.Typer(name="inspect", help="Inspect test and subset data")

app.add_typer(subset.app, name="subset")
