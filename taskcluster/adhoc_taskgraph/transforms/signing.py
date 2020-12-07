# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Create signing tasks.
"""

from __future__ import absolute_import, print_function, unicode_literals

from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by


transforms = TransformSequence()


@transforms.add
def define_signing_flags(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        # Current kind will be prepended later in the transform chain.
        task["name"] = _get_dependent_job_name_without_its_kind(dep)
        attributes = dep.attributes.copy()
        if task.get("attributes"):
            attributes.update(task["attributes"])
        task["attributes"] = attributes
        task["attributes"]["signed"] = True
        if "run_on_tasks_for" in task["attributes"]:
            task.setdefault("run-on-tasks-for", task["attributes"]["run_on_tasks_for"])

        # XXX: hack alert, we're taking a list and turning into a single item
        format_ = "macapp" if "macapp" in task["attributes"]["manifest"]["signing-formats"] else ""
        for key in ("worker-type", "worker.signing-type"):
            resolve_keyed_by(
                task,
                key,
                item_name=task["name"],
                level=config.params["level"],
                format=format_,
            )
        yield task


@transforms.add
def build_signing_task(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        task["dependencies"] = {"fetch": dep.label}
        artifact_prefix = task["attributes"].get("artifact_prefix", "public").rstrip('/')
        if not artifact_prefix.startswith("public"):
            scopes = task.setdefault('scopes', [])
            scopes.append(
                "queue:get-artifact:{}/*".format(artifact_prefix)
            )
        manifest_name = dep.label.replace("fetch-", "")
        manifest = dep.attributes['manifest']
        task["worker"]["upstream-artifacts"] = [
            {
                "taskId": {"task-reference": "<fetch>"},
                "taskType": "build",
                "paths": [dep.attributes['fetch-artifact']],
                "formats": manifest["signing-formats"],
            }
        ]
        if "mac-behavior" in manifest:
            task["worker"]["mac-behavior"] = manifest["mac-behavior"]
        if "mac-entitlements-url" in manifest:
            task["worker"]["entitlements-url"] = manifest["mac-entitlements-url"]
        if "product" in manifest:
            task["worker"]["product"] = manifest["product"]
        task.setdefault("label", "{}-{}".format(config.kind, manifest_name))
        task.setdefault("extra", {})["manifest-name"] = manifest_name
        del task["primary-dependency"]
        yield task


def _get_dependent_job_name_without_its_kind(dependent_job):
    return dependent_job.label[len(dependent_job.kind) + 1:]
