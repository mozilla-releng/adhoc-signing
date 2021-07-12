# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


from taskgraph.target_tasks import _target_task as target_task
from taskgraph.target_tasks import standard_filter


@target_task("promote_adhoc")
def target_tasks_promote_xpi(full_task_graph, parameters, graph_config):
    """Select the set of tasks required for promoting adhoc signing."""

    def filter(task, parameters):
        if task.attributes.get('shipping-phase') not in ('build', 'promote'):
            return False
        manifest_name = task.attributes.get('manifest', {}).get('manifest_name')
        if manifest_name and manifest_name == parameters["adhoc_name"]:
            return True

    return [l for l, t in full_task_graph.tasks.items() if filter(t, parameters)]
