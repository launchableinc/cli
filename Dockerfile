FROM python:3.11-slim

# Install Java runtime
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir wheel
RUN pip install --no-cache-dir launchable

RUN useradd -m launchable
USER launchable

# ENTRYPOINT, as opposed to CMD, ensure that user-provided additional options get passed to launchable,
# and eliminate the need for users to duplicate 'launchable' in their command line.
ENTRYPOINT ["launchable"]
