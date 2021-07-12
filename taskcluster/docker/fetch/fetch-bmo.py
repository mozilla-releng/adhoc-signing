#!/usr/bin/python3 -u
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# XXX This file borrows much from `fetch-content`

import argparse
import contextlib
import gzip
import hashlib
import pathlib
import random
import sys
import time
import urllib.parse
import urllib.request


def log(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()


class IntegrityError(Exception):
    """Represents an integrity error when downloading a URL."""


@contextlib.contextmanager
def rename_after_close(fname, *args, **kwargs):
    """
    Context manager that opens a temporary file to use as a writer,
    and closes the file on context exit, renaming it to the expected
    file name in case of success, or removing it in case of failure.

    Takes the same options as open(), but must be used as a context
    manager.
    """
    path = pathlib.Path(fname)
    tmp = path.with_name('%s.tmp' % path.name)
    try:
        with tmp.open(*args, **kwargs) as fh:
            yield fh
    except Exception:
        tmp.unlink()
        raise
    else:
        tmp.rename(fname)


# The following is copied from
# https://github.com/mozilla-releng/redo/blob/6d07678a014e0c525e54a860381a165d34db10ff/redo/__init__.py#L15-L85
def retrier(attempts=5, sleeptime=10, max_sleeptime=300, sleepscale=1.5, jitter=1):
    """
    A generator function that sleeps between retries, handles exponential
    backoff and jitter. The action you are retrying is meant to run after
    retrier yields.

    At each iteration, we sleep for sleeptime + random.randint(-jitter, jitter).
    Afterwards sleeptime is multiplied by sleepscale for the next iteration.

    Args:
        attempts (int): maximum number of times to try; defaults to 5
        sleeptime (float): how many seconds to sleep between tries; defaults to
                           60s (one minute)
        max_sleeptime (float): the longest we'll sleep, in seconds; defaults to
                               300s (five minutes)
        sleepscale (float): how much to multiply the sleep time by each
                            iteration; defaults to 1.5
        jitter (int): random jitter to introduce to sleep time each iteration.
                      the amount is chosen at random between [-jitter, +jitter]
                      defaults to 1

    Yields:
        None, a maximum of `attempts` number of times

    Example:
        >>> n = 0
        >>> for _ in retrier(sleeptime=0, jitter=0):
        ...     if n == 3:
        ...         # We did the thing!
        ...         break
        ...     n += 1
        >>> n
        3

        >>> n = 0
        >>> for _ in retrier(sleeptime=0, jitter=0):
        ...     if n == 6:
        ...         # We did the thing!
        ...         break
        ...     n += 1
        ... else:
        ...     print("max tries hit")
        max tries hit
    """
    jitter = jitter or 0  # py35 barfs on the next line if jitter is None
    if jitter > sleeptime:
        # To prevent negative sleep times
        raise Exception(f'jitter ({jitter}) must be less than sleep time ({sleeptime})')

    sleeptime_real = sleeptime
    for _ in range(attempts):
        log("attempt %i/%i" % (_ + 1, attempts))

        yield sleeptime_real

        if jitter:
            sleeptime_real = sleeptime + random.randint(-jitter, jitter)
            # our jitter should scale along with the sleeptime
            jitter = int(jitter * sleepscale)
        else:
            sleeptime_real = sleeptime

        sleeptime *= sleepscale

        if sleeptime_real > max_sleeptime:
            sleeptime_real = max_sleeptime

        # Don't need to sleep the last time
        if _ < attempts - 1:
            log("sleeping for %.2fs (attempt %i/%i)" % (sleeptime_real, _ + 1, attempts))
            time.sleep(sleeptime_real)


def stream_download(url, sha256=None, size=None):
    """Download a URL to a generator, optionally with content verification.

    If ``sha256`` or ``size`` are defined, the downloaded URL will be
    validated against those requirements and ``IntegrityError`` will be
    raised if expectations do not match.

    Because verification cannot occur until the file is completely downloaded
    it is recommended for consumers to not do anything meaningful with the
    data if content verification is being used. To securely handle retrieved
    content, it should be streamed to a file or memory and only operated
    on after the generator is exhausted without raising.
    """
    log('Downloading %s' % url)

    h = hashlib.sha256()
    length = 0

    t0 = time.time()
    with urllib.request.urlopen(url) as fh:
        if not url.endswith('.gz') and fh.info().get('Content-Encoding') == 'gzip':
            fh = gzip.GzipFile(fileobj=fh)

        while True:
            chunk = fh.read(65536)
            if not chunk:
                break

            h.update(chunk)
            length += len(chunk)

            yield chunk

    duration = time.time() - t0
    digest = h.hexdigest()

    log('%s resolved to %d bytes with sha256 %s in %.3fs' % (
        url, length, digest, duration))

    if size:
        if size == length:
            log('Verified size of %s' % url)
        else:
            raise IntegrityError('size mismatch on %s: wanted %d; got %d' % (
                url, size, length))

    if sha256:
        if digest == sha256:
            log('Verified sha256 integrity of %s' % url)
        else:
            raise IntegrityError('sha256 mismatch on {}: wanted {}; got {}'.format(
                url, sha256, digest))


def download_to_path(url, path, sha256=None, size=None):
    """Download a URL to a filesystem path, possibly with verification."""

    # We download to a temporary file and rename at the end so there's
    # no chance of the final file being partially written or containing
    # bad data.
    try:
        path.unlink()
    except FileNotFoundError:
        pass

    for _ in retrier(attempts=5, sleeptime=60):
        try:
            log(f'Downloading {url} to {path}')

            with rename_after_close(path, 'wb') as fh:
                for chunk in stream_download(url, sha256=sha256, size=size):
                    fh.write(chunk)

            return
        except IntegrityError:
            raise
        except Exception as e:
            log(f"Download failed: {e}")
            continue

    raise Exception("Download failed, no more retries!")


def command_bmo_fetch(args):

    dest = pathlib.Path(args.dest)
    dest.parent.mkdir(parents=True, exist_ok=True)

    url = f"https://bugzilla.mozilla.org/attachment.cgi?id={args.attachment_id}"

    try:
        download_to_path(url, dest, sha256=args.sha256, size=args.size)

    except Exception:
        try:
            dest.unlink()
        except FileNotFoundError:
            pass

        raise


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='sub commands')

    url = subparsers.add_parser('bmo-attachment', help='Download a static URL')
    url.set_defaults(func=command_bmo_fetch)
    url.add_argument('--sha256', required=True,
                     help='SHA-256 of downloaded content')
    url.add_argument('--size', required=True, type=int,
                     help='Size of downloaded content, in bytes')
    url.add_argument('--name', required=True,
                     help='The base filename of what we are fetching')
    url.add_argument('attachment_id', help='Attachment ID fetch')
    url.add_argument('dest', help='Destination path')

    args = parser.parse_args()

    if not args.dest:
        parser.error('no destination directory specified, either pass in --dest '
                     'or set $MOZ_FETCHES_DIR')

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
