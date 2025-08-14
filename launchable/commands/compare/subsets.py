import click
from tabulate import tabulate


@click.command()
@click.argument('file_before', type=click.Path(exists=True))
@click.argument('file_after', type=click.Path(exists=True))
def subsets(file_before, file_after):
    """
    Compare two subset files and display changes in test order positions.
    """

    # Read files and map test paths to their indices
    with open(file_before, 'r') as f:
        before_tests = f.read().splitlines()
    before_index_map = {test: idx for idx, test in enumerate(before_tests)}

    with open(file_after, 'r') as f:
        after_tests = f.read().splitlines()
    after_index_map = {test: idx for idx, test in enumerate(after_tests)}

    changes = []
    # Calculate order difference and add each test in file_after to changes
    for after_idx, test in enumerate(after_tests):
        if test in before_index_map:
            before_idx = before_index_map[test]
            order_diff = after_idx - before_idx
            changes.append((test, before_idx + 1, after_idx + 1, order_diff))
        else:
            changes.append((test, '-', after_idx + 1, 'NEW'))

    # Add all deleted tests to changes
    for before_idx, test in enumerate(before_tests):
        if test not in after_index_map:
            changes.append((test, before_idx + 1, '-', 'DELETED'))

    # Sort changes by the absolute value of order change
    changes.sort(key=lambda x: (abs(x[3]) if isinstance(x[3], int) else float('inf')), reverse=True)

    # Display results in a tabular format
    headers = ["Before", "After", "Order Change", "Test Path"]
    rows = [
        (order_before, order_after, f"{order_change:+}" if isinstance(order_change, int) else order_change, test)
        for test, order_before, order_after, order_change in changes
    ]
    click.echo(tabulate(rows, headers=headers, tablefmt="github"))
