# hotfix.lua 工作流说明

## 适用场景

将 CODM 项目中 `Client` 目录对应的 **当前 SVN 用户最近一次远端 C# 提交** 转译为 XLua 热修复脚本。

典型触发语句：

- `@command://hotfix.lua 99`
- `/hotfix.lua 99`
- `根据我最近的 SVN C# 提交生成 99 号热修复 Lua`

## 输入要求

输入中应包含一个数字序号，用作输出目录中的 `#<序号>`。

## 核心规则

### 1. 只处理当前 SVN 用户的远端提交

必须执行以下链路：

1. 获取当前 SVN 用户名。
2. 获取 `Client` 工作副本对应的远端 URL。
3. 使用远端 URL 查询日志，并通过 `--search <用户名>` 过滤。
4. 从匹配结果中找最近一条包含 `.cs` 修改的提交。

如果当前用户没有符合条件的提交：

- 明确报告给用户；
- 不要自动切换为其他用户的提交；
- 只有在用户明确要求时，才扩大搜索范围。

### 2. 输出路径固定

最终文件必须写到：

```text
Client/Export/LuaHotFixArchive/Automatic/<最新版本目录>/#<用户输入序号>/TestHotFix.lua
```

其中：

- `<最新版本目录>` 必须从 `Automatic` 下现有 `CNxx_WWLxx` 或 `CNxx.x_WWLxx.x` 目录中自动找到最新值；
- 子目录名必须是 `#<序号>`；
- 文件名必须是 `TestHotFix.lua`。

### 2.1 更新规则（必须遵守）

1. **写 hotfix 前先 `svn update` 热更归档目录**（`Client/Export/LuaHotFixArchive`），确保版本目录和 `#<id>` 编号占用情况是最新的，避免撞号或写到过期版本目录。目录大、更新慢，用后台方式跑并等待完成。
2. **选最新 WWL 版本目录**：从 `Automatic` 下的版本目录按版本号数值排序取最新（`CNxx_WWLyy` / `CNxx.x_WWLyy.x` 以 WWL 后的数值为准；纯 `WWLyy` 旧格式与 `CNxx_WWLyy` 新格式并存时以 WWL 数值大的为准）。
3. **编号冲突处理**：用户指定的 `#<id>` 在最新版本目录已存在时，明确报告已占用的修复内容并让用户确认换号或另立后缀目录（如 `#35_0621` 风格），不静默覆盖已有修复。

### 3. 关键分支必须加日志

每个关键方法都应补充：

- 方法入口日志
- nil 检查分支日志
- 关键 if / else 分支日志
- 关键循环节点日志
- 方法正常结束日志

统一使用：

```lua
CS.GameEngine.Log.PublishLog("[HotFix#<序号>] <方法名> - <描述>")
```

禁止使用 `GeneralLog`。

### 4. C# 源码是唯一真相源

- 先看 `svn diff` 确认修改点；
- 再看 `svn cat` 获取完整文件和完整方法体；
- 最后按 C# 逻辑逐行转译 Lua；
- 历史 Lua 只能参考写法，不能替代 C# 真相。

## Client 目录定位

优先使用以下规则定位 `Client`：

1. 从当前工作区向上查找路径中出现的 `QATxt`；
2. 取 `QATxt` 的父目录作为 `Client` 根目录；
3. 如果工作区不是该布局，再读取 `*.code-workspace` 中的相关目录配置；
4. 最后用 `svn info` 验证该目录是否为有效 SVN 工作副本。

## Python 运行约束

如果需要执行项目里的 Python 脚本，优先使用工作区父目录下的嵌入式 Python：

```text
<工作区父目录>/Python/python.exe
```

不要使用系统 `python` / `py` 作为默认执行入口。

## 推荐执行步骤

1. 解析用户输入的热修复序号。
2. 定位 `Client` 目录。
3. `svn update Client/Export/LuaHotFixArchive`（后台执行，等待完成；确认最新版本目录与编号占用）。
4. 获取当前 SVN 用户名。
5. 获取远端 SVN URL。
6. 查询远端最近 500 条日志，并用 `--search <用户名>` 过滤。
7. 找出最近一条包含 `.cs` 文件的提交。
8. 对每个 `.cs` 文件获取 `svn diff -c <rev>` 与 `svn cat -r <rev>`。
9. 识别发生变化的方法与完整方法体。
10. 在 `Automatic` 目录搜索同类 Lua 写法。
11. 结合 `csharp_to_lua_rules.md` 生成 Lua 热修复。
12. 写入标准输出路径。
13. 回读结果并给出简洁总结。

## 输出总结建议包含

- `revision`
- `author`
- 处理的 C# 文件数量
- 转译的方法数量
- 输出文件路径
- 需要人工复核的风险点
