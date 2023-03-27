# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Create signing tasks.
"""


from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by

MAC_RELEASE_ONLY_FORMATS = ["autograph_widevine", "autograph_omnija"]
transforms = TransformSequence()


@transforms.add
def define_signing_flags(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        # Current kind will be prepended later in the transform chain.
        task["name"] = _get_dependent_task_name_without_its_kind(dep)
        attributes = dep.attributes.copy()
        if task.get("attributes"):
            attributes.update(task["attributes"])
        task["attributes"] = attributes
        task["attributes"]["signed"] = True
        if "run_on_tasks_for" in task["attributes"]:
            task.setdefault("run-on-tasks-for", task["attributes"]["run_on_tasks_for"])

        # XXX: hack alert, we're taking a list and turning into a single item
        format_ = ""
        for f in ("macapp", "mac_single_file"):
            if f in task["attributes"]["manifest"]["signing-formats"]:
                format_ = f

        for key in ("worker-type", "worker.signing-type", "index.type"):
            resolve_keyed_by(
                task,
                key,
                item_name=task["name"],
                level=config.params["level"],
                format=format_,
            )
        yield task


def get_signing_cert(manifest, level):
    if level != "3":
        signing_cert = "dep-signing"
    else:
        signing_cert = manifest.get("signing-cert", "release-signing")
        assert signing_cert in ("nightly-signing", "release-signing")
    return signing_cert

def get_formats(level, manifest):
    """Given the task level, translate the formats"""
    formats = manifest["signing-formats"]
    if level != "3" and manifest.get("mac-behavior"):
        # Dep signing and mac
        formats = [f for f in formats if f not in MAC_RELEASE_ONLY_FORMATS]
    return formats

@transforms.add
def build_signing_task(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        task["dependencies"] = {"fetch": dep.label}
        artifact_prefix = (
            task["attributes"].get("artifact_prefix", "public").rstrip("/")
        )
        if not artifact_prefix.startswith("public"):
            scopes = task.setdefault("scopes", [])
            scopes.append(f"queue:get-artifact:{artifact_prefix}/*")
        manifest_name = dep.label.replace("fetch-", "")
        manifest = dep.attributes["manifest"]
        signing_cert = get_signing_cert(manifest, config.params["level"])
        upstream_artifact = {
            "taskId": {"task-reference": "<fetch>"},
            "taskType": "build",
            "paths": [dep.attributes["fetch-artifact"]],
            "formats": get_formats(config.params["level"], manifest),
        }
        if "single-file-globs" in manifest:
            if manifest.get("mac-behavior") != "mac_single_file":
                raise Exception(
                    "single-file-globs should only be specified for mac_single_file "
                    "mac-behavior tasks!"
                )
            upstream_artifact["singleFileGlobs"] = manifest["single-file-globs"]
        task["worker"]["upstream-artifacts"] = [upstream_artifact]
        # Optional keys (will be validated by worker-type schema)
        for key in ("mac-behavior", "product"):
            if key in manifest:
                task["worker"][key] = manifest[key]

        task.setdefault("label", f"{config.kind}-{manifest_name}")
        task.setdefault("extra", {})["manifest-name"] = manifest_name
        task["index"]["type"] = task["index"]["type"].format(signing_cert=signing_cert)
        task["worker"]["signing-type"] = task["worker"]["signing-type"].format(
            signing_cert=signing_cert
        )
        del task["primary-dependency"]
        yield task


def _get_dependent_task_name_without_its_kind(dependent_task):
    return dependent_task.label[len(dependent_task.kind) + 1 :]
