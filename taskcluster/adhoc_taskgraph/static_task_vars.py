# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Used in build_scriptworker_mac_signing_payload
MAC_STATIC_VARS_BY_PRODUCT = {
    # These variables will always be included in the task payload
    "mozillavpn": {
        # URLs used for Mac Notarization
        "loginItemsEntitlementsUrl": "https://raw.githubusercontent.com/mozilla-mobile/mozilla-vpn-client/main/taskcluster/scripts/signing/loginItems-entitlements.xml",
        "entitlementsUrl": "https://raw.githubusercontent.com/mozilla-mobile/mozilla-vpn-client/main/taskcluster/scripts/signing/entitlements.xml",
    },

    "firefox": {
        "entitlements-url": "https://hg.mozilla.org/mozilla-central/raw-file/tip/security/mac/hardenedruntime/v1/production/browser.xml",
        "requirements-plist-url": "https://hg.mozilla.org/mozilla-central/raw-file/tip/build/package/mac_osx/requirements.plist",
    },
    "mozregression": {
        "entitlements-url": "https://raw.githubusercontent.com/mozilla/mozregression/main/gui/mac/entitlements.xml",
        "requirements-plist-url": "https://raw.githubusercontent.com/mozilla/mozregression/main/gui/mac/requirements.plist",
    },
}
