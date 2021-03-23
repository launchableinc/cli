# Cypress

```bash
find ./cypress/integration | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  cypress > launchable-subset.txt
```

```bash
cypress run --spec "$(cat launchable-subset.txt)" --reporter junit --reporter-options "mochaFile=report/test-output-[hash].xml"
```

```bash
find ./cypress/integration | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  cypress > launchable-subset.txt
```

```bash
cypress run --spec "$(cat launchable-subset.txt)" --reporter junit --reporter-options "mochaFile=report/test-output-[hash].xml"

cypress run --spec "$(cat launchable-remainder.txt)" --reporter junit --reporter-options "mochaFile=report/test-output-[hash].xml"
```

```bash
launchable record tests --build <BUILD NAME> cypress ./report/*.xml
```
