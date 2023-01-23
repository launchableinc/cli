from typing import List, Sequence, Tuple


def normalize_key_value_types(kv_types_raw: List[str]) -> List[Tuple[str, str]]:
    """Normalize flavor list, because the type of the flavor list specified in the command line flags differs depending
    on the version of the click.

    TODO: handle extraction of flavor tuple to dict in better way for >=click8.0 that returns tuple of tuples as tuple
    of str
    E.G.
        <click8.0:
            `launchable record session --build aaa --flavor os=ubuntu --flavor python=3.5`
            is parsed as build=aaa, flavor=(("os", "ubuntu"), ("python", "3.5"))
        >=click8.0:
            `launchable record session --build aaa --flavor os=ubuntu --flavor python=3.8`
            is parsed as build=aaa, flavor=("('os', 'ubuntu')", "('python', '3.8')")
    """
    kvs = []
    for kv in kv_types_raw:
        if isinstance(kv, str):
            k, v = kv.replace("(", "").replace(")", "").replace("'", "").split(",")
            kvs.append((k.strip(), v.strip()))
        elif isinstance(kv, Sequence):
            kvs.append((kv[0], kv[1]))

    return kvs
