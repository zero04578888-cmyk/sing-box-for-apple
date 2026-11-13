# NEBULA 下一步

## 云端无签名验证

1. 选定有写权限的 GitHub 仓库。官方上游为只读；可在自己的账号创建公开 fork，或指定已有仓库。公开 fork 会公开本次源码改动；私有仓库的 macOS runner 可能消耗计费额度，执行前需确认。
2. 将已审查的 `feat/nebula-ui` 分支提交到该仓库。工作流的 push 触发器会先进行源码检查，再开始 macOS 构建。也可通过 Actions 页面手动运行 **NEBULA unsigned iOS**。
3. 首次使用 `run_ui_tests=false`。工作流必须先找到 Xcode >=26.2；然后按 `ci/libbox.json` 的固定官方 commit 和 Go 版本构建 iOS arm64 Framework，不改内核源码。首次构建可能耗时较长。
4. 检查 Libbox 和 SPM 日志。若官方依赖的下载、源码构建或 Swift 接口不兼容，先记录具体错误及版本；不要为消除错误而删减 VPN 功能或用空壳 Framework 代替。
5. SFI 与所有内嵌扩展使用 `CODE_SIGNING_ALLOWED=NO` 等标志编译。不创建签名钥匙串，不读取证书或真实订阅，不导出 IPA。下载 `nebula-validation-*` 的日志和 `Unsigned-iOS.xcresult` 后才能记录编译 PASS。
6. 编译通过后，用 `run_ui_tests=true` 再运行工作流，构建所需 Simulator 切片，在已安装的 **iPhone 16 Pro Max** 上执行 `NebulaUITests`。若该设备或运行时未安装，会明确失败；应补齐环境后再测，不替换成别的设备冒充通过。
7. 从 `Nebula-UI.xcresult` 读取实际截图。当前测试涵盖节点页和大字号首页/统计页；正式视觉验收还需补齐默认字号、各种 VPN 状态、无配置/无节点、订阅更新失败、长节点名、VoiceOver、增强对比度和 Reduce Motion。iPad 在原工程支持范围内，也需要独立捕获/验收。

公开仓库的标准 GitHub 托管 runner 通常不计费，仍以账号/组织当前 Actions 政策为准。本工作流不选 larger runner，不进行任何付费云服务部署。

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
