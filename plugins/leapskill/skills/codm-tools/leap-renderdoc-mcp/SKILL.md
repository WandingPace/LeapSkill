---
name: leap-renderdoc-mcp
description: "用于通过 renderdoc-mcp MCP 工具分析 RenderDoc .rdc 抓帧，包括黑屏、视觉异常、帧结构、具体 draw、GPU 渲染和性能问题。不用于仅比较常量缓冲区；该场景应使用 leap-rdc-debug-diff。"
---

# RenderDoc MCP

使用 `renderdoc-mcp` 分析 GPU 抓帧并诊断渲染问题。

调用工具时始终使用名为 `renderdoc-mcp` 的 MCP server。

当 MCP 工具范围外需要 shell 或批处理流程时，使用 `PATH` 中的 `renderdoc-cli`。

## 分析框架

每次分析任务都遵循以下流程：

```text
1. 理解目标 -> 用户想知道什么？
2. 打开并收集 -> 加载抓帧并并行收集上下文
3. 路由 -> 选择正确的诊断流程
4. 执行 -> 每一步都边验证边下钻
5. 总结 -> 结合证据展示结论
```

## 阶段 1：打开抓帧并收集上下文

### 打开抓帧

从文件打开：用 `.rdc` 路径调用 `open_capture`。

从应用打开：调用 `capture_frame` 启动应用、注入 RenderDoc、抓取一帧并自动打开。

验证：检查返回的 event 数量。如果为 `0`，说明抓帧为空，应立即报告。

错误恢复：
- `open_capture` 失败时，确认路径存在且指向有效的 `.rdc` 文件。
- `capture_frame` 失败时，检查可执行文件路径、应用是否需要管理员权限、是否立即退出，以及是否需要增大 `delayFrames`。

### 初始上下文收集

抓帧打开后，并行调用以下互不依赖的工具：

| 工具 | 提供的信息 |
|------|-------------------|
| `get_capture_info` | API、GPU、驱动、event 数量 |
| `get_stats` | 各 pass 的 draw 和三角形数量、头部 draw、最大资源 |
| `get_log` | 校验错误和调试消息；优先检查 HIGH 级别 |
| `list_passes` | 帧结构：pass 名称和 draw 数量 |

继续分析前先总结：
- 当前使用哪个图形 API？
- 有多少个 pass 和 draw？
- 是否存在 HIGH 级别的校验错误？
- 哪些 pass 或 draw 最昂贵？

后续分析以该总结作为工作上下文。

## 阶段 2：路由到诊断流程

根据用户目标选择流程：

| 用户目标 | 流程 |
|-----------|----------|
| “屏幕是黑的”或“没有渲染” | 黑屏诊断 |
| “颜色不对”或“有视觉异常” | 视觉异常诊断 |
| “性能差”或“太慢” | 性能分析 |
| “解释这一帧做了什么” | 帧流程讲解 |
| “调试这个具体 draw call” | 指定 draw 检查 |
| “对比两份抓帧”或“两帧之间变化了什么” | 帧回归诊断 |
| 通用或目标不明确的请求 | 询问用户想调查什么 |

## 诊断流程

### 黑屏诊断

```text
list_draws
  draws = 0?
    -> 没有提交几何体。检查：
       - 用 list_events 查看 Clear 或 Dispatch event
       - 用 get_log 查看 pipeline 创建或绑定错误
       - 报告“No draw calls found”及可能原因
  draws > 0?
    -> 对最后一个 draw 并行执行 goto_event 和 get_pipeline_state
       没有绑定 render target？
         -> 报告输出没有落到任何目标
       已绑定 render target？
         -> export_render_target
            render target 有内容？
              -> 可能是 Present 或 swapchain 问题；检查 Present 相关 event
            render target 是黑的？
              -> 检查绑定和 shader：
                 - get_bindings
                 - get_shader ps
                 - get_shader vs
```

并行机会：`goto_event` 和 `get_pipeline_state` 指向同一个 `eventId` 时可以并行执行。

### 视觉异常诊断

```text
从用户信息或导出 render target 找到有问题的 draw
  -> 对该 draw 执行 goto_event
  -> 并行执行 get_pipeline_state 和 get_bindings
     - 检查 blend state
     - 检查 render target 格式
     - 检查绑定纹理
     - 需要时导出可疑纹理
     - 检查 shader：
       - get_shader ps mode=disasm
       - get_shader ps mode=reflect
       - 需要查找相似 shader 时使用 search_shaders
```

如果有多个可疑 draw，列出候选 event ID 和名称，导出它们的 render target，再询问用户哪个表现不正确。

### 性能分析

```text
从 get_stats 开始
  -> 按三角形数量检查头部 draw
  -> 对高开销 draw 执行 goto_event 和 get_draw_info
  -> 用 get_pipeline_state 检查 pipeline 复杂度
  -> 用 get_shader vs/ps mode=reflect 检查 shader 反射
  -> 用 get_resource_info 检查过大资源
  -> 用 get_pass_info 检查最重的 pass
  -> 查找 shader 和资源相似的多余 draw
```

