# Robot

```bash
robot --dryrun -o dryrun.xml
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  robot dryrun.xml > launchable-subset.txt
```

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

```bash
robot --dryrun -o dryrun.xml
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-rest.txt \
  robot dryrun.xml > launchable-subset.txt
```

```bash
bundle exec rails test $(cat launchable-subset.txt)

bundle exec rails test $(cat launchable-rest.txt)
```


```bash
# run the tests however you normally do
robot .

launchable record tests --build <BUILD NAME> robot output.xml
```
