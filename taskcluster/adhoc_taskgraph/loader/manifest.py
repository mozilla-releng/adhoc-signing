# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

import copy

from ..signing_manifest import get_manifest


def loader(kind, path, config, params, loaded_tasks):
    """
    Create tasks for each manifest.

    Optional ``job-template`` kind configuration value, if specified, will be
    used to pass configuration down to the specified transforms used.
    """
    job_template = config.get("job-template")

    for manifest in get_manifest().values():
        job = {"manifest": manifest}
        if job_template:
            job.update(copy.deepcopy(job_template))

        yield job
