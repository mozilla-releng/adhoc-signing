# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from voluptuous import Required

from taskgraph.transforms.fetch import fetch_builder


@fetch_builder('bmo-attachment', schema={
    # The URL to download.
    Required('attachment-id'): str,

    # The SHA-256 of the downloaded content.
    Required('sha256'): str,

    # Size of the downloaded entity, in bytes.
    Required('size'): int,

    # The name to give to the generated artifact.
    Required('artifact-name'): str,

})
def create_fetch_url_task(config, name, fetch):

    artifact_name = fetch['artifact-name']


    # Arguments that matter to the cache digest
    args = (
        'bmo-attachment '
        '--sha256 {} '
        '--size {} '
        '--name {} '
        '{} '
        '/builds/worker/artifacts/{}'.format(
            fetch['sha256'],
            fetch['size'],
            artifact_name,
            fetch['attachment-id'],
            artifact_name
            )
    )

    cmd = [
        'bash',
        '-c',
        f'/usr/local/bin/fetch-bmo.py {args}'
    ]

    return {
        'command': cmd,
        'artifact_name': artifact_name,
        'digest_data': args,
    }
