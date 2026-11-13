# NEBULA 下一步

## 已完成与重跑

公开 fork：[zero04578888-cmyk/sing-box-for-apple](https://github.com/zero04578888-cmyk/sing-box-for-apple)，默认分支 `feat/nebula-ui`。已推送改动，官方上游保持只读。

[最终运行 43380949798](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43380949798) 在代码 `cdb1d15ca10c53fc1455364dcd7a5758af9a0aa4` 上完成：11 项源码测试、无签名 device 编译及 3 项 iPhone 16 Pro Max fixture UI 测试均通过，另完成 iPad Pro 13-inch (M4) 的默认字号首页原生捕获。当前无需等待云端验证。

后续修改代码后，在 fork 的 Actions 页面手动运行 **NEBULA unsigned iOS**：`run_ui_tests=false` 仅检查源码/依赖/device 编译；`true` 另构建 Simulator 切片并运行准确型号的原生 UI 检查。新变更需要新的运行证据，不沿用本次结论。

工作流选用已安装 Xcode >=26.2，按 `ci/libbox.json` 固定的官方 SHA/标签/Go 构建核心依赖，校验锁定 SPM；不修改内核。依赖不存在或下载失败时明确失败，不能以空壳 Framework 代替。device 使用 `CODE_SIGNING_ALLOWED=NO`；Simulator 单独 ad-hoc 签名。日志、结果摘要、xcresult、PNG 作为 `nebula-validation-*` artifact 保留 7 天，不导出 IPA。

公开仓库标准 runner 的计费以 GitHub 账号政策为准。本工作流不选择 larger runner，也不部署付费云服务。

## 后续界面检查

当前截图使用原有 fixture，明确标注 Preview data。目标手机的普通字号首页/统计/节点与最大辅助字号首页/统计已捕获复核。继续补测中文、长节点名、无配置/无节点、订阅更新失败、全部 VPN 过渡状态，以及手动 VoiceOver、增强对比度、Reduce Motion。已另捕获 iPad Pro 13-inch (M4) 默认字号首页；iPad 全流程、横屏及 macOS/tvOS 仍需独立验证，不能从已有截图推断通过。

## macOS 本地复现

先准备与 `ci/libbox.json` 对应的完整 Libbox.xcframework，并初始化子模块：

```sh
git submodule update --init --recursive
python3 ci/preflight.py --check-xcode
xcodebuild -resolvePackageDependencies -project sing-box.xcodeproj -scheme SFI \
  -onlyUsePackageVersionsFromResolvedFile -skipPackagePluginValidation
xcodebuild build -project sing-box.xcodeproj -scheme SFI -configuration Debug \
  -destination 'generic/platform=iOS' -skipPackagePluginValidation \
  CODE_SIGNING_ALLOWED=NO CODE_SIGNING_REQUIRED=NO CODE_SIGN_IDENTITY= DEVELOPMENT_TEAM=
```

需要固定工具链的完整依赖构建步骤见 `.github/workflows/ios-unsigned.yml`；Go 版本、Xcode 版本、平台切片和官方 commit 都应记录。不要把生成的 Framework/DerivedData、证书或个人配置提交进 Git。

## 签名与真机门槛

无签名编译成功后，仍需用户在受控环境中配置自己的 Apple Developer Team、唯一 Bundle ID、App Groups、Network Extension entitlements，以及各内嵌扩展的 provisioning。证书/私钥/密码仅使用本地钥匙串或受控 Secret；不提交进代码和测试 fixture。

在 iPhone 16 Pro Max 上完成：安装与系统 VPN 授权、连接/取消/断开、节点切换、订阅与配置更新、规则/系统代理选项、DNS/IPv4/IPv6、Wi-Fi/蜂窝切换、锁屏/后台/前台恢复、错误路径与现有工具入口。测试应使用用户授权的配置并保存脱敏日志。

**只有完成相应签名与真机验证，才能对该构建声称 VPN 可用。当前没有可用 IPA 的结论。**

## 本地变更保留与回退

原始基线和全部改动保存在交付补丁。应用补丁前在干净分支运行 `git apply --check`；若基线不同，应逐项解决冲突。不要用覆盖整个工程的方式抹掉其他开发者的修改。回退应针对本次提交或补丁，不触及用户配置数据。
