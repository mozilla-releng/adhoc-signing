# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

from six import text_type

from voluptuous import Required

from taskgraph.util.schema import taskref_or_string
from taskgraph.util import path as mozpath
from taskgraph.transforms.fetch import fetch_builder


@fetch_builder('bmo-attachment', schema={
    # The URL to download.
    Required('attachment-id'): text_type,

    # The SHA-256 of the downloaded content.
    Required('sha256'): text_type,

    # Size of the downloaded entity, in bytes.
    Required('size'): int,

    # The name to give to the generated artifact.
    Required('artifact-name'): text_type,

})
def create_fetch_url_task(config, name, fetch):

    artifact_name = fetch['artifact-name']

    workdir = '/builds/worker'

    # Arguments that matter to the cache digest
    args = [
        'bmo-attachment',
        '--sha256', fetch['sha256'],
        '--size', '%d' % fetch['size'],
        '--name', artifact_name,
        fetch['attachment-id']
    ]

    cmd = [
        'bash',
        '-c',
        'cd {} && '
        '/usr/bin/python3 {} {}'.format(
            workdir, '/builds/worker/bin/fetch-bmo.py'
        )
    ] + args

    return {
        'command': cmd,
        'artifact_name': artifact_name,
        'digest_data': ['bmo-attachment'] + args
    }
