# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

from taskgraph.transforms.base import (
    TransformSequence,
)

transforms = TransformSequence()


@transforms.add
def from_manifests(config, jobs):
    for job in jobs:
        manifest = job.pop('manifest')
        job['name'] = manifest['manifest_name']
        fetch = job.setdefault("fetch", {})
        fetch['type'] = manifest["fetch"].get('type', 'static-url')
        if fetch['type'] == 'static-url':
            fetch["url"] = manifest["fetch"]["url"]
            if manifest['fetch'].get('gpg-signature'):
                fetch['gpg-signature'] = manifest['fetch'].get('gpg-signature')
        elif fetch['type'] == 'bmo-attachment':
            fetch['attachment-id'] = unicode(manifest["fetch"]['attachment-id'])
        fetch["sha256"] = manifest["sha256"]
        fetch["size"] = manifest["filesize"]

        for k in ("artifact-name", ):
            if manifest.get(k):
                fetch[k] = manifest[k]
        job.setdefault('attributes', {})['manifest'] = manifest
        if manifest["private-artifact"]:
            job["artifact-prefix"] = config.graph_config["private-artifact-prefix"]
        else:
            job["artifact-prefix"] = "public/build"
        yield job
