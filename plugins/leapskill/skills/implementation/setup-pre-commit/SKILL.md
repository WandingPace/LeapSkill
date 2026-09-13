---
name: setup-pre-commit
description: "Configure pre-commit quality checks with Husky and lint-staged while preserving package manager conventions. Use when setting up git pre-commit hooks, automated formatters, staged linters, or typecheck gates — even if the user says \"add pre-commit hooks\"; 中文用户常会要求“添加 pre-commit 钩子”“配置 Husky 和 lint-staged”或“提交前自动格式化”。Do NOT use for continuous integration (CI) pipeline setup."
---

# 配置 Git pre-commit 钩子

使用 Husky、“lint-staged”和 Prettier 安装和配置确定性 Git 预提交质量关卡，保留现有存储库包管理器和构建脚本。

---

## 核心不变量

1. **包管理器保真度**：检测并使用存储库的本机包管理器（`bun`、`pnpm`、`yarn`、`npm`）；不要引入冲突的锁定文件。
2. **仅暂存格式**：通过“lint-staged”和“--ignore-unknown --write”严格针对暂存文件运行 Prettier，以防止未暂存的代码漂移。
3. **存储库范围的类型检查和测试**：在 `lint-staged` 成功后，在 `.husky/pre-commit` 内执行完整的类型检查和单元测试。
4. **保留现有配置**：如果存在`.prettierrc`或现有Husky钩子，则安全地合并脚本而不会覆盖用户规则。
5. **强制冒烟测试提交**：通过暂存所有配置更改并执行经过验证的测试提交来验证整个挂钩管道。

---

## 架构和内容地图 (MOC)

```
[ Git Commit Attempt ] ──► [ .husky/pre-commit Hook ]
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
  [ lint-staged ]             [ Typecheck Gate ]          [ Unit Test Gate ]
  - Prettier format           - `npm run typecheck`       - `npm run test`
  - Staged files only         - Full project types        - Unit/Integration pass
```

|组件|责任|配置文件|
|---|---|---|
| **Husky引擎** | Git 挂钩管理器 v9+ | `.husky/pre-commit` |
| ** lint 阶段** |专门针对分阶段更改运行格式化程序 | `.lintstagedrc` |
| **Prettier** |代码风格标准化| `.prettierrc` |

---

## 分步程序 (TWI)

### 第 1 步：检测包管理器并检查现有设置
- **操作**：检测锁文件（`bun.lockb` $\rightarrow$ Bun，`pnpm-lock.yaml` $\rightarrow$ pnpm，`yarn.lock` $\rightarrow$yarn，其他 npm）。
- **要点**：检查是否已安装 `prettier`、`lint-staged` 或 `husky`。
- **为什么**：重用现有的依赖项可以防止包膨胀和锁文件流失。

### 步骤 2：安装 DevDependency 并初始化 Husky
- **操作**：安装 `husky`、`lint-staged` 和 `prettier` 作为 devDependency，然后运行 ​​`npx husky init`。
- **要点**：验证 `"prepare": "husky"` 是否已添加到 `package.json` 中。
- **内嵌清单**：
  - [ ] 安装在 `devDependencies` 中的依赖项
  - [ ] 创建了`.husky/`目录
  - [ ] `package.json` 中存在 `prepare` 脚本

### 步骤 3：编写 `.husky/pre-commit` 和 `.lintstagedrc`
- **操作**：配置 `.husky/pre-commit`：
````bash
npx lint-staged
npm run typecheck
npm run test
````
*（使“npm”适应检测到的包管理器，如果脚本不存在，则省略“typecheck”/“test”）。*
- **要点**：使用 `{"*": "prettier --ignore-unknown --write"}` 创建 `.lintstagedrc`。
- **为什么**：`prettier --ignore-unknown` 在格式化所有支持的文本格式时安全地忽略二进制文件和图像。

### 步骤 4：冒烟测试和初始提交
- **操作**：暂存所有创建的挂钩文件并运行 `git commit -m "Add pre-commit hooks (husky + lint-staged + prettier)"`。
- **要点**：确认提交触发了预提交钩子并通过了所有阶段。
- **为什么**：实时提交执行证明挂钩是可执行的并且配置正确。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“在每次提交时在整个存储库中运行Prettier。”* | **通过“lint-staged”严格在暂存文件上运行 Prettier。** |每次提交时的完整存储库格式化都会减慢开发人员的工作流并污染差异。 |
| *“跳过预提交中的类型检查和测试步骤以使其更快。”* | **在预提交中包括类型检查和快速测试。** |在推送之前在本地捕获类型错误可以防止远程 CI 构建损坏。 |
| *“在 pnpm 或 Bun 存储库中使用 npm 命令。”* | **严格匹配检测到的包管理器命令。** |不匹配的包管理器会创建重复的锁定文件和损坏的安装。 |
