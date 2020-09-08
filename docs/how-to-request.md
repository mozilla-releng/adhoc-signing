# How to request an ad-hoc signature

The easiest way is via Bugzilla.

1. File a bug in the `Release Engineering::Custom Release Requests` component. This bug must be public.
2. Attach the unsigned binary to the bug. The attachment needs to be under 10mb.
3. Ideally give us the sha256 and filesize of the binary at the same time. You can get this value by
   ```
   openssl sha256 FILENAME
   cat FILENAME | wc -c
   ```
   Or, to find sha256 on Windows
   ```
   certutil -hashfile FILENAME SHA256
   ```
4. You can also open a PR for expediency. This is essentially copying the [template](https://github.com/mozilla-releng/adhoc-signing/blob/master/signing-manifests/example.yml.tmpl) to a `bugXXXXX` file in the [signing-manifests directory](https://github.com/mozilla-releng/adhoc-signing/tree/master/signing-manifests), and filling out the appropriate values.
5. If your request is approved, releng will review, merge, and sign your artifact, and attach it to the bug.

## Supported signatures

We currently support Firefox Release Authenticode (Windows) signing, and Firefox Release MAR (update) signing.

## Binaries larger than 10mb

We don't require bugzilla attachments currently. If you can get the assignee the file to sign in some other way (Firefox Send, magic wormhole), that should be sufficient. One workaround is to land the file in a github repo somewhere.

## Private artifacts

Currently, all artifacts will be public, meaning the unsigned and signed binaries will be available on the internet. Currently our support for keeping the binaries private end-to-end is incomplete. We can revisit should there be a need.
