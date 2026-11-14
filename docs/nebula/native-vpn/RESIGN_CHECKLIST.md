# 万能签兼容性与真机验收检查清单

当前 **BLOCKED：未取得 VPN 扩展独立 profile**。不运行 P12 云端签名，不进行设备安装。工具版本未知；以下是所需能力检查，不是已验证的万能签菜单或成功记录。

唯一目标 Team：`QCBW52C8MV`。扩展 ID 仍为计划值，不代表 Apple 已授权。

## 材料门槛

- [ ] 主 App 的 Ad Hoc profile 确实匹配 app.turquoise204.lynx5076，允许所用 Distribution 证书和目标设备。
- [ ] 已向有后台权限的提供方取得 app.turquoise204.lynx5076.extension 独立 Ad Hoc profile；该 ID 获 NE 和同一 Group 授权。
- [ ] 两份 profile 的 Team、证书、设备、有效期、NE、App Group 与实际签名 entitlements 一致。
- [ ] 私钥在用户信任的本地环境中，未发送到公开仓库、Actions、在线签名网站或聊天。

在前四项未满足前，不开始安装，不宣称“可正常安装和 VPN 可用”。

## 工具兼容性

- [ ] 解压 Artifact 后导入真正的 NEBULA-NativeVPN-StartupFix-Unsigned.ipa，而非外层 ZIP；先校验 SHA-256。
- [ ] 保留主 App、PlugIns/Extension.appex、Library.framework 及全部资源，不用删除 VPN 扩展来“修复安装”。
- [ ] 为两个 Bundle ID 分别指定或保留正确 profile；不能对两者强制套用主 profile。工具 GUI 只有一个主选择框本身不说明支持/不支持，关键是能否实际正确处理扩展自己的 profile。
- [ ] 递归签名 Library.framework 等内层代码、Packet Tunnel，最后签主 App；同一 Team/证书体系，符合当前 iOS 签名格式要求。
- [ ] 保持主/扩展 CFBundleIdentifier、BasePackageIdentifier、AppGroupIdentifier 一致；provider 仍为 app.turquoise204.lynx5076.extension，Group 仍为 group.43f7b1421047676b.1。
- [ ] 保留每个组件的 packet-tunnel-provider 和共同 Group；不伪造 profile 中未允许的能力，不“忽略权限错误”。requested-entitlements/ 只是源码请求，不是 profile。
- [ ] 不改成官方 App 的 Bundle ID，不注入未知动态库，不选择自动删除扩展或上传签名材料的选项。
- [ ] 生成的 signed IPA 只在私有本地保存，因为其中包含敏感 profiles；不上传公开 Artifact/安装站。

上述能力未经本轮实测，万能签兼容性为 **UNVERIFIED**。如果工具无法为两个组件提供正确的独立 profile/签名/entitlements，即不满足本项目要求，不能用一份 profile 代替。

## 数据与并存

新 Bundle ID 和新 Group 使用独立配置容器，不自动访问、搬运或删除旧容器。需要的配置只能由用户在本地导出再导入，不放公开构建产物。

## 两份 profile 齐备后的真机验收

- [ ] 安装前检查本机已有 App ID；如提示替换/删除任何原 App，取消。保留原完整版与 App Store App 的数据。
- [ ] 两个组件与 Framework 签名验证通过；冷启动无动态库/Group 权限错误。
- [ ] 使用授权测试配置，完成系统 VPN 授权，确认真实 Packet Tunnel provider 已启动。
- [ ] 连接、连接中取消、断开、重连、按需连接与系统状态一致，失败可恢复。
- [ ] 实测代理出口、规则、直连、TCP/UDP、DNS、IPv4/IPv6、切网、弱网、后台/锁屏恢复。
- [ ] 节点切换/测速、订阅更新、本地配置导入/导出、路由和 DNS 按测试配置工作；流量统计真实，断线不显示旧速率。
- [ ] 明确记录 iCloud、辅助扩展、SSID/BSSID 和组播相关功能的精简限制；不外推未测配置。

日志须脱敏；保存构建 SHA、IPA SHA-256、iOS/工具版本、PASS/FAIL/未测。编译、打包、App 打开或系统 Connected 都不是 VPN 数据面验证。
