# NEBULA 修改记录

基线：`768b3de2baf2461dd06405cba1b2ca4e39da5ea4`。实施分支：`feat/nebula-ui`。目标验收设备：iPhone 16 Pro Max。

## 设计与页面

- `NebulaTheme.swift`：iOS 专用深蓝黑背景、两级表面、蓝紫强调色、16pt 圆角、16pt 间距和随“增强对比度”调整的边线。
- `NebulaConnectionHero.swift`：首页连接主控区；原生电源按钮、明确的 VPN 状态、已连接时长、节点组和连接明细入口。仅截图模式显示“预览数据”。
- `StartStopButton.swift`：在既有控件上增加 prominent 呈现方式，继续调用原有 start/stop；异步操作进行中防止重复点击，保留错误弹窗和连接通知。克制的状态过渡尊重 Reduce Motion。
- `OverviewView.swift`：保留全部可配置卡片及配置选择/服务重载逻辑，增加主控区；过渡状态仍禁止编辑配置，但连接按钮可单独处理状态。辅助功能字号下成对卡片改为单列。
- `ViewModifiers.swift` / `DashboardCardHeader.swift`：iOS 卡片统一为有边线的深色表面，图标使用统一蓝色；非 iOS 保持原卡片材质分支。
- `UploadTrafficCard.swift` / `DownloadTrafficCard.swift` / `TrafficLineChart.swift`：上传紫色、下载蓝色，等宽数字、标明服务累计流量；无有效数据时显示等待状态，断线时不绘制旧曲线。图表的装饰路径对 VoiceOver 隐藏，速率/数值标签可读。
- `NebulaStatisticsView.swift`：新增统计页，复用当前 CommandClient 的速率、总量、内存、协程和连接计数；本地与远程目标共用既有数据链路；断线/重连时隐藏历史采样并提供等待说明。总量不解释成日/月用量。
- `NavigationPage.swift`：iOS 增加统计页和截图路由，保留原枚举 rawValue、日志、工具、设置与侧栏入口。
- `SFI/MainView.swift`：iOS 全局深色与蓝色 tint；首页已有主按钮，因此仅在其他标签页保留原底部连接附件，远程控制附件不变；侧栏私有方法补充 iOS 16 可用性声明，修复实际无签名编译发现的问题，保留 iOS 15 回退。
- `GroupListView.swift`：保留节点组订阅、选择及测速链路；新增未连接、等待数据和无节点组状态。
- `GroupItemView.swift`：选中节点同时通过色彩、勾选图标、VoiceOver selected trait 表示；Reduce Motion 下关闭选择动画。
- `GroupView.swift`：保留展开/收起与测速，按钮触控目标至少 44pt，组标题使用原生 Button，辅助功能字号下标题与操作分行，节点网格改为单列。
- `ProfileCard.swift` / `ProfileSelectorButton.swift`：保留新增、编辑、更新、分享、导出、扫码/二维码和配置列表；主要图标按钮使用动态字体、44pt 触控区域及可读标签，Reduce Motion 下关闭更新旋转；iOS 配置选择器使用可增高的布局。
- `RemoteDashboardView.swift`：保留远程控制行为；辅助功能字号下卡片也改为单列。
- `Localizable.xcstrings`：增加 23 个界面文案键及简体/繁体中文翻译；未覆盖的既有语言使用英文源文案回退，既有翻译未覆盖重写。

## 云端回归后修正

- Statistics 的本地内容显式观察 ExtensionProfile，停止后立即隐藏旧流量；远程目标继续使用共享 CommandClient，保持原数据边界。
- 最大辅助字号下连接区品牌/快捷入口纵排，底部控件高度随字号变化，隐藏冗余状态/计数视觉文本但保留可读语义，修复原生截图发现的横向溢出。
- 节点协议说明使用语义 `Color.secondary`，修复按钮 tint 导致的低对比度；fixture 类型名称改为规范小写，预览节点页明确标注 Preview data。
- 界面候选代码 `81baa05` 在 Actions `43373349224` 完成 10 项检查、device 无签名编译和 3 项原生 UI 测试；后续文档提交不改变受测代码。
- 补齐 iPad Pro 13-inch (M4) 原生首页捕获；将 Simulator 选择器扩展为准确机型选择，补充第 11 项测试。修正 target 名与产物名差异后，最终 CI `cdb1d15` / Actions `43380949798` 的编译、11 项源码检查、3 项手机 UI 测试与 iPad 捕获全部通过。Swift UI 保持 `81baa05`，没有为捕获改动界面。

## 构建与交接

- `.github/workflows/ios-unsigned.yml`：源文件检查 → macOS runner/Xcode 检查 → 固定版本 Libbox 构建及切片检查 → 锁定 SPM 依赖解析 → SFI 和内嵌扩展无签名编译。可手动开启 iPhone 16 Pro Max 模拟器界面测试；保留日志及 xcresult，不导出 IPA。
- `ci/libbox.json`：记录官方源仓库、固定 commit、版本标签、Go 版本与兼容性验证范围。构建官方依赖不更改内核、协议或 Go 源文件。
- `ci/preflight.py`、`select_xcode.py`、`select_simulator.py`：验证源码元数据、Framework 结构和平台切片，选择已安装的合格 Xcode 和准确设备；缺失时明确失败，不伪装成功。
- `ci/build_libbox.sh`：隔离官方依赖构建配方，补取并校验官方版本标签指向固定 commit，保留原版本/Beta 元数据；通过切片预检后立即缓存 Framework，后续 UI/应用编译失败不必重建内核依赖。
- `ci/test_simulator.py`：使用模拟的 simctl 清单验证最低运行时、准确机型、已有类型创建实例的选择边界；不冒充设备测试。
- `ci/test_preflight.py`：针对缺失/不完整 Framework、平台架构不符、路径越界、重复 JSON 键等预检边界的测试。
- `SFIUITests/NebulaUITests.swift`：使用原有截图 fixture 的启停状态、断线统计、节点入口、原标签页保留和大字号截图检查；不导入真实订阅、不执行真实 VPN 测试。
- `.gitignore`：忽略本地签名材料、私钥文件、环境变量文件及构建中间物。
- `README.md`：加入 NEBULA 源码、设计、验证和构建文档的入口，保留原许可全文。
- `PRODUCT.md`、`DESIGN.md`、`.impeccable/design.json`、本目录文档：产品约束、设计规范、源码分析、验证记录与后续步骤。

## 保持不变的边界

`Library/Network`、`Library/Database`、所有 Network Extension、系统扩展、其他辅助扩展、Libbox 内核、协议实现、Runestone 子模块、Xcode 项目/entitlements 均未改动。完整文件改动以补丁及交付清单为准。共享视图中的触控/字号改进也会影响 macOS/tvOS 对应视图；这些平台未运行验证。
