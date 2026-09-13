---
name: ai-data-remediation
description: "Self-healing data pipeline layer using semantic anomaly clustering, AST-validated lambda transformations, and zero-loss mathematical reconciliation. Use when data quality checks fail, anomalous records break ETL/ELT pipelines, you need automated data cleansing with sandboxed Python transformations, or you want to group data errors into semantic clusters — even if they don't explicitly say \"data remediation\". Do NOT use for standard database schema migrations, routine CRUD queries, or basic pipeline scheduling."
---

# AI数据修复

为关键任务管道数据运行自我修复修复层：拦截损坏或异常数据，协商模式系列，通过本地或盒子语言模型生成确定性修复逻辑，保证并零丢失数据。

## 核心原则

> **人工智能生成可验证的转换逻辑——接口直接接触或改变生产数据。**

---

## 核心不指标

1. **原始数据突变的人工智能逻辑**：模型生成纯粹的、确定性的转换函数，可以进行测试、审查和版本控制。原始模型输出永远不会直接通过管道传输到表中。
2. **强制 AST 静态验证**：每个生成的 lambda 或转换都必须在评估之前通过用于构建命名空间的抽象语法树 (AST) 验证。
3. **严格的零丢失统计**：输入记录总数必须完全等于成功记录加上隔离记录（$\text{Source} = \text{Success} + \text{Quarantine}$）。任何非零增量都会立即停止处理。
4. **气隙/隐私保护执行**：预先标记化或本地执行，敏感或PII数据绝不能传出到外部云API。
5. **人工审查隔离**：转换置信度较低 ($< 0.75$) 或 AST 检查失败的集群将路由到具有完整谱系的隔离隔离表。

---

## 架构和内容地图 (MOC)

```
[ Anomalous Records ] ──► [ Semantic Clustering ] ──► [ Sandboxed Logic Gen ] ──► [ AST Safety Gate ] ──► [ Vectorized Apply ] ──► [ Zero-Loss Audit ]
```

|组件|责任|关键机制|
|---|---|---|
| **异常记录柱** | 标记为“NEEDS_AI”的暂存柱状图 | 暂行平行存表/队列|
| **成型压缩** |将大量异常分组为模式系列|支撑+成型新生儿|
| **逻辑综合** |编译确定性 lambda 函数 | JSON约束输出格式 |
| **AST安全门** |静态代码分析和沙盒执行| Python `ast.parse` + 内置函数 |
| **对本**账目审计| | 记录统计的数学验证严格不指标：$\Delta = \text{源} - (\text{成功} + \text{隔离}) = 0$ |

---

## 分步程序 (TWI)

### 第1步：拦截和隔离异常记录
- **操作**：结果确定的验证层中失败的行提取到隔离的暂存蜡烛中。
- **关键点**：严格在主模式验证下游进行操作，而不是阻止主要食材流。
- **为什么**：解耦修复可保持上游队列的健康并防止系统范围内的背压。

###步骤2：语义异常压缩
- **操作**：计算错误的字符串的逗号表示将它们放入不同的模式组中。
- **关键点**：使用相似性将数千个破碎行压缩为5-15个同类集群。
- **为什么**：综合10个服务级转换函数不需要50,000行逐行LLM调用，可将执行时间和计算成本减少超过95%。

###步骤3：沙盒逻辑生成
- **操作**：将第三方供应商提供纯Python lambda函数的约束语言模型提示。
- **要点**：使用显式输入/输出类型规定将输出为单个 lambda 定义。
- **为什么**：Lambda函数是可重复的，可针对测试套件进行测试，并且在部署前易于检查。

###步骤4：AST安全验证和矢量化应用
- **操作**：静态解析的 lambda AST 生成并在设置环境中跨集群运行。
- **要点**：拒绝任何包含 `import`、`exec`、`eval`、`__builtins__`、文件 I/O 或网络调用的代码。
- **内嵌清单**：
  - [ ] AST 解析验证零个未经授权的节点类型（没有“Import”、“ImportFrom”、“Call”到未经批准的函数）
  - [ ] 转换建信得分$\ge 0.75$
  - [ ] Lambda 通过了 3 个负载样本输入的单元测试断言
  - [ ] 若未验证或失败的记录立即发送至隔离区
- **为什么**：未经检查的动态代码执行会带来严重的安全漏洞，并带来严重的数据库损坏的风险。

###步骤5：损失零协调和沿袭审计
- **操作**：跨输入、输出和隔离表运行数学平衡检查。
- **要点**：验证$\text{源记录} = \text{成功记录} + \text{隔离记录}$。
- **为什么**：无声的行会破坏财务分类、分析仪表板和下游依赖项。

---

## 反合理化护栏

|感应的合理化|约束规则|工程原理|
|---|---|---|
| *“生成的 lambda 看起来很安全，跳过 AST 检查。”* | **对100%生成的代码进行强制AST验证。** | 每个必须会验证的属性访问或系统调用障碍执行权限。
| *“只有3行消失了，无论如何我们还是要运送这批货物。”* | **如果$\Delta \neq 0$则立即停止。** | 沉默的记录会导致重大的审计和财务差异。
| *“让我们直接修复数据字符串而不是生成函数。”* | **生成逻辑，劫持就地改变原始数据。** |逻辑可以审计、单元测试、审查和回滚；原始数据不能修复。
| *“将包含 PII 的完整客户记录发送到公共 API，以便更快修复。”* | **实行数据边界隐私。** | PII 出口违反隐私法规和合规性要求。

---

## 验证和故障排除

- **AST拒绝**：如果模型尝试禁止导入，请收紧系统提示以强制执行纯数学/字符转换。
- **低模型置信度**：将整个模型系列路由到“quarantine_review”表以供人工签核。
- **协调差异**：检查行异常处理程序以确保失败的行在隔离区中被捕获而不是被吞掉。
