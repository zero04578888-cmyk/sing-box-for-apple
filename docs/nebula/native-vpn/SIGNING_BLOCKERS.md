# QCBW52C8MV 双组件签名要求

唯一目标团队为 `QCBW52C8MV`，使用用户指定的分发证书，不再使用旧团队证书或旧 Group。

| 项目 | 主 App | Packet Tunnel |
| --- | --- | --- |
| Bundle ID | app.turquoise204.lynx5076 | app.turquoise204.lynx5076.extension |
| application-identifier | QCBW52C8MV.app.turquoise204.lynx5076 | QCBW52C8MV.app.turquoise204.lynx5076.extension |
| 共同 Group | group.43f7b1421047676b.1 | group.43f7b1421047676b.1 |
| 所需 profile | 主 App 专用 Ad Hoc | 独立扩展 Ad Hoc，不能复制主 profile |
| NE | packet-tunnel-provider | packet-tunnel-provider |
| 当前证据 | 主 profile 的内容、证书与 Group 已本地审计；安装前仍核对撤销和设备 | 未取得匹配 profile，ID 仅为计划值 |

两份 profile 均须允许同一张用户指定分发证书、目标 iPhone UDID、共同 Group、所需 NE 能力，并在有效期内。Framework 递归签名，但不额外需要 profile；Personal VPN 不替代扩展授权。

主 profile 不授权任意后缀。提供方须在 Q 团队注册/授权扩展 ID 并签发独立 profile；本项目和万能签不能用 P12 在本地生成 Apple 授权。缺少开发者后台权限且提供方无法补齐时，原生 VPN 签名仍阻塞。

## 无签名构建与二签

CI 不接受 P12、密码、profile 或真实订阅，只写入身份请求配置、生成无签名产物与验证报告。intendedSigningTeamID 不表示已签名。

二签时分别选择主/扩展正确 profile，保留 Library.framework、PlugIns、资源和必要权限。不复制一份 profile 到两处，不删扩展、不构造 Group。导出 signed IPA 后在本地检查 CodeDirectory、证书、profile、XML/DER Entitlements、Bundle ID 和 Group，再做安装与 VPN 验收。

## 数据与并存

只使用新 Group，不读取、迁移或删除旧容器。保留旧分支、完整版和官方 App。安装前确认同 Bundle ID 的已有 App，不通过自动卸载/覆盖其他 App 解决问题。signed IPA 含敏感 profiles，只在本地保存，不公开上传。

当前最小请求为 NE + Group，iCloud 和辅助扩展限制保持不变。编译通过、错误界面出现或系统 Connected 都不能代替出口、DNS、路由、切网和后台恢复测试。

## Apple 参考

- [Ad Hoc profile](https://developer.apple.com/help/account/provisioning-profiles/create-an-ad-hoc-provisioning-profile/)
- [Entitlements 与授权](https://developer.apple.com/library/archive/technotes/tn2415/)
- [Network Extension](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.networking.networkextension)
