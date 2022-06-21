# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Build the cached_task digest to prevent rerunning tasks if the code hasn't changed.
"""

import hashlib
import json
import os
import subprocess

import taskgraph
from taskgraph.transforms.base import TransformSequence
from taskgraph.util.hash import hash_path, hash_paths
from taskgraph.util.memoize import memoize

from adhoc_taskgraph.signing_manifest import MANIFEST_DIR

transforms = TransformSequence()

BASE_DIR = os.getcwd()


@transforms.add
def add_resources(config, tasks):
    for task in tasks:
        resources = set(task.pop("resources", []))
        resources.add(
            os.path.join(MANIFEST_DIR, f"{task['extra']['manifest-name']}.yml")
        )
        resources = list(resources)
        attributes = task.setdefault("attributes", {})
        if attributes.get("resources") is not None:
            if resources and attributes["resources"] != resources:
                raise Exception(
                    f"setting {config.kind} {task.get('name')} "
                    f"task.attributes.resources to {resources}: "
                    f"it's already set to {attributes['resources']}!"
                )
        attributes["resources"] = resources
        yield task


@transforms.add
def build_cache(config, tasks):
    for task in tasks:
        if task.get("cache", True) and not taskgraph.fast:
            digest_data = []
            digest_data.append(
                json.dumps(
                    task.get("attributes", {}).get("digest-extra", {}),
                    indent=2,
                    sort_keys=True,
                )
            )
            resources = task["attributes"]["resources"]
            for resource in resources:
                path = os.path.join(BASE_DIR, resource)
                if os.path.isdir(resource):
                    digest_data.append(hash_paths(path, [""]))
                elif os.path.isfile(resource):
                    digest_data.append(hash_path(path))
                else:
                    raise Exception(f"Unknown resource {resource}")
            cache_name = task["name"].replace(":", "-")
            task["cache"] = {
                "type": f"adhoc-signing.v1.{config.kind}",
                "name": cache_name,
                "digest-data": digest_data,
            }

        yield task


@transforms.add
def set_label(config, jobs):
    """Set the job label, which the `cached_tasks` transform needs"""
    for job in jobs:
        job.setdefault("label", f"{config.kind}-{job.pop('name')}")
        yield job