按影响排序报告问题。每项都要说明问题是什么、出现在哪里、严重程度，以及可能的改进方向。

### 帧流程讲解

```text
list_passes
  -> 对每个重要 pass：
     - get_pass_info
     - 对第一个 draw 并行执行 goto_event 和 get_pipeline_state
     - 描述 pass 输入、shader 和输出
     - 用 export_render_target 展示 pass 结果
  -> 最后按从开始到结束的顺序讲解
```

并行机会：当多个 pass 是独立分析任务时，可并行检查两到三个。

### 像素级诊断

调查某个像素颜色错误或缺失时：

1. **pick_pixel**：读取当前像素颜色，确认问题。
2. **pixel_history**：找出哪些 draw 修改了该像素，并检查是否有 draw 被剔除或丢弃。
3. **debug_pixel**：跟踪片元 shader 执行，定位错误值的来源。
4. **get_texture_stats**：检查输入纹理的范围是否异常（NaN、全零等）。

### Shader 调试

某个 draw 输出错误时：

1. 先用 **debug_vertex** 或 **debug_pixel**、`mode="summary"` 跟踪 shader 执行。
2. 输入看起来不对时，用 **get_bindings** 检查绑定。
3. 逻辑看起来不对时，改用 `mode="trace"` 逐步执行。

### 帧回归诊断

对比两份抓帧以定位渲染差异时：

1. `diff_open` captureA captureB：加载两份抓帧。
2. `diff_summary`：快速判断是否存在差异，并检查 `divergedAt` 字段。
3. `diff_draws`：哪些 draw 发生变化、新增或删除？
4. `diff_pipeline "MarkerPath"`：该 draw 的 pipeline state 发生了什么变化？
5. 带 `diffOutput` 的 `diff_framebuffer`：执行像素级视觉对比。
6. `diff_close`：清理资源。

### 指定 draw 检查

用户指定 event ID 或 draw 名称时：

```text
并行执行 goto_event、get_pipeline_state 和 get_bindings
  -> 描述：
     - 用 get_shader vs mode=reflect 检查顶点 shader
     - 用 get_shader ps mode=reflect 检查像素 shader
     - 从 bindings 获取绑定纹理
     - 从 pipeline state 获取 render target
     - 从 pipeline state 获取 viewport
  -> 需要时继续深入：
     - get_shader vs/ps mode=disasm
     - export_render_target
     - export_texture
     - get_draw_info
```

## 验证检查点

在整个分析过程中执行以下检查：

| 此步骤之后 | 验证 |
|----------------|--------|
| `open_capture` 或 `capture_frame` | event 数量大于 0 |
| `get_log` | 先调查 HIGH 级别消息 |
| `list_draws` | draw 数量符合预期 |
| `get_pipeline_state` | 已绑定 shader 且存在 render target |
| `get_bindings` | 预期资源已绑定且不为 null |
| `get_shader` 返回空 | 该 event 可能没有绑定此阶段；尝试其他 stage 或 event |
| `export_render_target` | 图像没有异常地全黑或全白 |
| 每个阶段 | 总结已发现、已排除的内容和下一步 |

## 错误恢复

| 错误 | 恢复方式 |
|-------|----------|
| `open_capture` 找不到文件 | 确认路径，必要时向用户索取正确文件 |
| `open_capture` 文件无效 | 文件可能损坏或不是 `.rdc`；要求重新抓帧 |
| `capture_frame` 应用立即退出 | 检查 `cmdLine`、`workingDir` 和启动要求 |
| `capture_frame` 没有抓到帧 | 增大 `delayFrames`，并确认应用确实渲染到窗口 |
| `get_shader` 返回空 | 该 event 的此 stage 没有绑定 shader；尝试其他 stage 或 event |
| `get_pipeline_state` 没有 render target | 部分 draw 不输出到 render target；检查 draw flags |
| `export_render_target` 索引越界 | 检查绑定了多少 render target，并使用 `0` 到 `7` 的有效索引 |
| `get_resource_info` 的 `ResourceId` 无效 | 先调用 `list_resources` 获取有效 ID |
| 任意工具提示没有打开抓帧 | 先调用 `open_capture` |

## 何时询问用户

出现以下情况时先询问再继续：
- 多个 draw call 都可能是问题来源。
- 分析存在歧义，需要用户确认最可能的假设。
- 收集初始上下文后，用户目标仍不明确。
- 已找到可能根因，但继续缩小范围前需要确认。

以下情况不要询问：
- 下一步诊断已经明确。
- 采集更多数据能明显缩小问题范围。
- 导出图像或纹理能提供更好的证据。

## 工具参考

### 会话

| 工具 | 用途 |
|------|---------|
| `open_capture` | 加载 `.rdc` 文件进行分析 |
| `capture_frame` | 启动应用、注入 RenderDoc、抓取一帧并自动打开 |

### 导航和 Event

| 工具 | 用途 |
|------|---------|
| `list_events` | 列出所有 event，包括 draw 和非 draw |
| `list_draws` | 仅列出 draw call |
| `goto_event` | 导航到 event 并更新当前状态 |
| `get_draw_info` | 获取单个 draw call 的详细信息 |

