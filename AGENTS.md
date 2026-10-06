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
