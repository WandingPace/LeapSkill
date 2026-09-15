# user_config.json 配置说明

每个用户私有的本地配置文件，首次运行 skill 时自动创建，**不提交 SVN**。

## 配置格式

```json
{
  "trunk_local_path": "E:\\Trunk",
  "branch_local_path": "F:\\Branch",
  "svn_username": "linclin",
  "last_merge_mode": "file_overwrite",
  "last_updated": "2026-04-07T10:19:00"
}
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `trunk_local_path` | string | ✅ | 主线工程的本地目录路径 |
| `branch_local_path` | string | ✅ | 分支工程的本地目录路径 |
| `svn_username` | string | ✅ | SVN 用户名，用于"只合并自己的提交"过滤 |
| `last_merge_mode` | string | ❌ | 上次选择的合并模式，用于模式选择时标注"⭐ 上次使用" |
| `last_updated` | string | ❌ | 配置最后更新时间（ISO 8601 格式） |

### last_merge_mode 取值

| 值 | 含义 | 显示名称 |
|----|------|---------|
| `"svn_merge"` | SVN Merge 精细合并模式 | SVN Merge 模式 |
| `"file_overwrite"` | 文件覆盖同步模式 | 文件覆盖同步模式 |
| `""` 或不存在 | 未记录（首次使用） | 不标注任何模式 |

## 自动管理

- **创建**：首次运行 skill 时，校验通过后自动创建
- **svn:ignore**：创建时自动将 `user_config.json` 加入 `svn:ignore`，防止误提交
- **更新**：路径或用户名变更时自动更新；`last_merge_mode` 在合并正式执行时更新，取消流程不更新
- **校验失败**：不写入文件，保留旧配置
