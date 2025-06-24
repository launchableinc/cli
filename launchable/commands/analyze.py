import re
from time import sleep

import click
from git import Repo
from tabulate import tabulate
from tqdm import trange


@click.group(invoke_without_command=True, hidden=True)
@click.pass_context
def analyze(context: click.core.Context):
    if context.invoked_subcommand is None:
        answer = click.prompt("Can start analyze this repository? [Y/n]: ")
        if answer.lower() not in ("y", "yes", ""):
            click.echo("canceled.")
            return

        click.echo("Analyzing the repository...")
        for i in trange(100):
            sleep(0.05)

        click.echo("Completed analyzing the repository!!")
        click.echo("Next:\n1) Update some files and commit.\n2) Run `launchable analyze predict` to check the prediction result.")


@analyze.command(name="predict")
def predict():
    click.echo("Predicting the next files to be modified based on the analysis...", err=True)
    sleep(3)

    list = []
    for f in get_recently_modified_files_git():
        if is_test_file(f):
            list.append(f)

    click.echo("\n".join(list))

    # copy from subset.py
    header = ["", "Candidates",
              "Estimated duration (%)", "Estimated duration (min)"]
    rows = [
        [
            "Subset",
            len(list),
            100.0,
            len(list) * 1 / 60,
        ],
        [
            "Remainder",
            0,
            0,
            0,
        ],
        [],
        [
            "Total",
            len(list),
            100.0,
            len(list) * 1 / 60,
        ],
    ]
    click.echo(tabulate(rows, header, tablefmt="github", floatfmt=".2f"), err=True)


def get_recently_modified_files_git(repo_path='.', limit=30):
    repo = Repo(repo_path)
    files = list(repo.git.diff('HEAD~{}'.format(limit), name_only=True).splitlines())
    return files


test_path_pattern = re.compile(
    r'(?i)'
    r'(?<!/)\.?(?!\.)'
    r'.*'
    r'((^|/)(test|tests|__tests__)/|'
    r'(Test|Tests?|TestCase)|'
    r'(_test|test_|\.spec|\.test))'
)

exclude_keywords = [
    '.git/',
    '.github/',
    '__pycache__/',
    '/test_utils',
    '/data/',
    '/config/',
    '/fixtures/',
    '/mock/',
    '/build/',
]


def is_test_file(path: str) -> bool:
    if any(part.startswith('.') for part in path.split('/')):
        return False
    if any(key in path for key in exclude_keywords):
        return False
    return bool(test_path_pattern.search(path))
