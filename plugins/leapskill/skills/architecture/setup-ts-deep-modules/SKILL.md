---
name: setup-ts-deep-modules
description: "Enforce TypeScript package boundaries, entry points, and cyclic dependency rules with dependency-cruiser. Use when structuring monorepo packages, establishing public API entry points, or preventing circular imports — even if the user says \"fix TS package boundaries\"; 中文用户常会要求“修复 TS 包边界”“禁止循环依赖”或“设置 monorepo 公共入口”。Do NOT use for non-TypeScript repositories."
---

# 配置 TypeScript 深度模块边界

使用 dependency-cruiser 配置和验证跨 TypeScript 包的严格深度模块边界，确保公共接口仅存在于包根文件中，而私有实现保持密封在子目录中。

---

## 核心不变量

1. **根文件作为独占入口点**：外部调用者和消费者只能导入包根文件（`index.ts`，`client.ts`，`server.ts`）；所有子目录（`lib/`、`internal/`、`tests/`）都是私有的。
2. **四个严格的依赖关系规则**：强制 (1) 入口点边界，(2) 包内内部自由，(3) 仅测试导入入口点，(4) 零依赖循环。
3. **强烈不建议使用 barrel 文件**：公开集中的多个根入口点，而不是重新导出整个子树的巨型桶文件。
4. **强制验证规则会拦截违规**：在完成设置之前，故意引入禁止的深度导入，以验证 `lint:boundaries` 是否快速失败。
5. **无推测路径别名**：直接通过 dependency-cruiser 进行边界检查，而不是更改 `tsconfig.json` 路径或构建复杂的构建时层。

---

## 架构和内容地图 (MOC)

```
src/packages/
  <package-name>/
    index.ts          ◄── Public Entry Point (exported to other packages)
    client.ts         ◄── Additional Public Entry Point
    lib/              ◄── Private Implementation (sealed from outsiders)
    tests/            ◄── Tests (import only root entry points)
```

|规则|标识|目标|
|---|---|---|
| **应用侧入口边界** | `entrypoint-boundary-from-app` |应用/根代码只能导入包根入口点 |
| **测试入口边界** | `tests-through-entrypoints` |测试只能通过根入口点导入包 |
| **循环依赖预防** | `no-circular` |禁止所有循环依赖 |
| **验证门** | `lint:boundaries` 脚本 |违规时自动 CI 失败 |

---

## 分步程序 (TWI)

### 第 1 步：检测环境和包管理器
- **操作**：检测包管理器（`bun.lockb`$\rightarrow$bun、`pnpm-lock.yaml`$\rightarrow$ pnpm、`yarn.lock`$\rightarrow$yarn、其他 npm）并找到包根目录（`src/packages` 或 `packages`）。
- **要点**：检查现有的`.dependency-cruiser.*`配置以合并规则而不是覆盖。
- **为什么**：保留现有的项目包管理器标准可确保与当前 CI 脚本的零摩擦。

### 步骤 2：安装和配置 Dependency Cruiser
- **操作**：安装 `dependency-cruiser` 作为 devDependency 并将 `dependency-cruiser.config.cjs` 复制到 `.dependency-cruiser.cjs` 并更新 `PACKAGES_ROOT`。
- **要点**：使用 `.cjs` 扩展名，以便 CommonJS 在 ESM / `"type": "module"` 项目中无缝导出功能。
- **内嵌清单**：
  - [ ] 包管理器正确识别
  - [ ] “dependency-cruiser”已添加到“devDependencies”
  - [ ] `.dependency-cruiser.cjs` 配置了核心边界规则

### 步骤 3：连线脚本和脚手架清理示例
- **操作**：将 `"lint:boundaries": "depcruise <packages-root>"` 添加到 `package.json` 并创建一个示例深度包：
- `<packages-root>/example/index.ts` （公共入口点委托给 `lib/`）
- `<packages-root>/example/lib/impl.ts`（隐藏实现）
-`<packages-root>/example/tests/example.test.ts`（导入`../index`）
- **为什么**：参考包可作为开发人员的实时文档和入门模板。

### 步骤 4：验证规则会拦截违规
- **操作**：执行三个验证过程：
1. 运行 `lint:boundaries` $\rightarrow$ 必须在干净的存储库上**通过**。
2. 在测试 $\rightarrow$ 中添加深度导入 `import { impl } from "../lib/impl"` 必须 **FAIL**。
3. 恢复深度导入并运行 `lint:boundaries` $\rightarrow$ 必须 **PASS**。
- **关键点**：在没有观察到故意测试失败的情况下，切勿签署边界规则。
- **为什么**：未经验证的 linter 配置可能出现语法或 glob 错误，最终什么也没检查却全部通过。

### 步骤 5：文档包约定和代理指针
- **操作**：创建解释布局和规则的 `<packages-root>/README.md`，并在 `AGENTS.md` / `CLAUDE.md` 中添加单行上下文指针。
- **要点**：明确解释为什么不鼓励使用桶文件。
- **为什么**：代理指针确保未来的自治会话从第一个提示开始就尊重包边界。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“跳过测试规则是否因错误导入而失败。”* | **强制 三步验证（通过 $\rightarrow$ 失败 $\rightarrow$ 通过）。** |具有无效 glob 配置的 Linter 会静默地通过，而不执行任何操作。 |
| *“通过巨大的根index.ts桶导出所有子模块。”* | **不要使用巨型 barrel 文件。** |巨大的桶会破坏树摇动并创建隐藏的循环导入依赖项。 |
| *“为了方便起见，在单元测试中直接从 lib/ 导入。”* | **仅通过公共入口点执行测试。** |测试中的深度导入将测试套件与不稳定的内部重构紧密结合起来。 |
