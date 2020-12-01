import click
import os


@click.command(help="Subsetting tests")
@click.argument('test_names', required=True, nargs=-1)
@click.option(
    '--input',
    'input',
    help='test type',
    required=False,
    type=str,
    metavar='INPUT'
)
def test(test_names, input):
    for name in test_names:
        print(os.path.relpath(name))
    # Todo: send test names to an inference API

    # Todo: receive subset response, then output them to stdout
