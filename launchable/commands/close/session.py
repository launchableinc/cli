import click


@click.command()
@click.option(
    '--session',
    'session_id',
    help='Test session ID',
    type=str,
)
def session(session_id: str):
    print(session_id)
