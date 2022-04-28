# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Used in build_scriptworker_mac_signing_payload
MAC_STATIC_VARS_BY_PRODUCT = {
    # These variables will always be included in the task payload
    "mozillavpn": {
        # URLs used for Mac Notarization
        # TODO: These URLs should at least target the VPN repo
        "loginItems-entitlements-url": "https://gist.githubusercontent.com/bhearsum/d4dc4b93045baa3698c3b0b55e2491bb/raw/f3649e1b703aefe833916a71b725062dd1b7c86e/gistfile1.txt",
        "entitlements-url": "https://gist.githubusercontent.com/bhearsum/5dac6f523a828675bbc00e8165e29946/raw/6b5a395c476679bcc5ecb07eafdc8e5adefc7470/gistfile1.txt",
    }
}
