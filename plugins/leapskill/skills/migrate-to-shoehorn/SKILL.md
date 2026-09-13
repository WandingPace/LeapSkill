---
name: migrate-to-shoehorn
description: "Migrate unsafe TypeScript test assertions to @total-typescript/shoehorn with explicit fixture intent. Use when test files contain unsafe `as` or `as unknown as` typecasts, when mock fixtures break under typechecking, or when modernizing test typing — even if the user says \"fix test type assertions\". Do NOT use for production code types."
---

# 迁移到 Shoehorn

将不安全、脆弱的 TypeScript 测试装置类型转换（“as Type”、“asknown as Type”）从“@total-typescript/shoehorn”安全迁移到意图揭示、类型安全的帮助程序。

---

## 核心不变量

1. **测试代码严格隔离**：`@total-typescript/shoehorn` 严格用于测试套件和测试装置；切勿在生产应用程序代码中导入或使用鞋拔子助手。
2. **特定于意图的助手映射**：
- 仅部分键重要的部分对象 $\rightarrow$ `fromPartial(obj)`
- 故意使用无效/错误的类型进行错误测试 $\rightarrow$ `fromAny(obj)`
- 完全填充的模拟 $\rightarrow$ `fromExact(obj)`
3. **保留自动完成和重构安全**：在所有迁移的测试装置中维护 TypeScript 类型推断和 IDE 自动完成。
4. **自动发现和正则表达式警告**：通过有针对性的 grep (`as [A-Z]`) 发现测试转换；避免可能改变生产代码的盲目全局替换。
5. **强制类型检查绿色**：每个迁移过程都必须以绿色“tsc --noEmit”或等效的存储库类型检查命令结束。

---

## 架构和内容地图 (MOC)

```
[ Unsafe Test Casts (`as Type`, `as unknown as`) ] ──► [ Intent Classification ] ──► [ Replace with Shoehorn Helper ] ──► [ Verify Typecheck ]
```

|不安全模式|鞋拔更换|目标场景|
|---|---|---|
| `{ id: "123" } 作为用户` | `fromPartial<User>({ id: "123" })` |测试只关心大类型中的“id” |
| `{ id: 123 } 与用户一样未知` | `fromAny<用户>({ id: 123 })` |测试错误输入的运行时验证 |
| `completeMock 作为用户` | `fromExact<User>(completeMock)` |显式完整的模拟结构 |

---

## 分步程序 (TWI)

### 第 1 步：使用检测到的包管理器安装依赖项
- **操作**：安装`@total-typescript/shoehorn`作为devDependency（`bun add -d`，`pnpm add -D`，`npm i -D`）。
- **关键点**：检查是否严格添加到 `devDependency` 中。
- **为什么**：防止将测试帮助程序实用程序捆绑到生产版本中。

### 步骤 2：在测试文件中找到不安全的转换
- **操作**：搜索测试文件中的类型断言气味：
````bash
grep -rnE " as [A-Z]| 未知为 " --include="*.test.ts" --include="*.spec.ts" src/
````
- **关键点**：检查周围环境以确定装置是否是部分模拟或故意无效的有效负载。
- **内嵌清单**：
  - [ ] 仅针对测试文件（`*.test.ts`、`*.spec.ts`）
  - [ ] 零生产源文件修改
  - [ ] 每个固定装置的意图分类（“fromPartial”与“fromAny”）

### 第 3 步：替换演员表并导入助手
- **操作**：将 `as Type` 替换为 `fromPartial(...)`，将 `asknown as Type` 替换为 `fromAny(...)`，添加 `import { fromPartial, fromAny } from "@total-typescript/shoehorn"`。
- **为什么**：“fromPartial”记录了缺失字段是故意的，避免了错误的编译器错误，同时保留了类型智能。

### 步骤 4：运行类型检查和测试套件
- **操作**：执行项目的类型检查命令（例如`bun run typecheck`、`pnpm check`、`tsc --noEmit`）并运行测试套件。
- **关键点**：验证测试是否通过并且 TypeScript 发出 0 个错误。
- **为什么**：确保在迁移过程中不会引入微妙的类型契约回归。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“在生产助手中使用鞋拔子来绕过严格类型。”* | **禁止。仅测试代码。** |在生产环境中绕过类型会导致运行时 TypeError 静默崩溃。 |
| *“到处使用‘fromAny’，因为它比‘fromPartial’更容易。”* | **使用 `fromPartial` 来获取有效的部分； `fromAny` 仅适用于无效类型。** |过度使用“fromAny”会禁用自动完成和类型检查的好处。 |
| *“更新测试文件后跳过运行类型检查。”* | **强制绿色型式检查验证。** |轻微的语法错误或缺少通用参数会破坏 CI 构建。 |

