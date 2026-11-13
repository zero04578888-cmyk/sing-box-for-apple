# 双组件签名要求与阻塞报告

当前已知事实来自用户陈述：主 App 可用 ID 为 `com.Ekg.IYmq`；现有 Ad Hoc profile 包含 packet-tunnel-provider、Personal VPN 及 5 个 App Group，用户提取并指定共同容器 `group.64AF44249V.hE6jb4`。本阶段未读取 profile/P12/密码，没有 Apple Developer 后台访问，也没有真实签名。

## 两份 profile 的具体要求

| 项目 | 主 App profile | Packet Tunnel profile |
| --- | --- | --- |
| 对应 Bundle ID | com.Ekg.IYmq | com.Ekg.IYmq.extension（独立 ID） |
| application-identifier | 实际 AppIdentifierPrefix + com.Ekg.IYmq | 实际 AppIdentifierPrefix + com.Ekg.IYmq.extension |
| 团队/签名证书 | 同一开发团队，允许所用 Apple Distribution 证书及对应私钥 | 与主 App 同一 Team/证书体系，独立匹配扩展；不复制主 profile 冒充 |
| Network Extension | 授权 packet-tunnel-provider | **该独立扩展 ID** 也须被明确授权 packet-tunnel-provider |
| App Groups | 允许 group.64AF44249V.hE6jb4 | **扩展自己的 profile** 也必须允许同一 Group |
| Ad Hoc 设备 | 目标 iPhone UDID 在允许列表中 | 同一目标 iPhone 也被此 profile 允许 |
| 有效期/撤销/DER | 实际检查有效期、证书撤销与兼容的签名/profile 格式 | 逐项独立检查，不能从主 App 状态外推 |
| 当前证据 | 用户称已有，具体内容/证书匹配/UDID 未由本轮独立验证 | **未提供/缺失，明确阻塞** |

不根据 Group 字符串中的 `64AF44249V` 自动推断签名 Team ID 或 AppIdentifierPrefix。实际值以证书和每份 profile 的授权字段为准；共享 Group 能授权给多个不同 Bundle ID，但这不等于主 profile 本身可跨 Bundle ID 使用。

主 App 现有 Personal VPN 能力不替代 Packet Tunnel 扩展的签名授权。当前程序使用 NETunnelProviderManager 与独立自定义 Packet Tunnel，不通过改成同一个 Bundle ID、删扩展、或套用 Personal VPN 配置来绕过缺失 profile。精简版不实现单靠系统 IKEv2/IPsec 配置承载 sing-box 核心的替代方案。

## 为什么 P12 不能解决第二份 profile

P12 可以包含用户 Distribution 证书及其私钥，用于签代码；它不是创建任意 App ID、给扩展追加 NE/App Group 权限、或者签发 Apple provisioning profile 的授权。没有后台权限时，需要联系证书/profile 的提供方或持有相应开发者后台权限的团队，为 `com.Ekg.IYmq.extension` 创建/授权独立 ID 并提供正确 Ad Hoc profile。不能由本项目或万能签在本地伪造 Apple 授权。

如果提供方不能提供这份匹配扩展的 profile，则即使两个组件无签名编译和 IPA 结构检查通过，**原生 sing-box Packet Tunnel 安装/启用仍受阻塞**。不声称可以正常安装或使用 VPN；不把 App 打开、系统显示 Connected、或签名工具的“完成”提示作为真实数据面证据。

## 可选能力审计

精简签名请求只包含 NE + 共同 Group。没有请求 iCloud/ubiquity、wifi-info、multicast，也没有请求未使用的 Personal VPN API 权限；这些权限即使在主 profile 中被允许，也不会自动授权给扩展。iCloud 云端配置和五个辅助扩展的移除影响见 README.md。

wifi-info 移除后，SSID/BSSID 获取可能为空，基于 Wi-Fi 身份的路由规则可能不再匹配。multicast 移除后，组播/发现能力受系统限制。内核及协议实现仍保留，不能把这些 OS 权限限制误报为“所有配置功能完全等效”。如日后确需这些功能，应先确认扩展 profile 的相应授权，再独立评估，不自动添加权限。

## 保存与并存

原始 P12、私钥、密码、profile、UDID 与真实订阅只在受控本地保存，不上传聊天、公开仓库或公开 Actions。已签名 IPA 内嵌 profiles，也不得公开上传。本轮只公开 App/Group 标识符和源码请求模板；它们不是实际 profile 或授权证明。

完整版分支和原 Artifact 不被覆盖；官方 App 不被卸载或替换。两个已知旧打包命名空间不同于本次主 ID，但安装前仍需在本机确认没有任何已有 App 使用 `com.Ekg.IYmq`；若出现替换/删除提示即取消，不通过删除原 App 解决签名问题。原 sing-box URL scheme 的并存分配由 iOS 决定，验收时优先使用明确目标 App 的文件导入。

## 官方参考

- [Apple：Ad Hoc profile 与 App ID/证书/设备匹配](https://developer.apple.com/help/account/provisioning-profiles/create-an-ad-hoc-provisioning-profile/)
- [Apple：容器 App 与扩展均须签名](https://developer.apple.com/library/archive/documentation/General/Conceptual/ExtensibilityPG/ExtensionCreation.html)
- [Apple TN2415：entitlements 与 profile 授权](https://developer.apple.com/library/archive/technotes/tn2415/)
- [Apple：Network Extension entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension)
