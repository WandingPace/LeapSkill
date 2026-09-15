# branch_config.json 配置说明

项目组共享的配置文件，随 SVN 提交，所有人共用。**包含所有项目特定的配置**，其他项目适配时只需修改此文件。

## 配置格式

```json
{
  "trunk_url": "http://tc-svn.tencent.com/TIMIJ3/FPSMobile_proj/trunk/CODM_CHN/Client",
  "branch_root_url": "http://tc-svn.tencent.com/TIMIJ3/FPSMobile_proj/branches/CODM",
  "client_subpath": "Client",
  "branch_dir_pattern": "^(?P<date>\\d{8})_svn(?P<branch_rev>\\d+)_WWL(?P<version>[\\d.]+(?:\\+CN[\\d.]+)?)_[\\d.]+(?:_(?P<suffix>[\\w]+))?$",
  "branch_display": {
    "trunk_display_name": "Trunk",
    "branch_display_template": "{version} 分支",
    "branch_display_with_suffix_template": "{version}_{suffix} 分支"
  },
  "suffix_keywords": {
    "体验服": "tiyanfu",
    "tiyanfu": "tiyanfu",
    "临时": "linshi",
    "linshi": "linshi",
    "next": "next",
    "match": "match"
  }
}
```

## 字段说明

### SVN 地址配置

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `trunk_url` | string | ✅ | 主线 SVN 完整地址。用于校验主线目录 |
| `branch_root_url` | string | ✅ | 分支根目录地址，所有分支都在此目录下 |
| `client_subpath` | string | ✅ | 分支目录下的客户端子路径（如 `Client`）。完整分支 URL = `branch_root_url` + `/` + `分支目录名` + `/` + `client_subpath` |

### 分支目录名正则

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `branch_dir_pattern` | string | ✅ | 分支目录名的正则表达式，**必须包含以下命名组** |

**必须的命名组**：

| 命名组 | 必填 | 说明 | 示例值 |
|--------|------|------|--------|
| `date` | ✅ | 拉分支的日期 | `20260403` |
| `branch_rev` | ✅ | 拉分支时的 SVN revision 号 | `1788634` |
| `version` | ✅ | 版本号，用于用户输入匹配和友好名称显示 | `37.1`、`36.1+CN30.1` |
| `suffix` | ❌（可选） | 分支后缀，用于区分正式版/体验服/临时分支等 | `tiyanfu`、`linshi01`、`next` |

**CODM 项目正则匹配示例**：

| 分支目录名 | date | branch_rev | version | suffix |
|---|---|---|---|---|
| `20260403_svn1788634_WWL37.1_31.1` | `20260403` | `1788634` | `37.1` | （无） |
| `20260320_svn1772940_WWL37.1_31.1_tiyanfu` | `20260320` | `1772940` | `37.1` | `tiyanfu` |
| `20260109_svn1708050_WWL36.1+CN30.1_tiyanfu` | `20260109` | `1708050` | `36.1+CN30.1` | `tiyanfu` |
| `20251030_svn1616236_WWL35.1_29.1_tiyanfu01` | `20251030` | `1616236` | `35.1` | `tiyanfu01` |
| `20250909_svn1578658_WWL33.1_27.1_next` | `20250909` | `1578658` | `33.1` | `next` |

### 友好名称显示模板

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `branch_display.trunk_display_name` | string | ✅ | 主线的显示名称（如 `Trunk`） |
| `branch_display.branch_display_template` | string | ✅ | 无后缀分支的显示模板。`{version}` 会被替换为版本号。如 `{version} 分支` → `37.1 分支` |
| `branch_display.branch_display_with_suffix_template` | string | ✅ | 有后缀分支的显示模板。`{version}` 和 `{suffix}` 会被替换。如 `{version}_{suffix} 分支` → `37.1_tiyanfu 分支` |

### 分支类型关键词映射

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `suffix_keywords` | object | ✅ | key=用户可能说的关键词（中文或英文），value=对应的分支 `suffix` 值 |

**匹配规则**：
- 用户提示词中包含某个 key → 要求分支 `suffix` 包含对应的 value
- 用户没有提到任何 key → 要求 `suffix` 为空（正式版分支）

**CODM 项目配置示例**：

| 用户说 | 匹配的 key | 要求 suffix 包含 | `suffix=空` | `suffix=tiyanfu` |
|---|---|---|---|---|
| `37.1` | 无 | 空 | ✅ 正式版 | ❌ |
| `37体验服` | `体验服` | `tiyanfu` | ❌ | ✅ |
| `37 tiyanfu` | `tiyanfu` | `tiyanfu` | ❌ | ✅ |
| `37临时` | `临时` | `linshi` | ❌ | ❌ |

## 其他项目适配

其他项目使用本 skill 时，只需修改此文件，**不需要修改 SKILL.md**：

1. 修改 `trunk_url`、`branch_root_url`、`client_subpath` — 项目的 SVN 地址
2. 修改 `branch_dir_pattern` — 项目的分支目录命名正则（保留 `version` 和 `suffix` 命名组）
3. 修改 `suffix_keywords` — 项目的分支类型关键词映射（如项目没有体验服概念，可设为 `{}`）
4. 修改 `branch_display` — 项目的友好名称显示模板
