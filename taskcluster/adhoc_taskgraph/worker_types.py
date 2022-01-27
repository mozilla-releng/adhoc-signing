# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from taskgraph.transforms.task import payload_builder
from taskgraph.util import path as mozpath
from taskgraph.util.schema import taskref_or_string, resolve_keyed_by
from voluptuous import Any, Optional, Required


@payload_builder(
    "scriptworker-signing",
    schema={
        # the maximum time to run, in seconds
        Required("max-run-time"): int,
        Required("signing-type"): str,
        # list of artifact URLs for the artifacts that should be signed
        Required("upstream-artifacts"): [
            {
                # taskId of the task with the artifact
                Required("taskId"): taskref_or_string,
                # type of signing task (for CoT)
                Required("taskType"): str,
                # Paths to the artifacts to sign
                Required("paths"): [str],
                # Signing formats to use on each of the paths
                Required("formats"): [str],
            }
        ],
        # behavior for mac iscript
        Optional("behavior"): Any(
            # Adhoc signing doesn't have enough contention to warrant
            # splitting this into part 1 & part 3
            "mac_notarize",
            "mac_notarize_vpn",
        ),
        Optional("product"): str,
        Optional("entitlements-url"): str,
        Optional("nativemessaging-entitlements-url"): str,
        Optional("loginitems-entitlements-url"): str,
        Optional("provisioning-profile-url"): str,
    },
)
def build_scriptworker_signing_payload(config, task, task_def):
    worker = task["worker"]

    task_def["tags"]["worker-implementation"] = "scriptworker"

    task_def["payload"] = {
        "maxRunTime": worker["max-run-time"],
        "upstreamArtifacts": worker["upstream-artifacts"],
    }

    for key in (
        "behavior",
        "product",
        "entitlements-url",
        "provisioning-profile-url",
        "loginitems-entitlements-url",
        "nativemessaging-entitlements-url",
        "provisioning-profile-url",
    ):
        if worker.get(key):
            task_def["payload"][key] = worker[key]

    formats = set()
    for artifacts in worker["upstream-artifacts"]:
        formats.update(artifacts["formats"])
        for path in artifacts["paths"]:
            if not path.startswith("public/"):
                dirname = mozpath.dirname(path)
                scope = f"queue:get-artifact:{dirname}/*"
                if scope not in task_def.setdefault("scopes", []):
                    task_def["scopes"].append(scope)

    resolve_keyed_by(
        config.graph_config["scriptworker"],
        "scope-prefix",
        item_name="scriptworker.scope-prefix",
        product=worker.get("product", ""),
    )
    scope_prefix = config.graph_config["scriptworker"]["scope-prefix"]
    task_def["scopes"].append(
        "{}:signing:cert:{}".format(scope_prefix, worker["signing-type"])
    )


@payload_builder(
    "shipit-shipped",
    schema={
        Required("release-name"): str,
    },
)
def build_push_apk_payload(config, task, task_def):
    worker = task["worker"]

    task_def["payload"] = {
        "release_name": worker["release-name"],
    }
