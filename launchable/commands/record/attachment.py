import os
from typing import Optional

import click

from ...utils.env_keys import REPORT_ERROR_KEY
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
    try:
        session = require_session(session)

        client = LaunchableClient(app=context.obj)
        for a in attachments:
            click.echo("Sending {}".format(a))
            with open(a, mode='rb') as f:
                res = client.request(
                    "post", "{}/attachment".format(session), compress=True, payload=f,
                    additional_headers={"Content-Disposition": "attachment;filename=\"{}\"".format(a)})
                res.raise_for_status()
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e)
