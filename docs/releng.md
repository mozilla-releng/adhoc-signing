# Release Engineering docs

This document is for Release Engineering, on how to maintain this repo, and how to deal with ad-hoc signing requests.

1. Find out what needs signing, and why
   1. Make sure the signing format is a [supported signing format](https://github.com/mozilla-releng/adhoc-signing/search?q=supported_signing_formats&unscoped_q=supported_signing_formats). (These are currently only Firefox Release cert formats.)
   2. Make sure this is a valid request.
2. Get the binary to sign. This can be via bug attachment, taskcluster artifact link, magic wormhole, Firefox Send.
3. Calculate the checksum and the filesize:
   ```
   openssl sha256 <filename>
   cat <filename> | wc -c
   ```
4. Create a pull request, adding a new signing manifest to the [signing manifest directory](https://github.com/mozilla-releng/adhoc-signing/tree/master/signing-manifests). Use the [template](https://github.com/mozilla-releng/adhoc-signing/blob/master/signing-manifests/example.yml.tmpl) and create a new `.yml` file.
5. Get review, and merge.
6. Promote your manifest to get a valid release signature. This will require some shipit changes that aren't yet implemented.
