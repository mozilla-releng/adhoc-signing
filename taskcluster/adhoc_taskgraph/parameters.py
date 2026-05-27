# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from typing import Literal, Optional

from taskgraph.parameters import extend_parameters_schema
from taskgraph.util.schema import Schema


adhoc_schema = Schema.from_dict(
    {
        "shipping_phase": Optional[Literal["build", "promote"]],
        "adhoc_name": Optional[str],
    },
    kw_only=True,
)

extend_parameters_schema(adhoc_schema)
