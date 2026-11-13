# NEBULA Release 构建结果

[成功运行](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43419126885) · [下载完整 Artifact](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43419126885/artifacts/14034408615)

- 实际受测提交：`69b15b74b21a0f60a4a6d352d9da7e877c6d187f`；后续文档提交不改变该 IPA。
- SFI scheme / Release / generic/platform=iOS；设备目标为 arm64。
- 标准 macos-15-intel（x86_64）；Xcode 26.2 / 17C52；iOS SDK 26.2。
- 19 项源码测试通过；日志明确记录 ARCHIVE SUCCEEDED。
- 7 个 App/appex、8 个设备 Mach-O、Library.framework、131 个 App 普通文件及 8 份 dSYM 已保留。Libbox/Swift 依赖按实际链接结果处理，系统 Framework 由 iOS 提供；不是把所有源码 SDK 目录机械复制进 IPA。
- 构建/打包全程没有开发者签名、描述文件、私钥或真实订阅输入；未运行 UI fixture/截图测试，Swift 界面代码与已通过的 NEBULA 版本一致。

## 可下载内容

Artifact：`nebula-release-unsigned-43419126885`，ID `14034408615`，到期 `2026-11-27T12:09:31Z`（需 GitHub 登录）。

| 文件 | 用途 |
| --- | --- |
| NEBULA-Release-Unsigned.ipa | 完整 Payload 手工打包的无开发者签名 IPA；不是已签名 exportArchive 导出 |
| NEBULA-Unsigned.xcarchive.tar.gz | 完整规范化后的归档、App/扩展/Framework/资源与 dSYM |
| sing-box.app.tar.gz | 完整 App，保留文件权限及结构 |
| release-inventory.json | 7 个组件、8 个 Mach-O 的身份、架构、依赖、散列与签名状态；iCloud 元数据转换前后散列 |
| requested-entitlements/ | 7 份源码请求模板；不是 provisioning profiles 或 Apple 授权 |
| build-logs/、xcresult | 工具链、依赖、Release 设置、归档日志和结果 |
| signing-guides/、SHA256SUMS.txt | 签名准备、验收说明与公开校验值 |

IPA 大小：35,701,573 bytes；SHA-256：`f8f1329fcd28a9e95ae29c10fbe5407fe2dc2d2e4d89b3d19a0fb8eb7b7a4c1c`。

下载复核通过：全部公开 SHA256SUMS、ZIP CRC、8 个 Mach-O 散列、7 个运行时身份，App tar 内全部 131 个普通文件与 IPA 一致；xcarchive/App/IPA 的 iCloud 元数据一致。不是签名/安装/VPN 证明。

## 实际打包身份

主 App：`io.github.zero04578888.nebula`；Packet Tunnel：`io.github.zero04578888.nebula.extension`；App Group：`group.io.github.zero04578888.nebula`。这些是公开占位标识，不代表已在用户账户注册。

全量包计划需要 7 个对应的 App ID/profile 映射。Framework/dylib 需要签名，但不各自申请 profile。用户现有一份 Ad Hoc profile/一个固定 App ID 尚不足以证明全量包可签；5 个 App Group 不能代替扩展 App ID。主 App 和 VPN 扩展各自需要匹配的 NE/App Group 授权，还需核对 iCloud、wifi-info、multicast 等请求。

参阅 [签名需求](SIGNING_REQUIREMENTS.md)、[万能签步骤](RESIGN_INSTALL.md)、[真机验收](DEVICE_VPN_CHECKLIST.md)。工具版本与签名材料未实测，万能签兼容性为 UNVERIFIED。没有签名 IPA、没有安装/卸载/覆盖任何 App Store 应用，没有真实 VPN 可用结论。

## 运行记录

| 运行 | 提交 | 结果 |
| --- | --- | --- |
| 43412839795 | 3571b85 | Release archive 成功；Xcode 不展开 iCloud 字典键，元数据检查拒绝打包，原始产物保留 |
| 43414874790 | 8ff0ba6 | 18 项检查、Release 归档、完整 IPA/Artifact 成功；下载复核通过 |
| 43416381403 | 7edc491 | ARM64 runner 容量不足，多次未分配而失败；没有执行代码，不计作编译失败或通过 |
| 43419126885 | 69b15b7 | 最终标准 Intel runner：19 项检查、Release 归档、IPA/Artifact 与下载复核全部通过 |

最终源码中的 SFI/Info.plist、SwiftUI、网络/扩展、内核、Xcode 项目配置均与本阶段开始时相同。元数据转换只作用于隔离的无签名 Release 产物：识别原源码已知容器键，转换为该构建的 iCloud 容器，保持全部值并验证身份一致性；不删权限、不改二进制协议实现。

构建仍有上游/既有警告，例如 Libbox 生成头的 nullability、Swift 6 actor-isolation 提示及 AppIntents 元数据跳过；本轮没有为消除警告而改动核心或网络实现。日志完整保留。
