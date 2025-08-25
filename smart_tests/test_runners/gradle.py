import os
from typing import Annotated, List

import typer

from smart_tests.utils.java import junit5_nested_class_path_builder

from ..utils.file_name_pattern import jvm_test_pattern
from . import smart_tests


@smart_tests.subset
def subset(
    client,
    source_roots: Annotated[List[str] | None, typer.Argument(
        help="Source root directories to scan for tests"
    )] = None,
    bare: Annotated[bool, typer.Option(
        "--bare",
        help="outputs class names alone"
    )] = False,
):
    def file2test(f: str):
        if jvm_test_pattern.match(f):
            f = f[:f.rindex('.')]   # remove extension
            # directory -> package name conversion
            cls_name = f.replace(os.path.sep, '.')
            return [{"type": "class", "name": cls_name}]
        else:
            return None

    # Handle None source_roots - convert to empty list
    if source_roots is None:
        source_roots = []

    if client.is_get_tests_from_previous_sessions:
        if len(source_roots) != 0:
            typer.secho(
                "Warning: SOURCE_ROOTS are ignored when --get-tests-from-previous-sessions is used",
                fg=typer.colors.YELLOW, err=True)
        # Always set to empty list when getting tests from previous sessions
        source_roots = []
    else:
        if len(source_roots) == 0:
            raise typer.BadParameter("Error: Missing argument 'SOURCE_ROOTS...'")

    # Only scan if we have source roots
    for root in source_roots:
        client.scan(root, '**/*', file2test)

    def exclusion_output_handler(subset_tests, rest_tests):
        if client.rest:
            with open(client.rest, "w+", encoding="utf-8") as fp:
                if not bare and len(rest_tests) == 0:
                    # This prevents the CLI output to be evaled as an empty
                    # string argument.
                    fp.write('-PdummyPlaceHolder')
                else:
                    fp.write(client.separator.join(client.formatter(t) for t in rest_tests))

        classes = [to_class_file(tp[0]['name']) for tp in rest_tests]
        if bare:
            typer.echo(','.join(classes))
        else:
            typer.echo('-PexcludeTests=' + (','.join(classes)))
    client.exclusion_output_handler = exclusion_output_handler

    if bare:
        client.formatter = lambda x: x[0]['name']
    else:
        client.formatter = lambda x: f"--tests {x[0]['name']}"
        client.separator = ' '

    client.run()


def to_class_file(class_name: str):
    return class_name.replace('.', '/') + '.class'


@smart_tests.record.tests
def record_tests(
    client,
    reports: Annotated[List[str], typer.Argument(
        help="Test report files to process"
    )],
):
    client.path_builder = junit5_nested_class_path_builder(client.path_builder)
    smart_tests.CommonRecordTestImpls.load_report_files(client=client, source_roots=reports)
