from typing import List, Sequence, Tuple


def normalize_flavors(flavors_raw: List[str]) -> List[Tuple[str, str]]:
    """Normalize flavor list, because the type of the flavor list specified in the command line flags differs depending on the version of the click.

    TODO: handle extraction of flavor tuple to dict in better way for >=click8.0 that returns tuple of tuples as tuple of str
    E.G.
        <click8.0:
            `launchable record session --build aaa --flavor os=ubuntu --flavor python=3.5` is parsed as build=aaa, flavor=(("os", "ubuntu"), ("python", "3.5"))
        >=click8.0:
            `launchable record session --build aaa --flavor os=ubuntu --flavor python=3.8` is parsed as build=aaa, flavor=("('os', 'ubuntu')", "('python', '3.8')")
    """
    flavors = []
    for f in flavors_raw:
        if isinstance(f, str):
            k, v = f.replace("(", "").replace(
                ")", "").replace("'", "").split(",")
            flavors.append((k.strip(), v.strip()))
        elif isinstance(f, Sequence):
            flavors.append((f[0], f[1]))

    return flavors
