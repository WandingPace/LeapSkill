---
name: leap-svn-code-helper
description: "CODM SVN 工作流：提交/拉取、主线↔分支覆盖同步、关键字溯源、C#转XLua热修复、外链资源更新。触发：svn提交、svn更新、分支合并、谁提交了、hotfix.lua"

---

# 术语约定（必须遵守）

- **"更新" / "update" / "拉取最新" / "拉一下"** = `svn update`：从**当前工作区对应的 SVN URL**（主线或当前分支）拉取最新版本到本地工作区。**不是**文件覆盖同步、**不是** svn merge、**不跨主线↔分支**。
  - 例：「更新分支 shader 文件夹」= 在分支工作区对该 shader 目录执行 `svn update`，拉分支上别人最新提交的 shader。
  - 默认**不提交**（svn update 本身只更新工作区，不会产生提交）。
  - 仅当用户明确说「同步 / 合并 / 覆盖 / merge / 合入」等词时，才走下面的「文件覆盖同步」流程。
- **"同步 / 合并 / 覆盖 / 合入 / merge"** = 走「SVN 文件覆盖同步助手」流程（主线 ↔ 分支双向覆盖）。
- **"提交"** = `svn commit`，提交信息统一用下面的格式。

# SVN 提交

提交信息统一为
--task=75432594 [leap-AI] 模块: 内容


# SVN 文件覆盖同步助手

支持主线 ↔ 分支双向合并，仅提供**文件覆盖同步**模式（直接拷贝覆盖，不做逐行 merge）。

> 分支目录结构：`H:\BRANCH_AI\Client\Assets\...`（注意有 `Client` 子路径）

⚠️ **风险**：覆盖模式不做逐行合并，目标分支对同一文件的独立修改会被覆盖。

## 总体流程

```
阶段0: 信息收集与校验
  → 阶段1: SVN 信息验证
    → 阶段2: Revision 筛选与确认
      → 阶段3: 文件差异预览
        → 阶段4: 文件覆盖执行
          → 阶段5: 记录 mergeinfo
            → 阶段6: 编译检查
              → 阶段7: 生成报告
```

---

## 阶段0：信息收集与校验

### 0.1 读取配置文件

| 文件 | 路径 | 说明 |
|------|------|------|
| `branch_config.json` | `<skill_dir>/branch_config.json` | 项目组共享，随 SVN 提交，字段详见 `branch_config.schema.md` |
| `user_config.json` | `<skill_dir>/user_config.json` | 用户私有，不提交 SVN，字段详见 `user_config.schema.md` |

关键字段：`trunk_url`、`branch_root_url`、`client_subpath`、`branch_dir_pattern`（含命名组 `date`/`branch_rev`/`version`/`suffix`）、`branch_display`、`suffix_keywords`、`trunk_local_path`、`branch_local_path`、`svn_username`。

**读取流程**：
1. 读取 `branch_config.json`（不存在则提示项目组参照 schema 创建，中断）
2. 读取 `user_config.json`：存在 → 加载并进入 0.2 校验；不存在 → 进入首次配置流程

**首次配置流程**（`user_config.json` 不存在时）：
1. 执行 `svn info <workspace_root> --show-item url 2>&1`，与 `branch_config.json` 匹配判断当前是主线还是分支
2. `向用户提问确认` 让用户确认/补充路径
3. 校验通过后创建 `user_config.json`，并自动加入 `svn:ignore`

### 0.2 校验 SVN 地址（每次必须执行）

```powershell
Test-Path <trunk_local_path>
Test-Path <branch_local_path>
svn info <trunk_local_path> --show-item url 2>&1
svn info <branch_local_path> --show-item url 2>&1
```

校验规则：
- 主线实际 URL 必须等于 `trunk_url`
- 分支 URL 格式：`{branch_root_url}/{branch_dir_name}/{client_subpath}`，用 `branch_dir_pattern` 正则提取 `date`/`branch_rev`/`version`/`suffix`
- 用户提示词中的版本号/类型关键词须与实际分支匹配，不匹配则提示用户 `svn switch`
- 未提分支名 → `向用户提问确认` 确认当前分支

### 0.3 友好名称显示

全程用友好名称代替完整 SVN 地址（模板详见 `branch_config.schema.md`）：
- 主线：`branch_display.trunk_display_name`
- 分支：`branch_display.branch_display_template` 或 `branch_display_with_suffix_template`（替换 `{version}`/`{suffix}`）

### 0.4 收集合并参数

`向用户提问确认` 收集：

1. **合并方向**（提示词已明确则自动识别）：主线 → 分支 / 分支 → 主线
2. **时间筛选**：最近5分钟 / 30分钟 / 2小时 / 今天 / 全部 / 自定义

---

## 阶段1：SVN 信息验证

获取当前用户名（用于后续按作者过滤）：
```powershell
svn auth 2>&1
# 或从 svn log -l 1 解析 author
```

