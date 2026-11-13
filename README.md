# sing-box-for-apple

## NEBULA Native VPN branch

This independent `feat/nebula-native-vpn` branch keeps the NEBULA interface and the native sing-box Packet Tunnel path while distributing only SFI and Extension. The [full version](https://github.com/zero04578888-cmyk/sing-box-for-apple/tree/feat/nebula-ui) is preserved.

Main ID: `com.Ekg.IYmq`; provider ID: `com.Ekg.IYmq.extension`; common user-reported authorized Group: `group.64AF44249V.hE6jb4`. The extension profile is **MISSING**; one main profile does not authorize both components. No private signing or device installation is performed.

See [adaptation and feature impact](docs/nebula/native-vpn/README.md), [two-profile requirements/blockers](docs/nebula/native-vpn/SIGNING_BLOCKERS.md), [re-signer/device checklist](docs/nebula/native-vpn/RESIGN_CHECKLIST.md), and the [independent unsigned workflow](.github/workflows/ios-native-vpn-unsigned.yml). Historical full-version signing docs elsewhere do not describe this two-component package.

Experimental iOS/macOS/tvOS client for sing-box, the universal proxy platform.

## Documentation

[SFI](https://sing-box.sagernet.org/installation/clients/sfi/) | [SFM](https://sing-box.sagernet.org/installation/clients/sfm/)

## NEBULA iOS interface

This fork develops the NEBULA dark SwiftUI interface for iPhone 16 Pro Max. Existing VPN, proxy, profile, subscription, and remote-control features retain their original service implementations; the sing-box core and network protocols are not edited.

- [Source analysis](docs/nebula/SOURCE_ANALYSIS.md) and [change log](docs/nebula/CHANGELOG.md)
- [Design system](DESIGN.md)
- [Validation results](docs/nebula/TEST_RESULTS.md) and [build/device next steps](docs/nebula/NEXT_STEPS.md)
- [Unsigned iOS workflow](.github/workflows/ios-unsigned.yml): macOS dependency checks and unsigned device compilation, with optional fixture UI tests on Simulator

Code `cdb1d15` passed [unsigned device compilation and 3 fixture UI tests](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43380949798) on iPhone 16 Pro Max / iOS 26.2 Simulator.

Unsigned compilation and Simulator tests do not establish that a signed IPA can operate a real VPN. No signing private keys, credentials, or real subscriptions are included.

## License

```
Copyright (C) 2022 by nekohasekai <contact-sagernet@sekai.icu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
```
