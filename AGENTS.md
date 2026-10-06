# Agent guidance

Most changes in this repository add a signing manifest for a specific request. Use
[PR #297](https://github.com/mozilla-releng/adhoc-signing/pull/297) as an example of the
expected rationale and artifact evidence.

## Adding a signing manifest

1. Read the Bugzilla request and follow the review guidance in
   [docs/releng.md](docs/releng.md). Confirm the requestor's identity and the artifact's
   relationship to their organization. Explain why the signature is needed and why this
   ad hoc process fits. For repeat requests, link the earlier request and explain why
   this route still makes sense.
2. Identify the exact unsigned artifact. Verify its type, build variant, source revision,
   and chain of trust against the request. Make the manifest SHA-256 match the
   chain-of-trust record, and check `filesize` against the artifact bytes.
3. Add `signing-manifests/bugNNNNNN.yml`. Check its required fields and supported
   `signing-formats` and `signing-cert` values in
   [`signing_manifest.py`](taskcluster/adhoc_taskgraph/signing_manifest.py). Use a fetch
   type and URL that match the artifact source.
4. In the PR description, link the Bugzilla request, the try task and artifact, and the
   chain-of-trust evidence. State why ad hoc signing is appropriate; for a repeat request,
   include the previous PR when relevant.

Artifacts are public under the current workflow. End-to-end private artifact support is
incomplete; do not promise privacy based on the `private-artifact` field.

## Test the fetch task locally

For a manifest PR, use the `fetch-<manifest_name>` task label. Generate the graph with a
temporary params file for the PR event. This repository has no checked-in PR params
fixture:

```bash
TASK_LABEL=fetch-bugNNNNNN
PARAMS_FILE=/tmp/adhoc-signing-pr-params.yml
GRAPH_FILE=/tmp/adhoc-signing-target-graph.json
TASK_FILE=/tmp/adhoc-signing-fetch-task.json

uv run --with-editable "<taskgraph_repo>" taskgraph target-graph \
  --root taskcluster -p "$PARAMS_FILE" --json > "$GRAPH_FILE"
jq -e --arg label "$TASK_LABEL" '.[$label].task' "$GRAPH_FILE" > "$TASK_FILE"
uv run --with-editable "<taskgraph_repo>[load-image]" taskgraph load-task \
  --root taskcluster --image fetch - < "$TASK_FILE"
```

`--image fetch` builds this repository's `taskcluster/docker/fetch` image locally. It is
the image produced by the `docker-image-fetch` task. This runs the manifest's fetch task
in Docker and does not execute a signing task. Docker must be running.

Do not promote a manifest or trigger production signing while preparing a routine PR
unless the user explicitly requests that action. For Taskgraph code changes, inspect
[`.taskcluster.yml`](.taskcluster.yml), [`taskcluster/config.yml`](taskcluster/config.yml),
and the affected kind; follow the configured Taskcluster workflow instructions and reuse
existing upstream transforms.

See [docs/how-to-request.md](docs/how-to-request.md) for requester guidance and
[docs/releng.md](docs/releng.md) for the complete maintainer workflow.
