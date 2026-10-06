# Ad hoc signing agent instructions

## Reuse Gecko try artifacts for signing requests

Start from the Bugzilla, Phabricator, or Treeherder references the user provides.
If Mozilla MCP tools are available, use `mcp__moz__get_bugzilla_bug` for the bug
and `mcp__moz__get_phabricator_revision` for a referenced revision. If the user
provides a Phabricator revision but no try link, inspect the revision for its
associated Reviewbot try push. If the user provides a try push, use it as the first
candidate. Verify the artifact type, build variant, source revision, and chain of
trust against the request before using it. Check for a suitable existing artifact
before starting a local application build.

## Diagnose Gecko fetch tasks

Use Treeherder to find the fetch task for the selected try push. Follow its
Taskcluster dependency chain with the CLI until you reach the task named
`docker-image-fetch`:

```bash
TASKCLUSTER_ROOT_URL=<TC_ROOT_URL> taskcluster task def <task-id>
TASKCLUSTER_ROOT_URL=<TC_ROOT_URL> taskcluster task name <dependency-id>
```

Inspect the production fetch log with
`TASKCLUSTER_ROOT_URL=<TC_ROOT_URL> taskcluster task log <fetch-task-id>`. In Gecko
fetch tasks, `run-task-hg` prepares the worker and `fetch-content` performs the
download. A local `load-task` failure caused by a missing `run-task` executable only
shows a local runner/image mismatch; it does not establish that the production fetch
image or command is broken. Compare the production task definition and log before
changing the fetch command or image.
