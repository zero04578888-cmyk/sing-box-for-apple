# 万能签二签与并存安装步骤

本轮交付是未获开发者签名的 Release IPA。这里是按工具必备功能描述的步骤，不假定未知版本的具体按钮名称或已验证兼容性；能力要求见 SIGNING_REQUIREMENTS.md。

1. 下载 GitHub Actions 的 `nebula-release-unsigned-*` artifact，解压得到 `NEBULA-Release-Unsigned.ipa`。按 SHA256SUMS 校验；不要把 artifact ZIP 本身当 IPA。保留原始 unsigned IPA、inventory、完整 tar 产物和日志。
2. 仅在本地核对材料：Distribution 证书必须有匹配私钥；准备 7 个 Bundle ID 对应的 Ad Hoc profiles。检查同一 Team、有效期、证书许可和目标设备 UDID；分别检查主 App 与 VPN 扩展的 NE 权限、共同 App Group、iCloud 等能力。不要向聊天、仓库、Actions 或公开网页上传材料。
3. 先核对已有 App Store sing-box 的 Bundle ID。选择完全不同的主 ID `A` 与共享 Group `G`，扩展按 `A.extension` 等命名。不能确认不同，或固定 App ID 与原包相同，就停止安装，不删除原 App。
4. 使用确认仅在本机处理材料的万能签版本导入 unsigned IPA。导入证书和密码应为工具的本地操作；不要使用“上传证书在线签名”的网站。无本地材料处理保证时，先停止这一操作。
5. 检查包内全部 6 个扩展，包括 `Extensions/IntentsExtension.appex`。关闭自动删除插件/扩展、删权限、破解/注入等会改变交付内容的选项。若工具不支持保留 ExtensionKit，停止，不以功能缩水包代替完整交付。
6. 按每个 Bundle ID 分别选择 profile；Framework/dylib 递归签名但不使用主 profile 冒充扩展 profile。逐项设置 SIGNING_REQUIREMENTS.md 列出的 BasePackageIdentifier、AppGroupIdentifier、后台任务、FileProvider Group、iCloud/UTType 等运行时字段。仅改主 Bundle ID 不够。无法完成这一映射时，先用自己的 `A` / `G` 重新构建，再进行二签。
7. 签名顺序是内层代码/Framework → 每个扩展 → 主 App。每个组件实际签名的 application-identifier、Team、NE、App Groups/iCloud 必须获其 profile 授权。保留单独的 signed IPA，不覆盖 unsigned 原件。signed IPA 包含敏感 profiles，只保存在受控私有位置，不上传公开仓库、公开 Artifact 或公开安装站。
8. **安装前检查 signed IPA**：完整 7 个组件还在；每个 App/appex 均有对应 embedded.mobileprovision，Bundle ID 和运行时字段已一致；签名检查成功。可在受控 Mac 上运行 `codesign --verify --deep --strict --verbose=2 Payload/sing-box.app` 并逐组件查看 `codesign -d --entitlements :- <bundle>`，用 `security cms -D -i <bundle>/embedded.mobileprovision` 在本地解码核对。不要把输出中的 UDID、证书或 profile 全文发到公开位置。codesign 静态检查不是安装/VPN 证明。
9. 再次确认目标 Bundle ID 与官方 App 不同，才通过工具提供的标准安装功能安装。若出现“替换现有应用”或要求删除官方 App，取消；不允许继续。保持原 App、配置与订阅不变。
10. 打开 NEBULA，确认独立图标/显示名称及空的独立配置空间；再使用用户授权的测试配置执行 DEVICE_VPN_CHECKLIST.md。不要在验证前删除官方 App 或复制其整个共享数据库。

故障处理：安装失败先查每个扩展 profile、Team、证书有效期/撤销状态、设备 UDID、签名格式及能力；启动失败查内嵌 Framework、动态库与运行时字段；VPN provider 不出现/启动失败查 A.extension、NE 权限和 Group。不得通过删 Packet Tunnel、删扩展或伪造 entitlement 获得“安装成功”。

目前没有导入用户签名材料，没有运行万能签，没有生成已签名 IPA，没有安装/覆盖/卸载任何真机 App。
