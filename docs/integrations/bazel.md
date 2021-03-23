# Bazel

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    bazel > launchable-subset.txt
```

```bash
bazel test $(cat launchable-subset.txt)
```

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    --rest launchable-remainder.txt \
    bazel > launchable-subset.txt
```

```bash
bazel test $(cat launchable-subset.txt)

bazel test $(cat launchable-remainder.txt)
```

```bash
launchable record tests --build <BUILD NAME> bazel .
```
