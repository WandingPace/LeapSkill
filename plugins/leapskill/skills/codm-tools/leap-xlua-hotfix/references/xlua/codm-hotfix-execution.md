# CODM XLua Hotfix 执行与验收

仅在目标工程为 CODM Client，且需要生成、写入、注入或运行验收 Hotfix 时读取。

## 产物与目标包

从当前源码确认 `LuaWorkSpaceRelativePath` 或等价加载入口，再确定开发与注入目录；历史常用的 `Export/LuaHotFixArchive/WorkSpace/` 只作候选。有 TAPD ID 时可使用 `HotFix_<ID>_<short-name>.lua`，没有工作项时使用能唯一表达目标的英文简称。

Hotfix 使用的类型、方法、字段、helper 和枚举必须存在于目标包。通过目标版本源码、SVN 修订或同版本产物确认引入时间；当前主干存在不能证明旧包可用。归档脚本只提供当前版本写法的候选，不能覆盖真实签名。

## 注册语义

- 修复是在原方法前后增加过滤、短路或结果修正时，优先使用项目已证明可回调原方法的 `hotfix_ex`。
- 原实现会产生错误副作用或必须完整替换时使用 `xlua.hotfix`。
- 普通 `xlua.hotfix` 中调用同名方法会递归；`base(self)` 只在项目的 `hotfix_ex` 路径中使用。
- 私有成员或私有方法需要项目先例支持，并在注册前调用 `xlua.private_accessible`。
- 静态方法、显式接口、重载、泛型、构造函数和 `ref/out` 必须按目标版本的真实 XLua 生成与注册方式处理。
- 注册代码不放入仅运行时执行的 `if not HOTFIX_COMPILE` 块；顶层副作用和跨回调强引用必须有明确初始化与清理时机。

## Editor 验收

仅生成或审查 Hotfix 时，默认完成静态签名、Lua 语法和差异检查。用户明确要求注入或运行验收时，按 CODM Editor 验收 Reference 操作目标工程。

进入 PlayMode 后优先使用项目当前支持的 `InjectLuaWorkSpace`。会卸载全部 Hotfix 的入口只有在影响已明确时才使用。先证明脚本真实加载，再触发目标入口并观察能区分补丁的命中证据和用户行为；当前 C# 已包含相同修复时，最终 UI 正常不能单独证明 Hotfix 命中。

分别记录 Hotfix 文件绝对路径、字节数和 SHA-256，以及 Lua 语法、XLua 加载、Hotfix 命中、Editor 功能和 Android/iOS 真机结果。生成、注入、上传、投递、提交和发布是不同动作，分别遵守当前授权。
