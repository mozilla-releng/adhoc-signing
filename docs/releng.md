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
