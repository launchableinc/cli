import typer

from . import attachment, build, commit, session

app = typer.Typer(name="record", help="Record test results, builds, commits, and sessions")

app.add_typer(build.app, name="build")
app.add_typer(commit.app, name="commit")
# NestedCommand version will be added in __main__.py
# Remove old tests command registration - it will be replaced by NestedCommand in __main__.py
app.add_typer(session.app, name="session")
app.add_typer(attachment.app, name="attachment")
