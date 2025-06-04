FROM python:3.11-slim AS builder

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /src
COPY . .
RUN pip wheel --no-cache-dir -w /wheels .
RUN ls /wheels

FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels/*.whl /wheels/
RUN pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

# get rid of a warning that talks about pkg_resources deprecation
# see https://setuptools.pypa.io/en/latest/history.html#v67-3-0
RUN pip install setuptools==66.1.1

RUN useradd -m launchable
USER launchable

ENTRYPOINT ["launchable"]
