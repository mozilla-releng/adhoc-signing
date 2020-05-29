# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by

transforms = TransformSequence()


@transforms.add
def make_task_description(config, jobs):
    for job in jobs:
        if not (
            config.params.get('version')
            and config.params.get('adhoc_name')
            and config.params.get('build_number')
        ):
            continue
        primary_dep = job.pop("primary-dependency")
        attributes = primary_dep.attributes.copy()
        if attributes["manifest"]["manifest_name"] != config.params["adhoc_name"]:
            continue
        attributes.update(job.get("attributes", {}))
        job["attributes"] = attributes
        job["label"] = "{}-{}".format(config.kind, config.params["adhoc_name"])
        resolve_keyed_by(
            job, 'scopes', item_name=job['name'],
            **{'level': config.params["level"]}
        )

        job['worker']['release-name'] = '{adhoc_name}-{version}-build{build_number}'.format(
            adhoc_name=config.params['adhoc_name'],
            version=config.params['version'],
            build_number=config.params['build_number']
        )

        yield job
