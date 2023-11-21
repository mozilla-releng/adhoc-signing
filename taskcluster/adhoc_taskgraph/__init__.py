# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from importlib import import_module
from taskgraph.util import schema


def register(graph_config):
    """
    Import all modules that are siblings of this one, triggering decorators in
    the process.
    """
    _import_modules([
        "routes",
        "parameters",
        "release_promotion",
        "signing_manifest",
        "target",
        "worker_types",
        "fetches",
    ])


def _import_modules(modules):
    for module in modules:
        import_module(f".{module}", package=__name__)

schema.EXCEPTED_SCHEMA_IDENTIFIERS.extend(
    [
        "provisioning-profile-config",
    ]
)
