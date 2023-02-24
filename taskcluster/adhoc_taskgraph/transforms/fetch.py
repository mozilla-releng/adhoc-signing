# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from taskgraph.transforms.base import (
    TransformSequence,
)

transforms = TransformSequence()


@transforms.add
def from_manifests(config, tasks):
    for task in tasks:
        manifest = task.pop('manifest')
        task['name'] = manifest['manifest_name']
        fetch = task.setdefault("fetch", {})
        fetch['type'] = manifest["fetch"].get('type', 'static-url')
        if fetch['type'] == 'static-url':
            fetch["url"] = manifest["fetch"]["url"]
            if manifest['fetch'].get('gpg-signature'):
                fetch['gpg-signature'] = manifest['fetch'].get('gpg-signature')
        elif fetch['type'] == 'bmo-attachment':
            fetch['attachment-id'] = str(manifest["fetch"]['attachment-id'])
        fetch["sha256"] = manifest["sha256"]
        fetch["size"] = manifest["filesize"]

        for k in ("artifact-name", ):
            if manifest.get(k):
                fetch[k] = manifest[k]
        task.setdefault('attributes', {})['manifest'] = manifest
        if manifest["private-artifact"]:
            task["artifact-prefix"] = config.graph_config["private-artifact-prefix"]
        else:
            task["artifact-prefix"] = "public/build"
        yield task
