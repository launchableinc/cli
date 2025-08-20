import typer

from .subsets import app as subsets_app

app = typer.Typer()

app.add_typer(subsets_app, name="subsets")
