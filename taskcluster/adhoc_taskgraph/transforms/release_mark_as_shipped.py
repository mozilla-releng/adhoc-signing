# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by

transforms = TransformSequence()


@transforms.add
def make_task_description(config, tasks):
    for task in tasks:
        if not (
            config.params.get('version')
            and config.params.get('adhoc_name')
            and config.params.get('build_number')
        ):
            continue
        primary_dep = task.pop("primary-dependency")
        attributes = primary_dep.attributes.copy()
        if attributes["manifest"]["manifest_name"] != config.params["adhoc_name"]:
            continue
        attributes.update(task.get("attributes", {}))
        task["attributes"] = attributes
        task["label"] = "{}-{}".format(config.kind, config.params["adhoc_name"])
        resolve_keyed_by(
            task, 'scopes', item_name=task['name'],
            **{'level': config.params["level"]}
        )

        task['worker']['release-name'] = '{adhoc_name}-{version}-build{build_number}'.format(
            adhoc_name=config.params['adhoc_name'],
            version=config.params['version'],
            build_number=config.params['build_number']
        )

        yield task