### Pipeline 和绑定

| 工具 | 用途 |
|------|---------|
| `get_pipeline_state` | 检查绑定 shader、render target、depth state 和 viewport |
| `get_bindings` | 检查常量缓冲区、纹理、UAV 和 sampler |

### Shader

| 工具 | 用途 |
|------|---------|
| `get_shader` | 获取反汇编或反射信息 |
| `list_shaders` | 列出唯一 shader 及其使用次数 |
| `search_shaders` | 搜索 shader 反汇编文本 |

### 资源和 Pass

| 工具 | 用途 |
|------|---------|
| `list_resources` | 列出 GPU 资源，可附加过滤条件 |
| `get_resource_info` | 详细检查单个资源 |
| `list_passes` | 列出 render pass 及其 draw 数量 |
| `get_pass_info` | 列出单个 pass 内的 draw |

### 信息和诊断

| 工具 | 用途 |
|------|---------|
| `get_capture_info` | 检查 API、GPU、驱动和 event 数量 |
| `get_stats` | 检查各 pass 明细、头部 draw 和大资源 |
| `get_log` | 检查调试和校验消息 |

### 导出

| 工具 | 用途 |
|------|---------|
| `export_render_target` | 将当前 event 的 render target 导出为 PNG |
| `export_texture` | 将纹理资源导出为 PNG |
| `export_buffer` | 将 buffer 数据导出为二进制文件 |

### 像素和调试

| 工具 | 关键参数 | 用途 |
|------|----------------|---------|
| `pixel_history` | `x`、`y`、`eventId`（可选）、`targetIndex`（可选） | 查询某个像素在指定 event 之前被哪些 draw 修改；包含 shader 输出、混合后数值和 pass/fail 状态 |
| `pick_pixel` | `x`、`y`、`eventId`（可选）、`targetIndex`（可选） | 读取单个像素的 RGBA 值；返回 float、uint 和 int 表示 |
| `debug_pixel` | `eventId`、`x`、`y`、`mode`（summary/trace）、`primitive`（可选） | 调试某个像素的片元 shader；summary 返回输入输出，trace 增加逐步执行 |
| `debug_vertex` | `eventId`、`vertexId`、`mode`（summary/trace）、`instance`（可选）、`index`（可选）、`view`（可选） | 调试指定顶点的顶点 shader；支持 summary 或完整 trace |
| `debug_thread` | `eventId`、`groupX/Y/Z`、`threadX/Y/Z`、`mode`（summary/trace） | 按 workgroup 和线程坐标调试 compute shader 线程 |
| `get_texture_stats` | `resourceId`、`mip`（可选）、`slice`（可选）、`histogram`（可选）、`eventId`（可选） | 获取像素最小值和最大值，并可返回 256 桶 RGBA 直方图；适合检测 NaN 或全零纹理 |

### Shader 热编辑

| 工具 | 用途 |
|------|---------|
| `shader_encodings` | 列出支持的 shader 编译编码 |
| `shader_build` | 编译 shader 源码并返回 shaderId |
| `shader_replace` | 用已构建 shader 替换指定 event/stage 的 shader |
| `shader_restore` | 将单个 shader 恢复为原始版本 |
| `shader_restore_all` | 恢复所有已替换 shader 并释放资源 |

### 扩展导出

| 工具 | 用途 |
|------|---------|
| `export_mesh` | 将变换后的顶点数据导出为 OBJ 或 JSON |
| `export_snapshot` | 导出完整 draw 状态（pipeline、shader 和 render target） |
| `get_resource_usage` | 查询资源在所有 event 中的使用方式 |

### CI 断言

| 工具 | 用途 |
|------|---------|
| `assert_pixel` | 以可配置容差校验像素 RGBA 值 |
| `assert_state` | 校验 pipeline state 字段是否符合预期值 |
| `assert_image` | 逐像素比较两份 PNG |
| `assert_count` | 校验资源、draw 或 event 数量 |
| `assert_clean` | 校验没有超过指定严重级别的调试消息 |

### Diff / 对比

| 工具 | 关键参数 | 用途 |
|------|----------------|---------|
| `diff_open` | `captureA`、`captureB` | 打开两份抓帧进行并排对比 |
| `diff_close` | — | 关闭 diff 会话并释放资源 |
| `diff_summary` | — | 多级检查后的高层摘要；检查 `divergedAt` 字段 |
| `diff_draws` | — | 使用 LCS 对齐比较 draw call 序列；报告变化、新增和删除的 draw |
| `diff_resources` | — | 比较两份抓帧的 GPU 资源列表 |
| `diff_stats` | — | 比较两份抓帧的逐 pass 统计 |
| `diff_pipeline` | `marker` | 比较 marker path 标识的匹配 draw 的 pipeline state |
| `diff_framebuffer` | `eidA`、`eidB`、`target`（可选）、`threshold`（可选）、`diffOutput`（可选） | 执行像素级 render target 对比，可输出差异图 |
