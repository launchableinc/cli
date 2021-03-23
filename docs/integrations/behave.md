# Behave

```bash
find ./features/ | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  behave > launchable-subset.txt
```

```bash
behave -i "$(cat launchable-subset.txt)"
```

```bash
find ./features/ | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  behave > launchable-subset.txt
```

```bash
behave -i "$(cat launchable-subset.txt)"

behave -i "$(cat launchable-remainder.txt)"
```

```bash
# run the tests however you normally do
behave --junit

launchable record tests --build <BUILD NAME> behave ./reports/*.xml
```
