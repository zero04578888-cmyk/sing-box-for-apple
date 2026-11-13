# NEBULA 原生 VPN 精简版

独立分支 `feat/nebula-native-vpn`，起点为已通过完整 Release 构建的 `69b15b74b21a0f60a4a6d352d9da7e877c6d187f`。完整版 `feat/nebula-ui`、原完整 IPA/归档和官方 App 保留；本阶段不安装、覆盖或卸载任何设备 App，不处理 P12/私钥。

## 源码与构建结果

主 App `com.Ekg.IYmq`；独立 Packet Tunnel `com.Ekg.IYmq.extension`。两个组件共同使用用户从**主 App profile** 提取并提供的 `group.64AF44249V.hE6jb4`。没有生成 `group.com.Ekg.IYmq`，没有从 Group 名推断 Team ID，没有读取或提交原始 profile，也没有据此推断扩展已获授权。

- SFI 的编译依赖收敛为 SFI、Extension、Library、ApplicationLibrary；只内嵌 `PlugIns/Extension.appex`。其他平台/辅助扩展源码暂留作历史参考，但不在精简版 SFI 构建和交付中。
- 主 App/Packet Tunnel 的请求 entitlements 均只保留 `packet-tunnel-provider` 与上述共同 App Group。profile 内允许的更多权限不是必须全部请求。
- 去掉主 App iCloud 容器元数据和 iCloud/ubiquity entitlements；去掉扩展 wifi-info、multicast 与 macOS 命名空间的可选请求，避免假定尚未确认的授权。
- Variant 从主 App/扩展各自 Info.plist 的 `NebulaNativeVPNOnly` 标记识别精简版；配置页面不提供新建 iCloud 云端配置，底层云端读写明确报错，已有记录不迁移、不删除。删除辅助扩展后，不再注册 FileProvider domain 或提供失效的“在文件 App 浏览工作目录”入口。
- NEBULA 设计系统、首页/统计/节点 SwiftUI 组件原样保留。UI 只做可选能力入口与错误说明适配，不重新设计。

本地源码预检、双组件依赖/权限边界和打包负例测试不能代替 Xcode 构建。实际云端受测 SHA、结果、下载地址、架构与组件计数以后续 BUILD_RESULTS.md / Artifact 中的 release-inventory.json 为准；在真实运行完成前不标为通过。

## 功能保留与移除

| 功能 | 精简版结果 | 限制/证据 |
| --- | --- | --- |
| NEBULA 首页、连接按钮、节点、流量、统计 | 保留 | 对应设计及 Dashboard/Groups 源码不改；本轮不重做视觉验收 |
| sing-box 内核、代理协议、路由、DNS、Packet Tunnel | 实现保留 | 固定官方核心；Library/Network 和 PacketTunnelProvider.swift 与受测基线无 diff；不是数据面真机验证 |
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

## 独立 GitHub Actions 方案

`.github/workflows/ios-native-vpn-unsigned.yml` 在推送精简分支时触发；不修改完整版分支的工作流。标准 `macos-15-intel`，选择已安装 Xcode >=26.2，SFI / Release / generic/platform=iOS，实际输出必须是 iOS arm64。

流程：源码身份/依赖闭包检查 → 19 项边界单元测试 → 固定官方 Libbox/锁定 SPM → 仅 SFI 与 Extension 的实际 Build Settings → CODE_SIGNING_ALLOWED=NO 归档 → 校验两个 Bundle ID、相同 Group、无 iCloud、单个 Packet Tunnel → 手工 Payload IPA → 保留完整 xcarchive/App/dSYM/日志/xcresult，上传 14 天 Artifact。

缓存按工具链/官方核心 commit/Go/架构/锁文件区分。没有证书/profile 输入，没有钥匙串操作，没有私钥签名，没有模拟器/真机安装。打包器拒绝辅助扩展、错误 Group、iCloud 元数据、profile/私钥文件和外逃符号链接；不能用缺少组件的空包伪装成功。

## 签名与安装门槛

详见 [两份描述文件要求及阻塞](SIGNING_BLOCKERS.md) 和 [万能签检查清单](RESIGN_CHECKLIST.md)。**当前扩展独立 profile 缺失，签名准备状态为 BLOCKED_EXTENSION_PROFILE_REQUIRED。** 构建出的无签名 IPA只是后续二签输入，不表示已满足安装条件，更不表示真机 VPN 可用。
