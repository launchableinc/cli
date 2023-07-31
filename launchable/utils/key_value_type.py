from typing import List, Tuple


def normalize_key_value_types(kv_types_raw: List[str]) -> List[Tuple[str, str]]:
    kvs = []
    for kv in kv_types_raw:
        if isinstance(kv, str):
            k, v = kv.replace("(", "").replace(")", "").replace("'", "").split(",")
            kvs.append((k.strip(), v.strip()))

    return kvs
