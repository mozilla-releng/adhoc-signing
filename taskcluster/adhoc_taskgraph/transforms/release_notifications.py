# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Add notifications via taskcluster-notify for release tasks
"""


from taskgraph.transforms.base import TransformSequence
from taskgraph.util.keyed_by import evaluate_keyed_by
from taskgraph.util.schema import resolve_keyed_by


transforms = TransformSequence()


@transforms.add
def add_notifications(config, tasks):
    shipping_phase = config.params.get("shipping_phase")
    if not all([shipping_phase]):
        return

    for task in tasks:
        if "primary-dependency" in task:
            dep = task["primary-dependency"]
            attributes = dep.attributes.copy()
            if task.get("attributes"):
                attributes.update(task["attributes"])
            task["attributes"] = attributes
            task.setdefault("dependencies", {}).update({"signing": dep.label})
        if task.get("attributes", {}).get("shipping-phase") != shipping_phase:
            continue

        emails = config.graph_config['notify']['email']
        format_kwargs = dict(
            config=config.__dict__,
            label=task["label"],
        )
        notifications = task.pop('notifications')
        subject = notifications['subject'].format(**format_kwargs)
        message = notifications['message'].format(**format_kwargs)

        # We only send mail on success to avoid messages like 'blah is in the
        # candidates dir' when cancelling graphs, dummy task failure, etc
        task.setdefault('routes', []).extend(
            [f'notify.email.{email}.on-completed' for email in emails]
        )

        task.setdefault('extra', {}).update(
            {
               'notify': {
                   'email': {
                        'subject': subject,
                    }
                }
            }
        )
        if message:
            task['extra']['notify']['email']['content'] = message

        yield task
