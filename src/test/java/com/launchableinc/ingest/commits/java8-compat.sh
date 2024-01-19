#!/bin/bash -ex
# Make sure the java bits we ship are Java8 compatible

# report the full dump to assist investigation
# the first number printed is the Java class file version. We want to support Java8 = 52.0, so no newer version allowed
# - META-INF/versions/... is a mechanism known as multi-release jar, so we can ignore newer classes in there
# - module-info.class is a metadata for Java module system (Java9+) that earlier JVM will ignore
java -jar external/maven/v1/https/repo1.maven.org/maven2/org/jvnet/animal-sniffer/*/animal-sniffer-*.jar src/main/java/com/launchableinc/ingest/commits/exe_deploy.jar \
  | grep -v META-INF/versions \
  | grep -v module-info.class \
  | tee classes

# report by versions
cat classes | cut -f1 -d' ' | sort | uniq -c | tee versions

cat versions | grep -A100 -F '52.0' | tee newer
if ((`cat newer | wc -l` > 1)); then
  echo "Class file versions newer than 52.0 not allowed to support Java 8"
  exit 1
fi
