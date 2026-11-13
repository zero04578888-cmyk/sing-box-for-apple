# NEBULA 验证记录

## 已执行的本地检查

环境：Windows；无 Xcode、Swift 编译器或 iOS Simulator。

| 检查 | 结果 | 证明范围 |
| --- | --- | --- |
| 初始 Git 工作区 | PASS | feat/nebula-ui，基线 commit 已记录，修改前干净 |
| 源码依赖预检 `python ci/preflight.py --source-only` | PASS | 本地 SPM 包/Runestone、scheme、entitlements、字符串目录 JSON、24 个远程 SPM 锁定 revision |
| `python -m unittest discover -s ci -p 'test_*.py' -v` | PASS，7 项 | 预检器对缺失 Framework、缺失二进制/头文件、设备与模拟器架构、目录越界、重复 JSON 键的处理；fixture 不是真实 Framework |
| 19 个修改/新增 Swift 文件的 Tree-sitter 语法解析 | PASS | 语法树无 ERROR/missing 节点；**不是 Swift 编译、类型检查或 API 可用性验证** |
| 工作流 YAML 解析、actionlint 1.7.12 | PASS | YAML 和 GitHub Actions 静态语法检查；不是云端执行成功 |
| `git diff --check` | PASS | 补丁空白格式 |
| 新增文件私钥/令牌/带凭据 URL 模式扫描 | PASS | 未发现这些模式；不等于通用 Secret 检测或人工审计 |
| 补丁应用检查 | PASS | 能应用于基线 commit 的独立临时 Git index |
| 核心/网络/数据库/扩展/项目配置边界 diff | PASS | 受保护目录无改动；不是 VPN 行为回归测试 |

## 明确未通过或未执行

| 项目 | 状态 | 原因/下一证据 |
| --- | --- | --- |
| 完整 Framework 预检 `python ci/preflight.py` | **FAIL（已确认缺失）** | 本地缺少 Libbox.xcframework；脚本正确返回非零，不能视为完整依赖齐备 |
| SPM 远程解析/二进制下载 | NOT RUN | 需要 macOS/Xcode 实际解析，锁文件不能代替下载验证 |
| 固定版本官方 Libbox 构建及 API 兼容性 | NOT RUN | CI 配置已提供，尚无运行日志；相同版本号本身不证明 API 一致 |
| SFI/内嵌扩展无签名 Xcode 编译 | NOT RUN | 本机无 Xcode；上游仓库无写权限且尚无获准的可写目标 |
| 新增 3 项 XCUITest | NOT RUN | 需要 Simulator 切片、准确设备/运行时；已有 snapshot 模式是界面 fixture，不是真实 VPN |
| iPhone 16 Pro Max 原生截图和视觉审查 | NOT RUN | 无模拟器/真机；没有把浏览器或生成图片当作 SwiftUI 运行证据 |
| VoiceOver、Reduce Motion、最大字号的人工检查 | NOT RUN | 源码有相应支持，仍需设备操作确认 |
| macOS/tvOS 应用编译与回归 | NOT RUN | 本轮聚焦 iOS，无对应运行环境 |
| 签名、授权、真机 VPN、DNS/IPv6/切网/后台恢复 | NOT RUN | 需要用户的开发者签名与设备验证；无签名编译无法证明这些能力 |

## 原生视觉验收门槛

独立界面审查返回 **disposition: recapture**：缺少 iPhone 16 Pro Max 和 iPad 的原生设备截图。预期证据为 `.impeccable/review/phone.png` 与 `tablet.png`；需要画面完整、内容可见、非空白的实际 Simulator/设备捕获。源码设计规范和 HTML 色样不是原生渲染证据。当前不做视觉通过结论。

## 云端记录

尚未创建运行。当前上游 `SagerNet/sing-box-for-apple` 为只读；连接账号 `zero04578888-cmyk` 没有同名 fork。需要选定可写目标，公开发布源码的选择由用户确认后执行。无证书、私钥、密码或真实订阅信息被新增到仓库。
