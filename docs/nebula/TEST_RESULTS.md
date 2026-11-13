# NEBULA 验证记录

最终受测代码：`cdb1d15ca10c53fc1455364dcd7a5758af9a0aa4`（界面代码保持 81baa05；后续仅增加 CI 捕获与修正产物路径）。后续提交仅更新文档，不改变受测代码。基线：`768b3de2baf2461dd06405cba1b2ca4e39da5ea4`。

## 最终云端结果

[Actions 43380949798](https://github.com/zero04578888-cmyk/sing-box-for-apple/actions/runs/43380949798)：**SUCCESS**，源码与 native 两个 job 均通过。

环境：标准 `macos-15` ARM64 runner；Xcode **26.2 / 17C52**；iOS SDK **26.2**；模拟器 **iPhone 16 Pro Max / iOS 26.2 / arm64**。不使用 larger runner 或付费云部署。

| 检查 | 结果 | 证明范围 |
| --- | --- | --- |
| 源码预检 | PASS | 本地包、Runestone 子模块、scheme、entitlements、字符串目录及 24 个远程锁定包元数据 |
| Python 单元测试 | **11/11 PASS** | Framework 缺失/结构/切片/路径/JSON 与准确模拟器选择边界；fixture 不冒充真实设备 |
| 官方 Libbox | PASS | 固定官方 SHA `824dbcfb4dd0a95921840b1737b950cde590241e`，标签 `v1.15.0-alpha.13`，Go `1.26.10`；版本标签校验后构建，核心源码 diff 检查无修改；最终运行复用已验证缓存 |
| Framework 预检 | PASS | 设备 iOS arm64 + 当前 runner 原生 Simulator 切片，二进制/头文件/module 结构完整 |
| 锁定 SPM 依赖解析 | PASS | 24 个远程包及 2 个本地包实际解析，Package.resolved 未修改 |
| SFI 与内嵌扩展 device 编译 | **PASS** | `generic/platform=iOS`；`CODE_SIGNING_ALLOWED=NO`；日志含 `BUILD SUCCEEDED` |
| 原生 fixture UI 测试 | **3/3 PASS，0 skipped** | 测试结果 JSON 与 xcresult 均记录 Passed，日志含 `TEST SUCCEEDED` |
| 原生截图 | 已捕获并复核 | 6 张 PNG：5 张 1320×2868 手机截图（首页、统计、节点及首页/统计 Accessibility XXXL）与 1 张 iPad Pro 13-inch (M4) 默认字号首页；使用明确标注的预览数据 |

3 项 UI 测试分别覆盖：

1. 首页/统计进入，停止后显示 Disconnected，统计出现 Waiting for live data，旧速率 249 MB/s 不存在，再次启动显示 Connected。这是原有截图 fixture 的状态集成检查，不启动真实隧道。
2. 节点入口、fixture 节点名称及 Dashboard/Statistics/Logs/Tools/Settings 标签保留。
3. Accessibility XXXL 首页/统计渲染；目标名与速率的横向边界在屏幕内。

## 本地检查与边界

编辑主机为 Windows，无 Xcode/Swift/Simulator。源码预检、11 项 Python 测试、21 个修改/新增 Swift 文件的语法解析、YAML/actionlint、补丁空白及基线应用检查均通过。语法解析只证明语法树，云端 Xcode 编译才提供类型与 SDK 编译证据。

本地仍无 `Libbox.xcframework`，完整预检应返回缺失错误；云端按固定官方源构建并验证，未把缺失依赖当作已安装。未提交生成的 Framework 或 DerivedData。

核心/网络/数据库/Network Extension、辅助扩展实现、项目及 entitlements 与基线无改动。界面继续复用既有 start/stop、配置、订阅、远程控制及节点操作链路；这不等于全部功能的真机回归已通过。新增文件未发现私钥、令牌或带凭据 URL 模式；未添加真实订阅、密码或签名材料。模式扫描不能替代完整安全审计。

构建通过但并非零警告：例如 Libbox 生成头文件的 nullability 冲突、部分 target 的 AppIntents metadata 跳过，以及既有 ExtensionProvider 等文件的 Swift 6 actor-isolation 提示。日志保留，未通过改动核心来消除这些警告。

## 截图审查范围

本轮已打开全部 6 张原生 PNG。iPad 捕获是默认字号首页的单一状态，不是平板全流程回归。普通字号页面层级、节点说明文字及选中状态可读；最大辅助字号改为单列，首页品牌/快捷入口纵排；统计页不再横向溢出。大字号首屏只显示部分内容，继续使用原生纵向滚动。

此前因无捕获返回的 `recapture` 不能作为视觉通过依据。补齐 iPad 后的新截图对应上述最终受测代码；独立 finish review 返回 **disposition: ship**，material_fixes: none，仅覆盖这 6 个捕获状态；完整审查报告另附。六张截图不代表横屏、其他状态或全平台视觉验收。

## 故障与修复记录

| 运行 | 代码 | 结果/处理 |
| --- | --- | --- |
| 43361445048 | b7d4670 | Libbox 构建成功；macOS Bash 空数组/nounset 失败，改为非空参数数组 |
| 43362163664 | 73ec25b | 依赖通过；侧栏 ToolbarContentBuilder 缺 iOS 16 可用性声明，补私有方法 @available，保留 iOS 15 回退 |
| 43363727237 | 2d2144c | 10 项检查、完整 device 无签名 build 通过 |
| 43364788814 | 2d2144c | 为补取并校验官方版本标签主动取消；不计 UI 通过 |
| 43365296033 | 9bd00e1 | 官方版本/SHA、Framework、SPM 通过；为修正跨 step 的 Simulator 环境传递主动取消 |
| 43366611476 | 7c2e6bd | device build 通过；UI 2/3 通过。断线统计残留和截图 AX 溢出均保留失败证据后修复 |
| 43371946078 | 64ca261 | device build 通过；为合并截图发现的节点说明对比度修复主动取消 |
| 43373349224 | 81baa05 | device build、10 项源码测试、3 项手机 UI 测试全部通过 |
| 43378230146 | c025495 | device build、11 项源码测试与 3 项手机 UI 测试通过；新增 iPad 捕获误用 SFI.app 产物路径失败，修正为实际 sing-box.app 并检查文件存在 |
| **43380949798** | **cdb1d15** | **最终 device build、11 项源码测试、3 项手机 UI 测试与 iPad 原生捕获全部通过** |

断线统计修复位于负责展示本地数据的 Statistics 内容层：显式观察选中 ExtensionProfile，立即隐藏旧速率；未修改 CommandClient 或协议。节点说明改用 `Color.secondary`，避免继承按钮 tint。测试断言没有削弱。

## 未执行的验证

| 项目 | 状态 |
| --- | --- |
| 手动 VoiceOver、Reduce Motion、增强对比度、中文/长名称全流程 | NOT RUN；源码支持与自动测试不替代人工操作 |
| iPad 全流程/横屏、最低支持 iOS、macOS/tvOS 编译回归 | NOT RUN；只补齐 iPad 默认字号首页捕获，主目标为 iPhone 16 Pro Max |
| 所有异常/权限/订阅失败路径的运行回归 | NOT RUN；既有入口保留，需授权配置与设备验证 |
| Apple Developer 签名、安装、系统 VPN 授权 | NOT RUN |
| 真机代理/VPN、DNS/IPv6、切网、锁屏/后台恢复 | NOT RUN |

Simulator 测试仅使用 ad-hoc 签名，无开发者身份或证书；device 步骤为无签名编译。**没有导出 IPA，也没有“IPA 已能正常使用 VPN”的结论。**

Actions 诊断 artifact 保留 7 天；本地交付另保存摘要、日志和原生 PNG。完整 xcresult 已下载到工作区中间目录，可在 macOS Xcode 打开。
