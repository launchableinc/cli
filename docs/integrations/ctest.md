# CTest

```bash
# --show-only=json-v1 option outputs test list as JSON
ctest --show-only=json-v1 > test_list.json
launchable subset \
    --build <BUILD NAME> \
    --target <TARGET> \
    ctest test_list.json > launchable-subset.txt
```

```bash
# run the tests
ctest -T test --no-compress-output -R $(cat launchable-subset.txt)
```

```bash
# --show-only=json-v1 option outputs test list as JSON
ctest --show-only=json-v1 > test_list.json
launchable subset \
    --build <BUILD NAME> \
    --target <TARGET> \
    --rest launchable-remainder.txt \
    ctest test_list.json > launchable-subset.txt
```

```bash
# `-T test` option outputs test reports in CTest's XML format
ctest -T test --no-compress-output -R $(cat launchable-subset.txt)

ctest -T test --no-compress-output -R $(cat launchable-remainder.txt)
```

```bash
launchable record tests --build <BUILD NAME> ctest Testing/**/Test.xml
```
