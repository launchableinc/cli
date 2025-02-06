#!/bin/bash -ex
bazel build //src/main/java/com/launchableinc/ingest/commits:exe_deploy.jar
bazel test //...
cp bazel-bin/src/main/java/com/launchableinc/ingest/commits/exe_deploy.jar launchable/jar/exe_deploy.jar

