from typing import Annotated, List

import typer

from ...utils.launchable_client import LaunchableClient
from ..helper import get_session_id

app = typer.Typer(name="attachment", help="Record attachment information")


@app.callback(invoke_without_command=True)
def attachment(
    ctx: typer.Context,
    session: Annotated[str, typer.Option(
        "--session",
        help="test session name"
    )],
    attachments: Annotated[List[str], typer.Argument(
        help="Attachment files to upload"
    )],
    build: Annotated[str | None, typer.Option(
        "--build",
        help="build name"
    )] = None,
    no_build: Annotated[bool, typer.Option(
        "--no-build",
        help="If you want to only send test reports, please use this option"
    )] = False,
):
    app = ctx.obj
    client = LaunchableClient(app=app)
    try:
        session_id = get_session_id(session, build, no_build, client)

        for a in attachments:
            typer.echo(f"Sending {a}")
            with open(a, mode='rb') as f:
                res = client.request(
                    "post", f"{session_id}/attachment", compress=True, payload=f,
                    additional_headers={"Content-Disposition": f"attachment;filename=\"{a}\""})
                res.raise_for_status()
    except Exception as e:
        client.print_exception_and_recover(e)
