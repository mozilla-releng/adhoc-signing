# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from taskgraph.parameters import extend_parameters_schema
from voluptuous import (
    Any,
    Optional,
    Required,
)


# Please keep this list sorted and in sync with taskcluster/docs/parameters.rst
adhoc_schema = {
    Optional('shipping_phase'): Any("build", "promote", None),
    Optional('adhoc_name'): Any(str, None),
    Optional('adhoc_revision'): Any(str, None),
}

extend_parameters_schema(adhoc_schema)
