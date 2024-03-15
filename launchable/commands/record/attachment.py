from typing import Optional

import click

from ...utils.launchable_client import LaunchableClient
from ..helper import require_session


@click.command()
@click.option(
    '--session',
    'session',
    help='Test session ID',
    type=str,
)
@click.argument('attachments', nargs=-1)  # type=click.Path(exists=True)
@click.pass_context
def attachment(
        context: click.core.Context,
        attachments,
        session: Optional[str] = None
):
    client = LaunchableClient(app=context.obj)
    try:
        session = require_session(session)

        for a in attachments:
            click.echo("Sending {}".format(a))
            with open(a, mode='rb') as f:
                res = client.request(
                    "post", "{}/attachment".format(session), compress=True, payload=f,
                    additional_headers={"Content-Disposition": "attachment;filename=\"{}\"".format(a)})
                res.raise_for_status()
    except Exception as e:
        client.print_exception_and_recover(e)
