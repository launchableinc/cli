import typer

from . import subset, tests

app = typer.Typer(name="inspect", help="Inspect test and subset data")

app.add_typer(subset.app, name="subset")
app.add_typer(tests.app, name="tests")
