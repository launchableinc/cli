import typer

from . import attachment, build, commit, session, tests

app = typer.Typer(name="record", help="Record test results, builds, commits, and sessions")

app.add_typer(build.app, name="build")
app.add_typer(commit.app, name="commit")
app.add_typer(tests.app, name="tests")
# for backward compatibility
app.add_typer(tests.app, name="test")
app.add_typer(session.app, name="session")
app.add_typer(attachment.app, name="attachment")
