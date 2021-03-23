# Minitest

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  minitest test/**/*.rb > launchable-subset.txt
```

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  minitest test/**/*.rb > launchable-subset.txt
```

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

```bash
launchable record tests --build <BUILD NAME> minitest "$CIRCLE_TEST_REPORTS/reports"
```
