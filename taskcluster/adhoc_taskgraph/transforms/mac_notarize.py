# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Create signing tasks.
"""
from taskgraph.transforms.base import TransformSequence

transforms = TransformSequence()


@transforms.add
def build_notarize_task(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        if not dep.attributes["manifest"].get("signingscript-notarization"):
            continue
        task["dependencies"] = {"release-signing": dep.label}
        artifact_prefix = (
            task["attributes"].get("artifact_prefix", "public").rstrip("/")
        )
        if not artifact_prefix.startswith("public"):
            scopes = task.setdefault("scopes", [])
            scopes.append(f"queue:get-artifact:{artifact_prefix}/*")
        manifest = dep.attributes["manifest"]
        task["attributes"]["manifest"] = manifest
        manifest_name = manifest["manifest_name"]

        fetch_path = dep.attributes["fetch-artifact"]
        if manifest["artifact-name"].endswith(".dmg") and manifest["mac-behavior"] in (
            "mac_sign",
            "mac_sign_hardened",
            "mac_sign_and_pkg_hardened",
        ):
            # mac_sign behavior produces a tar file only
            fetch_path = fetch_path.replace(".dmg", ".tar.gz")

        task["worker"]["upstream-artifacts"] = [
            {
                "taskId": {"task-reference": "<release-signing>"},
                "taskType": "signing",
                "paths": [fetch_path],
                "formats": ["apple_notarization"],
            }
        ]
        task["worker"]["product"] = manifest["product"]

        task.setdefault("label", f"{config.kind}-{manifest_name}")
        task.setdefault("extra", {})["manifest-name"] = manifest_name

        del task["primary-dependency"]
        yield task
