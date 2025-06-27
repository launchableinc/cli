from typing import Annotated, List, Optional

import typer

from ...utils.launchable_client import LaunchableClient
from ..helper import require_session

app = typer.Typer(name="attachment", help="Record attachment information")


@app.callback(invoke_without_command=True)
def attachment(
    ctx: typer.Context,
    attachments: List[str],
    session: Annotated[Optional[str], typer.Option(
        help="Test session ID"
    )] = None,
):
    app = ctx.obj
    client = LaunchableClient(app=app)
    try:
        session = require_session(session)

        for a in attachments:
            typer.echo("Sending {}".format(a))
            with open(a, mode='rb') as f:
                res = client.request(
                    "post", "{}/attachment".format(session), compress=True, payload=f,
                    additional_headers={"Content-Disposition": "attachment;filename=\"{}\"".format(a)})
                res.raise_for_status()
    except Exception as e:
        client.print_exception_and_recover(e)
