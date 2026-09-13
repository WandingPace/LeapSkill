---
name: wizard
description: "Generate an interactive bash wizard to guide humans through manual setup, dashboard, or credential steps. Use when setting up API keys, third-party dashboards, CI secrets, or infrastructure where human authentication is required — even if the user says \"create a setup wizard\". Do NOT use for steps the AI agent can execute autonomously."
---

# 向导

生成结构化的交互式 Bash 向导，引导操作员逐步完成手动仪表板程序、秘密配置和不可逆转的切换操作。

---

## 核心不变量

1. **仅限人类边界**：向导严格适用于需要人工交互身份验证、MFA、计费审批或物理仪表板导航的任务。
2. **不可变帮助程序库**：在“STAGES”标记上方的“template.sh”中保留标准化 UI 帮助程序库；切勿修改内部屏幕清除或秘密屏蔽逻辑。
3. **URL优先导航**：在提示用户输入值或确认之前，始终打开目标 URL (`open_url`)。
4. **屏蔽秘密输入**：对所有 API 令牌、私钥和密码使用 `ask_secret`；将机密直接保存到 `.env` 或 GitHub Secrets (`set_secret`)。
5. **静态语法验证**：在交给用户之前使用“bash -n <script>”和“shellcheck”验证所有生成的向导脚本。

---

## 架构和内容地图 (MOC)

```
[ Manual Dashboard / Credential Prerequisite ] ──► [ Scope Stages & Target Secrets ] ──► [ Generate Wizard from template.sh ] ──► [ Operator Execution ]
```

|组件|责任|参考模板|
|---|---|---|
| **Bash 向导引擎** | UI 助手、秘密提示、.env upsert、GitHub CLI 写入 | `技能/向导/template.sh` |
| **舞台脚手架** |带 URL 触发器的线性步骤序列 | `脚本/setup-*.sh` |
| **验证通过** | Bash 语法检查和试运行 | `bash -n <脚本>` |

---

## 分步程序 (TWI)

### 第 1 步：范围手动阶段和秘密清单
- **操作**：检查 `.env.example`、`.github/workflows/*` 和文档以识别所需的所有手动输入和机密。
- **关键点**：对于每个值，确定：(1) 源 URL/仪表板路径，(2) 目标（`.env`、`gh Secret` 或两者），(3) 秘密可见性。
- **为什么**：彻底的清单可以防止编写不完整的脚本，从而使操作员中途受阻。

### 步骤 2：每个阶段的地图操作员旅程
- **操作**：起草清晰、顺序的说明：单击哪个仪表板菜单、在哪里生成密钥以及填充哪个变量。
- **要点**：澄清确切的 UI 标签（例如“设置 $\rightarrow$ API 密钥 $\rightarrow$ 创建密钥”）。
- **内嵌清单**：
  - [ ] 每个阶段都对应一个单一的重点任务
  - [ ] 根据官方文档验证 URL
  - [ ] 映射到“ask_secret”和“write_env”的秘密输入

### 步骤 3：从 `template.sh` 编写向导脚本
- **操作**：将`skills/wizard/template.sh`复制到目标路径（例如`scripts/setup-provider.sh`），设置`TOTAL_STAGES`，并在标记下方设置创作阶段。
- **要点**：请勿触摸“STAGES”标记上方的辅助功能。
- **为什么**：UI 帮助程序的一致性可确保跨平台（macOS、Linux、WSL）统一、强大的终端行为。

### 步骤 4：验证语法并交付交接
- **操作**：运行 `bash -n <script>` 和 `chmod +x <script>`。为用户提供准确的执行命令。
- **要点**：不要尝试在代理会话内自主运行交互式向导。
- **为什么**：向导需要交互式终端输入和浏览器窗口来阻止自治代理子 shell。

---

## 反合理化护栏

|诱人的合理化|约束规则|工程原理 |
|---|---|---|
| *“生成代理可以通过 CLI 执行的步骤的向导。”* | **直接执行代理支持的步骤；为仅人工任务保留向导。** |强迫人类执行代理可以运行的任务会浪费人类时间。 |
| *“使用标准‘read’提示输入机密，无需屏蔽。”* | **所有敏感凭证的强制“ask_secret”。** |明文秘密提示在终端日志和肩窥中泄漏 API 令牌。 |
| *“尝试在后台子 shell 中执行交互式 bash 向导。”* | **通过执行命令将向导脚本移交给用户。** |后台子 shell 在交互式“read”和“open”调用上无限期挂起。 |

