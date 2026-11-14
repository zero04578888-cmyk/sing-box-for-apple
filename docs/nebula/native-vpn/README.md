# NEBULA QCBW52C8MV 原生 VPN

独立分支 `feat/nebula-qcbw52c8mv-native-vpn` 从已保留启动保护的修复分支创建。完整版本、原精简版、修复分支及官方 App 保留，不安装、覆盖或卸载设备 App。

## 当前身份

- 唯一目标签名团队：`QCBW52C8MV`。
- 主 App：`app.turquoise204.lynx5076`。
- 计划 Packet Tunnel：`app.turquoise204.lynx5076.extension`。
- 两组件共同 Group：`group.43f7b1421047676b.1`。
- 主 profile 的 App ID、Group、证书关联已本地审计；扩展独立 profile **仍缺失**，不推断计划 ID 获 Apple 授权。

Info.plist 和请求权限模板使用同一构建变量。AppConfiguration 动态派生扩展 ID、后台任务和配置文件类型。活动 iOS 构建目标默认团队改为 QCBW52C8MV，使用手动配置和空签名身份；无签名 CI 仍明确禁止签名，不输入私钥。

NEBULA 页面、核心、协议和四个启动保护 Swift 文件与修复分支保持一致。新 Bundle ID/Group 使用独立容器，不自动访问、搬运或删除旧数据；必要配置由用户本地导出再导入，不放公开 CI。

## 功能保留与移除

| 功能 | 精简版结果 | 限制/证据 |
| --- | --- | --- |
| NEBULA 首页、连接按钮、节点、流量、统计 | 保留 | 对应设计及 Dashboard/Groups 源码不改；本轮不重做视觉验收 |
| sing-box 内核、代理协议、路由、DNS、Packet Tunnel | 实现保留 | 固定官方核心；保留现有网络实现及已完成的共享容器启动检查；不是数据面真机验证 |
| VPN 启停、系统授权、状态反馈、按需连接 | 既有链路保留 | NETunnelProviderManager + 独立 NEPacketTunnelProvider；仍需扩展 profile 及真机验证 |
| 本地配置、订阅、后台订阅更新、节点选择/测速 | 保留 | 沿用既有存储/HTTP/服务操作；未导入真实订阅 |
| 配置编辑、文件导入/导出、App 内分享与二维码 | 保留 | 系统文件选择器可将用户选中的 iCloud Drive 等提供者文件导入为本地副本；不等于持有自有 iCloud 容器 |
| iCloud 云端配置类型/自动云端读写 | 移除/禁用 | 缺少已确认 iCloud 授权；历史记录保留，读取时报可恢复说明，不静默转存或删数据 |
| Widget/控制中心独立组件 | 不打包 | WidgetExtension 移除；不承诺对应入口可用 |
| Siri/App Intents 独立扩展 | 不打包 | IntentsExtension 移除；不承诺所有快捷指令路径可用 |
| Files App 工作目录集成 | 移除 | FileProviderExtension 不打包，不注册 domain；App 内工作目录管理和配置文件导入/导出保留 |
| 作为系统接收目标的 Share/Action 扩展 | 移除 | 其他 App 的系统 Share/Action 菜单不再通过这些扩展导入；App 内文件导入及导出分享保留 |
| SSID/BSSID 感知规则 | 可能受限，未验证 | 未请求 wifi-info；保留核心实现已有的 nil/不可用处理，不声称依赖 Wi-Fi 身份的规则仍等效 |
| 组播/广播发现相关功能 | 可能受限，未验证 | 未请求 multicast；普通 TCP/UDP/路由/DNS 实现未裁剪，但受 OS 权限的流量与局域网发现需另测 |
| macOS/tvOS | 不作本轮结论 | 使用原完整版分支；不以 iOS 精简构建推断其他平台 |

数据库 schema、现有 profile ID 和内容不改；仅 iCloud 读写增加精简版可用性检查。本地/远程配置读写仍走原路径。不要把完整 App 的整个 Group 数据目录直接覆盖到精简版，或在安装失败时删除原 App。

## Codemagic 无签名构建

选择本分支根目录 codemagic.yaml 的 `nebula-native-vpn-unsigned`，显示名 `NEBULA QCBW52C8MV - unsigned Release`。机器为 mac_mini_m2 / Xcode 26.2 / SDK 26.2，仅手动启动，先核对免费额度；不使用签名变量组或开发者自动签名。

复用固定官方 Libbox、锁定 SPM、Release archive 和 Payload 打包。检查源码身份、主/扩展 Info、后台任务和文件类型后，重新读取实际 IPA，比对两组件身份、ZIP CRC 与每个文件，拒绝旧 Group、少扩展或与归档 App 不一致的包。

成功输出 IPA、完整 archive、匹配 dSYM、ipa-verification.json、release-inventory.json、dSYM-inventory.json、validation-report.json、日志及 xcresult。intendedSigningTeamID 仅是二签目标，不是已经授予的权限。

本分支新身份尚无云端完成或真机验收记录；[历史构建结果](BUILD_RESULTS.md) 仅记录旧版本，不能把旧 IPA 当作新身份交付。

## 签名门槛

详见 [独立描述文件要求](SIGNING_BLOCKERS.md) 和 [万能签/真机清单](RESIGN_CHECKLIST.md)。状态仍为 **BLOCKED_EXTENSION_PROFILE_REQUIRED**。主 profile、证书、Group 和编译成功都不能代替扩展独立授权。
