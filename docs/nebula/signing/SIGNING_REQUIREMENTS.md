# NEBULA Release 签名需求

本阶段不修改 Swift UI、sing-box 内核或协议，不安装/卸载任何设备 App。此文档不包含证书、私钥、密码、描述文件或订阅。

## 已有验证与本次产物

前一成功运行：[43380949798](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43380949798)，代码 `cdb1d15ca10c53fc1455364dcd7a5758af9a0aa4`；Xcode 26.2 / 17C52，macos-15 ARM64，SFI scheme，Debug，generic/platform=iOS，CODE_SIGNING_ALLOWED=NO。设备编译、3 项 fixture UI 测试及原生捕获通过。后续 `0ef6e51` 仅更新文档。旧工作流只上传诊断证据，没有上传可重新签名的完整 App，也没有验证 Release。

本次独立工作流：`.github/workflows/ios-release-unsigned.yml`，手动触发，SFI / Release / generic/platform=iOS，禁用开发者签名。优先生成 xcarchive；归档失败时保留具体错误并尝试真实 Release build。通过结构、机型平台、Mach-O 与依赖检查后，使用完整 App 创建 `Payload/sing-box.app` 的 ZIP，命名为 `NEBULA-Release-Unsigned.ipa`。

初始使用标准 macos-15 ARM64，已成功生成过完整 Release IPA。后续核对运行 43416381403 因 GitHub ARM64 容量不足、未分配 runner 而失败，没有执行代码。为避免重复排队，Release 工作流改用 GitHub 文档列出的标准 `macos-15-intel`；不使用 `-large` / `-xlarge`。实际 Xcode/SDK 仍需预检，实际 host 架构与系统版本分别保存在 runner-architecture.txt、macos.txt；目标产物始终是 iOS arm64。

这是**手工打包的无开发者签名 IPA**，不是 `xcodebuild -exportArchive` 的已签名导出，不可直接据此安装或宣称 VPN 可用。未运行依赖账户/描述文件的签名导出。预编译 Framework 中如有供应商签名，不代表已为用户签名；二签必须覆盖全部内嵌代码。

实际成功的 Release commit、Xcode、产物数量和下载链接以最终构建记录、`build-logs/commit.txt`、`xcode.txt`、`release-inventory.json` 为准；未完成的运行不能记录为通过。

首轮 Release 的 `xcodebuild archive` 已成功，但 Xcode 没有替换 NSUbiquitousContainers 的字典键变量，打包器拒绝不一致的容器。修复限定在无签名 Release 产物打包层：保留通用源码 Info.plist 原默认配置，打包时仅把已知的原源码容器键（或早期变量模板键）转换成隔离构建的 iCloud 容器，保留其全部配置值；不一致的运行时身份和未知容器仍被拒绝。该步骤发生在创建 IPA 和 tar 之前，archive/App/IPA 均保留一致的规范化配置；前后 plist SHA-256 记在 inventory。没有删减 iCloud 权限，也没有改动 Swift/核心代码；普通 Xcode 构建的源码配置保持原样。

## 标识与描述文件

源码默认 base：`io.nekohasekai.sfamt`；默认共享容器：`group.io.nekohasekai.sfamt`。本次云端构建主动覆盖为隔离的**公开占位标识**，没有声称这些标识已在用户开发者账户注册。

| 组件 | 本次无签名 Bundle ID | 单独匹配的 Ad Hoc profile |
| --- | --- | --- |
| 主 App / SFI | io.github.zero04578888.nebula | 1 |
| Packet Tunnel / Extension | io.github.zero04578888.nebula.extension | 1 |
| WidgetExtension | io.github.zero04578888.nebula.widget | 1 |
| FileProviderExtension | io.github.zero04578888.nebula.fileprovider | 1 |
| ShareExtension | io.github.zero04578888.nebula.share | 1 |
| ActionExtension | io.github.zero04578888.nebula.action | 1 |
| IntentsExtension（ExtensionKit） | io.github.zero04578888.nebula.intents | 1 |

保留完整组件时，签名计划为 **7 个匹配 Bundle ID 的 App ID / 7 份 profile**。最低限度主 App + Packet Tunnel 也需要各自匹配；本交付不删掉其余扩展来减少签名要求。Framework/dylib 需要重新签名，但不各自申请 provisioning profile。最终数量以实际 inventory 为准。

用户现有一个固定 App ID、一个 Ad Hoc profile 和 5 个 App Group，尚不能证明完整包可签。5 个 Group 不是 5 个 App ID，也不能代替扩展 profiles。主 App 的固定 ID 若为 `A`，当前代码从 Info.plist 的 BasePackageIdentifier 推导 VPN ID 为 `A.extension`，必须注册并配置这个独立扩展 ID；其余后缀同表。

每份 profile 必须属于同一开发团队，准确匹配对应 Bundle ID，包含这台 iPhone 16 Pro Max 的 UDID，未过期/未撤销，允许所用 Distribution 证书，并授权相应能力。必须实际持有证书对应的**私钥**；只有 `.cer` 或证书显示名称不能完成签名。本轮未读取或验证用户材料，以上账户状态均为 UNVERIFIED。

## App Group 与运行时配置

本次占位共享容器：`group.io.github.zero04578888.nebula`。主 App 和所有扩展在 entitlement 及各自 Info.plist 的 `AppGroupIdentifier` 中使用相同值。生产二签时从用户已有 5 个 Group 中选择一个确实属于该 Team 且授权给全部相关 App ID 的共同 Group；不能随意给每个扩展分配不同 Group。

