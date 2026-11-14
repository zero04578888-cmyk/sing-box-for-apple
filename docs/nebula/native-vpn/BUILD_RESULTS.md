# 历史：旧身份精简版云端构建与签名状态

> 以下是旧身份与旧提交的历史成功记录，不是 QCBW52C8MV 新身份版本的编译或 VPN 验收证明。当前分支、标识和待构建状态见 [README](README.md)。

**源码适配、云端无签名 Release 构建与下载复核通过；签名 BLOCKED_EXTENSION_PROFILE_REQUIRED。**

- 分支 `feat/nebula-native-vpn`；受测提交 `5743a8412714bf96a7cd32b9e2237fd34f4d2d7e`，起点为已通过完整版 Release 的 `69b15b74b21a0f60a4a6d352d9da7e877c6d187f`。
- [成功运行](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43436217497) · [下载 Artifact](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43436217497/artifacts/14044821988)（需 GitHub 登录，保留至 `2026-11-27T14:05:29Z`）。
- Xcode 26.2 / 17C52，标准 macos-15-intel；SFI / Release / generic/platform=iOS，实际设备产物 arm64。
- 19 项源码/打包负例/身份/权限/依赖闭包检查通过，日志有 ARCHIVE SUCCEEDED。
- 实际交付：主 App + 1 个 Packet Tunnel、3 个设备 Mach-O、Library.framework 及资源、完整 xcarchive/App tar 与 dSYM。不是裁掉代理内核来减小签名要求。
- 下载复核：全部公开 SHA-256、ZIP CRC、78 个 App 普通文件与 tar 逐项一致、两个 Bundle 的身份/同一 Group/原生标记/无 iCloud、3 个 Mach-O 散列、两份最小权限模板以及 archive/App/IPA 元数据一致。

## IPA 与构建产物

`NEBULA-NativeVPN-Unsigned.ipa`，34,974,868 bytes；SHA-256：`0e04f514b545b1d8fe0e38d66bda4a9bdf7baccf1f30af62d6452e41e7664bd7`。

这是完整 Payload 手工打包的**无开发者签名** IPA，不是已签名 exportArchive 导出。Artifact 另含完整 NEBULA-NativeVPN-Unsigned.xcarchive.tar.gz、sing-box.app.tar.gz、release-inventory.json、requested-entitlements/、日志、xcresult 与原生版说明。请求模板不是 provisioning profile，也不是 Apple 已签名授权。

## 身份与两个 profile

| 组件 | Bundle ID | 共同 Group | 当前授权证据 |
| --- | --- | --- | --- |
| 主 App | com.Ekg.IYmq | group.64AF44249V.hE6jb4 | 用户从主 profile 提取；本轮未读取原始文件，不独立验证证书/设备/有效期 |
| Packet Tunnel | com.Ekg.IYmq.extension | group.64AF44249V.hE6jb4 | 计划中的独立 ID；**独立 profile 缺失，不推断已获授权** |

需要两份各自匹配的 profile；同一 P12 只有在两份 profile 都允许相应证书时才可能复用。主 profile 中的 NE、Personal VPN 和 5 个 Group 不能自动授权扩展。用户无后台权限时，应向有权限的提供方申请/授权扩展 ID 与 profile，不能用 P12 本地伪造。

## 保留边界与未测项目

NEBULA Dashboard/Groups/Theme、Library/Network、PacketTunnelProvider.swift、官方核心 commit/构建配方均与基线无 diff；iCloud 与辅助扩展的功能减项详见 [功能清单](README.md)。无数据库 schema 变更、自动迁移、清空或旧配置删除。

未处理 P12/私钥，没有真实签名、真机安装或 VPN 流量验证。不能声称当前 IPA 可正常安装或使用 VPN。即使日后补齐两份 profile，也需按 [检查清单](RESIGN_CHECKLIST.md) 核对万能签的扩展独立 profile/递归签名能力和实际数据面。具体工具版本未经实测，兼容性 UNVERIFIED。

原完整版分支 `feat/nebula-ui` 保持 `e0f5d16193f8a2c8c464e1c56352cf07105dc647`，既有完整产物不覆盖。官方 App 未被安装、替换或卸载；安装前还必须在本机确认没有其他 App 使用 com.Ekg.IYmq，如提示替换/删除则取消。

编译通过不等于无警告；上游 nullability、既有 Swift 6 actor-isolation/AppIntents 提示等保留在完整日志中，本轮未为消除它们而改动核心/网络实现。本轮没有重做界面或真机验收。
