import click
import os
import sys
from os.path import join, relpath, normpath
import glob
from typing import Callable, Union, Optional
from ..utils.click import PERCENTAGE, DURATION
from ..utils.env_keys import REPORT_ERROR_KEY
from ..utils.http_client import LaunchableClient
from ..testpath import TestPath
from .helper import find_or_create_session
from ..utils.click import KeyValueType
from .test_path_writer import TestPathWriter
from ..engine import Optimize
# TODO: rename files and function accordingly once the PR landscape


@click.group(help="Subsetting tests")
@click.option(
    '--target',
    'target',
    help='subsetting target from 0% to 100%',
    type=PERCENTAGE,
)
@click.option(
    '--time',
    'duration',
    help='subsetting by absolute time, in seconds e.g) 300, 5m',
    type=DURATION,
)
@click.option(
    '--confidence',
    'confidence',
    help='subsetting by confidence from 0% to 100%',
    type=PERCENTAGE,
)
@click.option(
    '--session',
    'session',
    help='Test session ID',
    type=str,
)
@click.option(
    '--base',
    'base_path',
    help='(Advanced) base directory to make test names portable',
    type=click.Path(exists=True, file_okay=False),
    metavar="DIR",
)
@click.option(
    '--build',
    'build_name',
    help='build name',
    type=str,
    metavar='BUILD_NAME'
)
@click.option(
    '--rest',
    'rest',
    help='output the rest of subset',
    type=str,
)
@click.option(
    "--flavor",
    "flavor",
    help='flavors',
    cls=KeyValueType,
    multiple=True,
)
@click.option(
    "--split",
    "split",
    help='split',
    is_flag=True
)
@click.pass_context
def subset(context, target, session: Optional[str], base_path: Optional[str], build_name: Optional[str], rest: str,
           duration, flavor, confidence, split):

    def run(implType, **kwargs): # typing: implType is a subtype of Optimize
        client = implType(context=context, base_path=base_path) # typing: Optimize

        def get_payload(session_id, target, duration):
            payload = {
                "testPaths": client.test_paths,
                "session": {
                    # expecting just the last component, not the whole path
                    "id": os.path.basename(session_id)
                }
            }

            if target is not None:
                payload["target"] = target
            elif duration is not None:
                payload["goal"] = {
                    "type": "subset-by-absolute-time",
                    "duration": duration,
                }
            elif confidence is not None:
                payload["goal"] = {
                    "type": "subset-by-confidence",
                    "percentage": confidence
                }

            return payload

        """called after tests are scanned to compute the optimized order"""

        # When Error occurs, return the test name as it is passed.
        output = client.test_paths
        rests = []
        subset_id = ""

        session_id = find_or_create_session(client.context, session, build_name, flavor)

        if not session_id:
            # Session ID in --session is missing. It might be caused by Launchable API errors.
            pass
        else:
            try:
                client = LaunchableClient(
                    test_runner=context.invoked_subcommand)

                client.enumerate_tests()

                # temporarily extend the timeout because subset API response has become slow
                # TODO: remove this line when API response return respose within 60 sec
                timeout = (5, 180)
                payload = client.get_payload(session_id, target, duration)

                res = client.request(
                    "post", "subset", timeout=timeout, payload=payload, compress=True)

                res.raise_for_status()
                output = res.json()["testPaths"]
                rests = res.json()["rest"]
                subset_id = res.json()["subsettingId"]

            except Exception as e:
                if os.getenv(REPORT_ERROR_KEY):
                    raise e
                else:
                    click.echo(e, err=True)
                click.echo(click.style(
                    "Warning: the service failed to subset. Falling back to running all tests", fg='yellow'),
                    err=True)

        if len(output) == 0:
            click.echo(click.style(
                "Error: no tests found matching the path.", 'yellow'), err=True)
            return

        if split:
            click.echo("subset/{}".format(subset_id))
        else:
            # regardless of whether we managed to talk to the service
            # we produce test names
            if rest:
                if len(rests) == 0:
                    rests.append(output[0])

                client.write_file(rest, rests)

            client.print(output)

    return run
