# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import copy

from ..signing_manifest import get_manifest


def loader(kind, path, config, params, loaded_tasks):
    """
    Create tasks for each manifest.

    Optional ``task-template`` kind configuration value, if specified, will be
    used to pass configuration down to the specified transforms used.
    """
    task_template = config.get("task-template")

    for manifest in get_manifest().values():
        task = {"manifest": manifest}
        if task_template:
            task.update(copy.deepcopy(task_template))

        yield task
