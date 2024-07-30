FROM eclipse-temurin:8

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  python3-setuptools \
  pipx \
  && apt-get -y clean \
  && rm -rf /var/lib/apt/lists/*

ENV PATH="$PATH:/root/.local/bin"

RUN pipx install wheel
RUN pipx install launchable