---

## 阶段2：Revision 筛选与确认

> 如果用户已明确指定 revision 范围，直接跳到阶段3。

**步骤：**

1. `向用户提问确认`：只合并我自己的提交 / 合并所有人的提交

2. 计算时间范围并获取候选列表：
   ```powershell
   svn log <source_url> -r <branch_point_rev+1>:HEAD --limit 2000 2>&1
   ```
   - 剔除 `svn:mergeinfo` 中已记录的 revision
   - 按时间筛选（`$now.AddMinutes(-5)` 等）
   - 按作者过滤（如选择"只合并自己"）

3. 获取每个 revision 的详情：
   ```powershell
   svn log -r <rev> -v <source_url> 2>&1
   ```

4. 按提交消息主题分组展示（取 `:` 前第一个词为组名），表格列：#、Revision、日期、提交消息、涉及文件

5. `向用户提问确认`：全部合并 / 调整排除 / 查看详情 / 取消

6. 确认后，对最终选中 revision 涉及的文件执行状态检查：

   ```powershell
   svn status <files...> 2>&1
   svn status -u <files...> 2>&1
   # 内容对比
   $isSame = ((Get-FileHash "<src_file>" -Algorithm MD5).Hash -eq (Get-FileHash "<tgt_file>" -Algorithm MD5).Hash)
   ```

   文件状态标记：`✅ 已同步` / `🔄 有差异` / `➕ 待新增` / `❌ 待删除`

   - 全部已同步 → 提示"无需合并"，提供"记录 mergeinfo 并结束"或"直接结束"
   - 有问题文件 → `向用户提问确认`：自动修复（update/revert）/ 打开目录 / 取消；修复后重新检查
   - 通过 → 进入阶段3

> 💡 通过 `svn merge -c` 执行的合并会自动更新 `svn:mergeinfo`，下次运行时自动过滤已合并 revision；手动复制文件则不会，需用户手动排除。

---

## 阶段3：文件差异预览

汇总选中 revision 的所有变更文件（去重），展示分类表（操作类型 📝/➕/❌、文件路径、源路径、目标路径），分析变更，提示覆盖风险。

`向用户提问确认`：确认执行 / 调整排除 / 取消

---

## 阶段4：文件覆盖执行

```powershell
# M 修改（先 update 确保目标文件是最新版本，再覆盖）
svn update "<tgt_file>" 2>&1
Copy-Item "<src_file>" "<tgt_file>" -Force

# A 新增（父目录不存在时先创建）
Copy-Item "<src_file>" "<tgt_file>" -Force
svn add "<tgt_file>" 2>&1

# D 删除
svn delete "<tgt_file>" 2>&1
```

执行完输出汇总表（覆盖/新增/删除数量及状态）。

---

## 阶段5：记录 mergeinfo（自动执行，不可跳过）

将本次覆盖涉及的 revision 记录到 `svn:mergeinfo`，确保下次运行时不重复出现。

---

## 阶段6：编译检查

扫描冲突标记残留、重复定义等编译问题。

---

## 阶段7：生成报告 & 提交提示

提示用户手动提交，并展示改动列表和回退命令：
```powershell
svn revert -R .   # 在目标目录执行（回退所有改动）
```

---

## 关键注意事项

- PowerShell 中 `svn` 命令输出用 `2>&1` 捕获，行数截取用 `Select-Object -First N`
- 大量冲突文件可用 Python 脚本批量处理，编码优先 `utf-8-sig`，失败用 `gbk`
- 树冲突：`svn resolve --accept working <file>`
- `向用户提问确认` options 有数量限制，revision 过多时分批或提供"全选"选项

---

# SVN 关键字溯源搜索

逐个检查历史 revision 的文件内容，找出**哪个提交引入或删除了某个关键字**（组件名、方法名、字段名等）。

## 执行流程

### 步骤1：收集参数

如用户未提供，`向用户提问确认` 收集：

| 参数 | 必填 | 默认 | 说明 |
|------|------|------|------|
| 目标文件路径 | ✅ | — | SVN 管理的本地文件路径 |
| 搜索关键字 | ✅ | — | 要查找的字符串 |
| 检查数量 | — | 100 | 最多检查最近多少个 revision |
| 仅显示引入提交 | — | 否 | 只显示新增该关键字的提交 |

### 步骤2：执行脚本

```powershell
# 基本用法
python "<skill_dir>/scripts/svn_keyword_search.py" "<file_path>" "<keyword>"

# 常用选项
python "..." "<file_path>" "<keyword>" -n 200             # 检查200个revision
python "..." "<file_path>" "<keyword>" --introduced-only  # 只显示引入提交
python "..." "<file_path>" "<keyword>" -t 30              # 超时30秒/次
```