`Library/Shared/AppConfiguration.swift` 在运行时读取 Info.plist，推导 VPN provider ID、后台任务、UTType、iCloud 容器。故仅修改 CFBundleIdentifier 或签名的 application-identifier 不够。占位包改为用户自己的 `A` / `G` 时，至少同步核对：

- 主 App 的 CFBundleIdentifier = A，各扩展 = A 加表内后缀。
- 主 App/各扩展的 BasePackageIdentifier = A，AppGroupIdentifier = G。
- 各签名 entitlement 的 application-identifier、team-identifier、App Groups、必要的 keychain-access-groups 应来自正确 profile/团队，不能沿用上游 Team。
- 主 App 的 BGTaskSchedulerPermittedIdentifiers = A.update_profiles；UTExported/Imported 的 profile 类型及相关引用同步。
- 主 App 的 NSUbiquitousContainers、主 App/Intents 的 iCloud/ubiquity entitlements 对应已授权 `iCloud.A`；如用户没有相应 iCloud 能力，完整功能签名仍有阻塞，不能悄悄删除能力后称功能保留。
- FileProvider 的 NSExtensionFileProviderDocumentGroup = G。

最可靠的路径是使用自己的非官方 `A` / `G` 在受控环境重新构建同一源码，再签名；如果二签工具能完整重写这些运行时字段，也需逐项验证。不要对二进制做不确定的字符串替换。requested-entitlements 中的 plist 只是源码请求模板，不是 profile，也不是已签名授权，不能原样当成所有组件的通用 entitlements。

## 权限核对

| 组件 | 源码请求 | 需要核对 |
| --- | --- | --- |
| 主 App | Network Extension: packet-tunnel-provider；App Groups；iCloud CloudDocuments/ubiquity | 主 App profile 也需匹配 NE、Group 与 iCloud，不能只核对扩展 |
| Packet Tunnel | packet-tunnel-provider；App Groups；multicast；wifi-info | VPN 扩展的独立 profile 中对应的 iOS 能力；保留源码请求，不以任意添加 entitlement 伪造授权 |
| Intents | App Groups；iCloud CloudDocuments/ubiquity | 独立 profile、iCloud 与共享容器 |
| Widget/FileProvider/Share/Action | App Groups 等各自请求 | 各自 profile 与共同 Group |

部分共享 entitlement 文件含 `com.apple.security.app-sandbox`、network.client/server、files.user-selected 等 macOS 命名空间键。完整请求清单原样提供，不把这些键一概解释成 iOS 开发者门户的独立能力。实际 iOS 签名 entitlement 与 profile 的允许集合必须逐项比对。用户已说明具有 packet-tunnel-provider 权限，但没有读取具体 profile，故不推断权限已覆盖所有 App ID。

## 万能签兼容性结论

**条件性可二签；未实测，不能保证该版本万能签支持此完整多扩展包。** 未获得工具版本或本地运行证据，也没有可核实的完整 7-profile/ExtensionKit/自定义运行时字段支持证据；不把名称相近的签名工具当成同一产品。

必须具备：保留 PlugIns 与 Extensions 中全部扩展；逐 Bundle ID 指定 profile；递归签名全部动态 Framework/dylib 和扩展、最后签主 App；保留正确 entitlements；支持当前 iOS 所需签名格式/DER；完整处理上述运行时标识。若工具对所有组件强制套用同一份 profile（且不能保留或映射各扩展自己的 profile）、仅改主 Bundle ID、自动移除扩展或丢掉 NE/App Groups，则**不满足本项目签名要求**。不得靠“忽略权限错误”继续安装。

不把 P12/私钥、密码、profile 发送到其在线签名网页；仅在用户已信任、确认材料保存在本机的签名环境操作。未能确认本地处理时，不输入私钥。构建流程不接收这些输入，也没有相关 Secrets。已签名 IPA 内含各组件的 embedded.mobileprovision，属于私有交付，也不得上传公开仓库或公开 Artifact。

## 不覆盖官方安装

本阶段没有设备安装操作。占位 Bundle ID 和 Group 与源码上游默认值不同，打包器拒绝上游身份/容器。二签仍必须选与现有 App Store App **不同**的 Bundle ID、不同共享容器及对应 profiles；若固定 App ID 与已装官方包相同，停止安装并先取得独立 ID/profile，不卸载、不覆盖、不迁移原应用数据。

显示名称相同不等于相同 Bundle ID；可在本地签名副本设置显示名称为 NEBULA 以便辨认。两个 App 仍声明原 sing-box URL scheme，iOS 可能选择其中一个处理该链接；验收阶段使用明确的文件导入/目标 App，不能据此认为官方数据被改写。

## 官方依据

- [Apple：创建 Ad Hoc profile](https://developer.apple.com/help/account/provisioning-profiles/create-an-ad-hoc-provisioning-profile/)：App ID、证书与已注册设备关联。
- [Apple：App Extension Programming Guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/ExtensionCreation.html)：容器 App 与内嵌扩展都必须签名。
- [Apple TN2415](https://developer.apple.com/library/archive/technotes/tn2415/)：签名 entitlement 必须得到 profile 授权。
- [Apple：Network Extensions entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension)：packet-tunnel-provider。
- [GitHub：标准托管 runner](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)：macos-15-intel 为标准 Intel 标签，与 larger runner 标签不同。

构建、结构验证和二签准备都不能替代签名安装及真实 VPN 数据面的验收。
