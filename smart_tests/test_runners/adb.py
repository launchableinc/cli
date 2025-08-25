import re

from . import smart_tests


@smart_tests.subset
def subset(client):
    prev_cls_name = None
    pattern = re.compile(r'^INSTRUMENTATION_STATUS: class=(.+)$')
    for line in client.stdin():
        match = pattern.match(line)
        if match:
            cls_name = match.group(1)
            if prev_cls_name != cls_name:
                client.test_path([{"type": "class", "name": cls_name}])
                prev_cls_name = cls_name

    client.separator = ','

    client.run()


record_tests = smart_tests.CommonRecordTestImpls(__name__).report_files()