> 建议先确认当前文件是否包含关键字再运行脚本（大文件每个 revision 需数秒）：
> ```powershell
> Select-String -Path "<file_path>" -Pattern "<keyword>" | Select-Object -First 5
> ```

### 步骤3：汇总展示

脚本输出标记说明：`➕ Added`（引入）、`➖ Removed`（删除）、`✅ Present`（存在未变化）

向用户展示：
1. **引入该关键字的提交**（最重要）：revision、作者、时间、提交信息
2. **所有包含该关键字的提交列表**（按时间倒序）
3. 未找到时提示扩大 `-n` 参数重试

---

# Hotfix 部分

---
name: leap-svn-code-helper
description: .
---

## Purpose

Convert the current SVN user's latest remote C# commit in a CODM `Client` repository into a reviewed XLua hotfix script, and write the final output into `Client/Export/LuaHotFixArchive/Automatic/<latest-version>/#<id>/TestHotFix.lua`.

## Trigger examples

- `@command://hotfix.lua 99`
- `/hotfix.lua 99`
- `根据最近的 SVN C# 提交生成 99 号热修复 Lua`
- `把当前用户最新一条 C# 提交转成 TestHotFix.lua`

## 更新规则（必须遵守）

修改或新增 hotfix 前：

1. **先 `svn update` 热更归档目录**（`Client/Export/LuaHotFixArchive`）：拉取远端最新的版本目录与 hotfix 编号占用情况，避免撞号或写到过期版本目录。更新可能耗时较长（目录大），用后台方式跑并等待完成后再继续。
2. **然后在最新的 WWL 版本目录上加**：
   - 从 `Automatic` 下的版本目录中选最新 WWL 版本（按版本号数值排序，如 `CN33.0_WWL39.0` > `WWL10.0`；`CNxx_WWLyy` 格式以 yy 为准）；
   - 在该版本目录下选可用的 `#<id>` 编号目录（用户指定的 id 已被占用时，明确报告冲突并让用户确认是否换号，不静默覆盖）；
   - 目录命名遵循该版本目录内的现有风格（如 `#35` 或 `#35_0621`）。

## Required operating procedure

1. Parse the numeric hotfix id from the request. Ask for the id only if it is truly missing.
2. Read `references/hotfix_workflow.md` before starting the conversion flow.
3. Read `references/csharp_to_lua_rules.md` before writing Lua code.
4. Determine the real `Client` directory using the workflow reference. Prefer the `QATxt` anchor rule when the workspace follows the CODM layout.
5. Query the current SVN username, resolve the remote SVN URL, and search the **remote** log with `--search <username>`.
6. Use the matching remote C# commit as the only source commit. Do not silently switch to another user's commit.
7. Fetch both `svn diff` and `svn cat` for every changed `.cs` file. Use C# source as the single source of truth.
8. Search `Client/Export/LuaHotFixArchive/Automatic` for previous Lua hotfix examples, but use them only for style and namespace confirmation.
9. Generate XLua hotfix code that preserves method names, signatures, execution order, and branch logic from C#.
10. Add `CS.GameEngine.Log.PublishLog` logs on method entry, key branches, nil checks, important loops, and method exit.
11. Write the final file only to `Client/Export/LuaHotFixArchive/Automatic/<latest-version>/#<id>/TestHotFix.lua`.
12. Verify the written file and report revision, changed files, converted methods, output path, and any review risks.

## Hard rules

- Treat C# source as the **only** truth source.
- Never invent methods, namespaces, or missing logic.
- Never use another user's commit unless the current user has no matching C# commit and explicitly asks to broaden the search.
- Never place the final output outside the latest `Automatic/<version>/#<id>/TestHotFix.lua` path.
- Prefer the workspace-parent embedded Python runtime `../Python/python.exe` when running project Python scripts.
- Treat bundled scripts as helper utilities only; manually verify every critical result.

## Bundled resources

- `references/hotfix_workflow.md`: end-to-end operating workflow and path/output rules.
- `references/csharp_to_lua_rules.md`: detailed C# → Lua conversion rules and pitfall checklist.
- `scripts/svn_diff_parser.py`: helper script for parsing SVN diffs and locating changed methods.
- `scripts/lua_generator.py`: helper script for generating starter XLua hotfix code.

## Expected final response

Return a short execution summary containing:

- SVN revision and author
- Count of changed C# files
- Count of converted methods
- Final `TestHotFix.lua` output location
- Any parts that still need human review

# 外链资源更新

更新哪个地图的外链资源 直接在对应地图目录下新建一个_Temp_[地图名] 文件夹下更新对应外链svn链接的地图,
https://tc-svn.tencent.com/TIMIJ3/FPSMobile_proj/trunk/CODM_CHN/ArtResource/Assets/Scenes_Resource/Map/PVP/[地图名]/


https://tc-svn.tencent.com/TIMIJ3/FPSMobile_proj/trunk/CODM_CHN/ArtResource/Assets/Scenes_Resource/Map/