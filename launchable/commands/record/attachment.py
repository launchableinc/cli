import click

from ...utils.launchable_client import LaunchableClient
from ...utils.session import validate_session_format


@click.command()
@click.option(
    '--session',
    'session',
    help='In the format builds/<build-name>/test_sessions/<test-session-id>',
    type=str,
    required=True,
)
@click.argument('attachments', nargs=-1)  # type=click.Path(exists=True)
@click.pass_context
def attachment(
        context: click.core.Context,
        attachments,
        session: str
):
    client = LaunchableClient(app=context.obj)
    try:
        validate_session_format(session)

        for a in attachments:
            click.echo("Sending {}".format(a))
            with open(a, mode='rb') as f:
                res = client.request(
                    "post", "{}/attachment".format(session), compress=True, payload=f,
                    additional_headers={"Content-Disposition": "attachment;filename=\"{}\"".format(a)})
                res.raise_for_status()
    except Exception as e:
        client.print_exception_and_recover(e)
