# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

FROM debian:trixie-20260623@sha256:d07d1b51c39f51188e60be9b64e6bf769fa94e187f092bc32b91305cfa34ba5a

### Add worker user and setup its workspace.
RUN mkdir -p /builds && \
    groupadd -g 1000 worker && \
    useradd -u 1000 -g 1000 -d /builds/worker -s /bin/bash -m worker && \
    mkdir -p /builds/worker/workspace && \
    chown -R worker:worker /builds

# Declare default working folder
WORKDIR /builds/worker

RUN apt-get update && \
    apt-get install -y --force-yes --no-install-recommends \
      gnupg \
      bzip2 \
      git \
      python3-requests \
      unzip

# %include-run-task

COPY fetch-bmo.py /usr/local/bin/fetch-bmo.py
RUN chmod a+x /usr/local/bin/fetch-bmo.py

ENV SHELL=/bin/bash \
    HOME=/builds/worker \
    PATH=/builds/worker/.local/bin:$PATH


VOLUME /builds/worker/checkouts
VOLUME /builds/worker/.cache


# run-task expects to run as root
USER root
