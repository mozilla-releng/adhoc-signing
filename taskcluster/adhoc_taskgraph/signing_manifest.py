# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import glob
import os
from copy import deepcopy

from taskgraph.util import yaml
from taskgraph.util.memoize import memoize
from taskgraph.util.readonlydict import ReadOnlyDict
from taskgraph.util.schema import validate_schema
from voluptuous import Any, Optional, Required, Schema

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ROOT = os.path.join(BASE_DIR, "taskcluster", "ci")
MANIFEST_DIR = os.path.join(BASE_DIR, "signing-manifests")

SUPPORTED_SIGNING_FORMATS = (
    "autograph_gpg",
    "autograph_authenticode",
    "autograph_authenticode_stub",
    "autograph_authenticode_sha2",
    "autograph_authenticode_sha2_stub",
    "autograph_authenticode_sha2_rfc3161_stub",
    "autograph_hash_only_mar384",
    "macapp",
)

SUPPORTED_SIGNING_CERTS = (
    "dep-signing",
    "nightly-signing",
    "release-signing",
)

base_schema = Schema(
    {
        Required("bug"): int,
        Required("sha256"): str,
        Required("filesize"): int,
        Required("private-artifact"): bool,
        Required("signing-formats"): [Any(*SUPPORTED_SIGNING_FORMATS)],
        Optional("signing-cert"): Any(*SUPPORTED_SIGNING_CERTS),
        Required("requestor"): str,
        Required("reason"): str,
        Required("artifact-name"): str,
        Required("fetch"): Any(
            {
                Optional("gpg-signature"): str,
                Optional("type"): "static-url",
                Required("url"): str,
            },
            {
                Required("type"): "bmo-attachment",
                Required("attachment-id"): Any(str, int),
            },
        ),
        Required("manifest_name"): str,
        Optional("mac-behavior"): str,
        Optional("product"): str,
    }
)


def check_manifest(manifest):
    # XXX add any manifest checks we want.
    # XXX sha256 is a valid sha256?
    # XXX url is a reachable url?
    # XXX bug exists in bugzilla?
    # XXX formats are known and valid for artifact-name

    # MozillaVPN can only be signed as mac_notarize_vpn
    if manifest.get("mac-behavior", "") == "mac_notarize_vpn":
        assert len(manifest["signing-formats"]) == 1
        assert manifest["signing-formats"][0] == "macapp"
        assert manifest["product"] == "mozillavpn"


@memoize
def get_manifest():
    manifest_paths = glob.glob(os.path.join(MANIFEST_DIR, "*.yml"))
    all_manifests = {}
    for path in manifest_paths:
        rw_manifest = yaml.load_yaml(path)
        manifest_name = os.path.basename(path).replace(".yml", "")
        rw_manifest["manifest_name"] = manifest_name
        validate_schema(base_schema, deepcopy(rw_manifest), "Invalid manifest:")
        check_manifest(deepcopy(rw_manifest))
        assert manifest_name not in all_manifests
        all_manifests[manifest_name] = rw_manifest
    return ReadOnlyDict(all_manifests)
