# sing-box-for-apple

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
