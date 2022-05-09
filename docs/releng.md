# Release Engineering docs

This document is for Release Engineering, on how to maintain this repo, and how to deal with ad-hoc signing requests.

1. Find out what needs signing, and why
   1. Make sure the signing format is a [supported signing format](https://github.com/mozilla-releng/adhoc-signing/search?q=supported_signing_formats&unscoped_q=supported_signing_formats). (These are currently both Firefox Release and Firefox Nightly cert formats.)
   2. Make sure this is a valid request. (e.g. check the requester identity on PMO, ensure the binary is related to the requester organization, etc)
2. Get the binary to sign. This can be via bug attachment, taskcluster artifact link, magic wormhole
3. Calculate the checksum and the filesize:
   ```
   openssl sha256 <filename>
   cat <filename> | wc -c
   ```
4. Create a pull request, adding a new signing manifest to the [signing manifest directory](https://github.com/mozilla-releng/adhoc-signing/tree/master/signing-manifests). Use the [template](https://github.com/mozilla-releng/adhoc-signing/blob/master/signing-manifests/example.yml.tmpl) and create a new `.yml` file.
5. Get review, and merge.
6. Promote your manifest to get a valid release signature. Someday these steps will be in shipit, but for now:
   - Go to the merge taskgroup. Generally this is linked from the status symbol of the latest merge to master: a yellow dot for in-progress, a red X for failure, and a ![green checkmark](screenshot1.png) for success. Click it.
   - Click on `details` of the decision task, then `View task in taskcluster` to go to the decision task. This task will need to be green before we can proceed.
   - Go to the task group view: Either click on `Task Group` at the top left, or change the `tasks/TASKID` to `tasks/groups/TASKID` in the url bar.
   - Click the vertical three dots in the lower right, and choose `Promote an adhoc signature`. You will need to be signed in for this to work. The sign-in link is in the top right.
   - In the `Promote an adhoc signature` page, fill in the `adhoc_name`. This will match the name of the new signing manifest, minus the trailing `.yml`. So if you just added `bug12345.yml` for this signing request, your `adhoc_name` would be `bug12345`.
   - Click `Promote an Adhoc Signature` in the bottom right. This will spawn an action task. Once it goes green, go to the action task group by changing the url from `tasks/TASKID` to `tasks/groups/TASKID`. (The `Task Group` link in the top left will bring you to the *decision task group*, not the *action task group*.) The `release-signing` task will have the signed artifact.

## Troubleshooting

### Fetch tasks failing due to size mismatch

If the fetch task fails with an error similar to:
```
[task 2022-05-09T18:26:34.476Z] Downloading https://firefox-ci-tc.services.mozilla.com/api/queue/v1/task/ZkERnaA8TDqw53rZVdG1lA/runs/0/artifacts/public%2Fwindows%2Finstaller%2FMozillaVPN.msi
[task 2022-05-09T18:26:35.075Z] https://firefox-ci-tc.services.mozilla.com/api/queue/v1/task/ZkERnaA8TDqw53rZVdG1lA/runs/0/artifacts/public%2Fwindows%2Finstaller%2FMozillaVPN.msi resolved to 21618688 bytes with sha256 50aab8a6508f5155c275e25e490bc41a112223b060c708cee3883cbd294940eb in 0.599s
[task 2022-05-09T18:26:35.078Z] Traceback (most recent call last):
[task 2022-05-09T18:26:35.078Z]   File "/usr/local/bin/fetch-content", line 675, in <module>
[task 2022-05-09T18:26:35.079Z]     sys.exit(main())
[task 2022-05-09T18:26:35.079Z]   File "/usr/local/bin/fetch-content", line 671, in main
[task 2022-05-09T18:26:35.079Z]     return args.func(args)
[task 2022-05-09T18:26:35.079Z]   File "/usr/local/bin/fetch-content", line 554, in command_static_url
[task 2022-05-09T18:26:35.079Z]     download_to_path(args.url, dl_dest, sha256=args.sha256, size=args.size)
[task 2022-05-09T18:26:35.079Z]   File "/usr/local/bin/fetch-content", line 226, in download_to_path
[task 2022-05-09T18:26:35.079Z]     for chunk in stream_download(url, sha256=sha256, size=size):
[task 2022-05-09T18:26:35.079Z]   File "/usr/local/bin/fetch-content", line 200, in stream_download
[task 2022-05-09T18:26:35.079Z]     url, size, length))
[task 2022-05-09T18:26:35.079Z] __main__.IntegrityError: size mismatch on https://firefox-ci-tc.services.mozilla.com/api/queue/v1/task/ZkERnaA8TDqw53rZVdG1lA/runs/0/artifacts/public%2Fwindows%2Finstaller%2FMozillaVPN.msi: wanted 21453995; got 21618688
[taskcluster 2022-05-09 18:26:35.351Z] === Task Finished ===
[taskcluster 2022-05-09 18:26:35.479Z] Unsuccessful task run with exit code: 1 completed in 8.074 seconds
```

This could be due to a network error, mitm attack or (most likely) file compression. To resolve this:
1. Make sure the file was decompressed when you downloaded it locally to check the hash / size. Either download it through Firefox or use `curl --compressed`.
2. If the sizes still don't match, try re-running the task to rule out a network intermittent.
3. If the sizes still don't match you may be the target of a mitm attack. Try using a VPN and/or avoid public WiFi.
