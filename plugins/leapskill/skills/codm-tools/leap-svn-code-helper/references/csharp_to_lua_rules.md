# C# 到 Lua 转译规则

## 🎯 经验总结（2026-02-05 更新）

本次热修复开发过程中总结的关键教训：

### 最严重的错误：自创方法名
- ❌ 把 `UpdateVestData()` 写成了 `RefreshShoppingCarMachine()`
- **教训**：必须严格按照 C# 源码翻译，不能添加任何 C# 中不存在的代码

### 命名空间错误（共 4 处）
| 错误写法 | 正确写法 | 教训 |
|---------|---------|------|
| `CS.PVE.EBREquipmentSlotType` | `CS.GameBase.EBREquipmentSlotType` | 枚举在 GameBase |
| `CS.GameBase.EventManager` | `CS.GameEngine.EventManager` | EventManager 在 GameEngine |
| `CS.GameUI.GameUIEventEnum` | `CS.GameBase.GameUIEventEnum` | 事件枚举在 GameBase |
| `CS.PVE.PVEMACHINE_TYPE` | `CS.PVE.MP.PVEMACHINE_TYPE` | PVE 相关类在 PVE.MP |

### 验证命名空间的正确流程
1. **首先**：搜索历史 Lua 代码 `findstr /s /r /i "类名" "...\CN29.0_WWL35.0\*.lua"`
2. **其次**：搜索 C# 定义 `findstr /s /r "public.enum.类名" "...\*.cs"`
3. **最后**：查看 namespace `findstr /n "namespace" "找到的文件"`

### 生成代码的正确流程
1. `svn cat` 获取完整 C# 源码
2. `svn diff` 确认实际修改点
3. **逐行翻译** C# 为 Lua，不添加任何额外代码
4. 每个类/枚举都要验证命名空间

---

## 🚨 核心原则（最高优先级）

### 1. C# 代码为唯一真相源

**历史 Lua 代码只能参考写法风格，不能完全照抄！**

必须遵循以下流程：
1. **首先**：确保 C# 原始代码能够编译通过
2. **然后**：根据 C# 代码的实际签名和逻辑进行转译
3. **最后**：参考历史 Lua 代码的**写法风格**（如命名空间、工具类调用方式等）

```
❌ 错误流程：直接复制历史 Lua 代码
✅ 正确流程：C# 代码 → 理解逻辑 → 参考风格 → 生成 Lua
```

### 2. 方法签名必须与 C# 一致

历史 Lua 代码可能存在 bug 或过时的写法，**必须核对 C# 原始方法签名**：

```csharp
// C# 方法签名
public List<uint> GetAllSubTask(uint actvId, uint seqId)
```

```lua
-- ❌ 错误（历史代码可能只传了一个参数）
local allSubtask = game.CommonMgr:GetAllSubTask(task.SeqId)

-- ✅ 正确（与 C# 签名一致）
local allSubtask = game.CommonMgr:GetAllSubTask(task.ActvId, task.SeqId)
```

### 3. 参考历史代码的正确用途

| 可以参考 | 不能照抄 |
|---------|---------|
| 命名空间写法 `CS.GameEngine.xxx` | 方法参数数量/类型 |
| 工具类调用方式 `CS.GameUI.UICommonTools.SafeSetActive` | 业务逻辑实现 |
| 类型转换语法 `cast(obj, typeof(...))` | 条件判断/分支逻辑 |
| 泛型创建方式 `CS.System.Collections.Generic.List(Type)()` | 循环遍历范围 |

### 4. 命名空间必须查证 C# 源码

**不要假设命名空间！** 必须通过搜索 C# 代码确认类的实际命名空间：

```lua
-- ❌ 错误：猜测命名空间
CS.GameBase.DataStoreManager.Instance
CS.GameBase.GamePlay.Game
CS.PVE.EBREquipmentSlotType.Vest

-- ✅ 正确：查证后的命名空间
CS.GameEngine.DataStoreManager.Instance
CS.GameEngine.GamePlay.Game
CS.GameBase.EBREquipmentSlotType.Vest  -- EBREquipmentSlotType 在 GameBase 命名空间
```

**查证方法**：
1. 搜索 `public enum ClassName` 或 `public class ClassName` 找到定义文件
2. 查看该文件顶部的 `namespace` 声明
3. 使用命令：`findstr /s /r "public.enum.TypeName" "H:\Client\Assets\Scripts\*.cs"`

**⚠️ 这是核心规则，命名空间错误会导致运行时报错！**

---

## 📍 命名空间映射（已验证）

以下命名空间经过本次调试验证：

| C# 类 | Lua 完整路径 | 备注 |
|------|-------------|------|
| `GamePlay.Game` | `CS.GameEngine.GamePlay.Game` | 不是 GameBase |
| `GamePlay.MapID` | `CS.GameEngine.GamePlay.MapID` | |
| `GamePlay.GetPawn` | `CS.GameEngine.GamePlay.GetPawn` | |
| `DataStoreManager.Instance` | `CS.GameEngine.DataStoreManager.Instance` | 不是 GameBase |
| `EventManager.Instance` | `CS.GameEngine.EventManager.Instance` | ⚠️ 在 GameEngine，不是 GameBase |
| `Log.PublishLog` | `CS.GameEngine.Log.PublishLog` | |
| `UICommonTools` | `CS.GameUI.UICommonTools` | |
| `DMZGame` | `CS.DmzGame.DMZGame` | |
| `DMZCampTask` | `CS.Network.DMZCampTask` | 不是 DmzGame |
| `UnityTool` | `CS.UnityTool` | 全局命名空间 |
| `GameObject` | `CS.UnityEngine.GameObject` | |
| `EBREquipmentSlotType` | `CS.GameBase.EBREquipmentSlotType` | 在 GameBase 命名空间 |
| `GameUIEventEnum` | `CS.GameBase.GameUIEventEnum` | ⚠️ 在 GameBase，不是 GameUI |
| `MPPawn` | `CS.PVE.MP.MPPawn` | |
| `MPVEGame` | `CS.PVE.MP.MPVEGame` | |
| `PVEShoppingMachine` | `CS.PVE.MP.PVEShoppingMachine` | ⚠️ 在 PVE.MP，不是 PVE |
| `PVEMACHINE_TYPE` | `CS.PVE.MP.PVEMACHINE_TYPE` | ⚠️ 在 PVE.MP，不是 PVE |

---

## 🔄 类型转换

### cast() 函数（全局函数）

```lua
local game = CS.GameEngine.GamePlay.Game
cast(game, typeof(CS.DmzGame.DMZGame))

-- 之后可以直接访问子类属性
if game ~= nil and game.CommonMgr ~= nil then
    -- ...
end
```

**注意**：
- 使用全局 `cast()`，不是 `xlua.cast()`
- `xlua.cast()` 会报错！

---

## 📦 泛型类型创建

### 单层泛型

```lua
-- List<T> - 使用函数调用语法
local taskList = CS.System.Collections.Generic.List(CS.Network.DMZCampTask)()

-- 添加元素
taskList:Add(task)

-- 遍历（从 0 开始）
for i = 0, taskList.Count - 1 do
    local item = taskList[i]
end
```

### 嵌套泛型 List<List<T>>

```lua
-- 先获取内层类型
local listType = typeof(CS.System.Collections.Generic.List(CS.Network.DMZCampTask))

-- 创建外层 List
local sortedList = CS.System.Collections.Generic.List(listType)()

-- 创建并添加内层 List
local innerList = CS.System.Collections.Generic.List(CS.Network.DMZCampTask)()
innerList:Add(task)
sortedList:Add(innerList)

-- 插入到指定位置
sortedList:Insert(0, innerList)
```

**注意**：不能使用字符串语法创建嵌套泛型：
```lua
-- ❌ 错误：会报 "No such type"
CS.System.Collections.Generic["List`1[System.Collections.Generic.List`1[...]]"]()
```

---

## 🛠️ 常用工具类

### UI 操作

```lua
-- 安全设置 Active（使用 UICommonTools）
CS.GameUI.UICommonTools.SafeSetActive(gameObject, true)
CS.GameUI.UICommonTools.SafeSetActive(gameObject, false)

-- 安全设置 Label
CS.GameUI.UICommonTools.SafeSetLabel(label, "text")
```

### Transform 操作

```lua
-- 重置本地 Transform（使用 UnityTool）
CS.UnityTool.ResetLocalTransform(transform)

-- 设置父节点
item.transform.parent = parentTransform
```

### 日志输出

```lua
-- ✅ 正确：使用 PublishLog
CS.GameEngine.Log.PublishLog("[HotFix#XX] message")

-- ✅ 带变量的日志
CS.GameEngine.Log.PublishLog("[HotFix#99] count = " .. tostring(count))

-- ❌ 禁止：不要使用 GeneralLog
CS.GameEngine.Log.GeneralLog(...)  -- 禁止！
```

**⚠️ 所有日志统一使用 `PublishLog`，禁止使用 `GeneralLog`！**

### GameObject 操作

```lua
-- 实例化
local itemObj = CS.UnityEngine.GameObject.Instantiate(template)

-- 获取组件
local itemComp = itemObj:GetComponent(typeof(CS.GameBase.SomeComponent))
```

---

## 🔧 HotFix 函数选择

### xlua.hotfix - 完全替换

```lua
xlua.hotfix(CS.Namespace.ClassName, 'MethodName', function(self, arg1, arg2)
    -- 完全替换原方法，不调用原实现
end)
```

### hotfix_ex - 可调用原方法

```lua
require 'xlua.util'.hotfix_ex(CS.Namespace.ClassName, 'MethodName', function(self, arg1, arg2)
    -- 可以调用原方法
    self:MethodName(arg1, arg2)
    -- 然后添加额外逻辑
end)
```

---

## ⚠️ 重要注意事项

### 1. 私有成员访问（重要！）

**`xlua.private_accessible` 的使用规则：**

| 场景 | 是否需要 | 说明 |
|------|---------|------|
| 热修复当前类，访问**当前类**的私有成员 | ❌ **不需要** | xlua.hotfix 已经可以访问当前类的所有成员 |
| 热修复当前类，访问**其他类**的私有成员 | ✅ **需要** | 必须对被访问的类声明 `xlua.private_accessible` |

**示例 - 正确用法**：

```lua
-- 热修复 ClassA 的方法，访问 ClassA 自己的私有成员
-- ❌ 错误：不需要对当前类声明
xlua.private_accessible(CS.Namespace.ClassA)  -- 多余！
xlua.hotfix(CS.Namespace.ClassA, 'Method', function(self)
    local value = self.m_privateField  -- 直接访问即可
end)

-- ✅ 正确：不需要声明，直接访问
xlua.hotfix(CS.Namespace.ClassA, 'Method', function(self)
    local value = self.m_privateField  -- xlua.hotfix 已经可以访问当前类的私有成员
end)
```

```lua
-- 热修复 ClassA 的方法，但需要访问 ClassB 的私有成员
-- ✅ 正确：需要对被访问的外部类 ClassB 声明
xlua.private_accessible(CS.Namespace.ClassB)  -- 必须！因为要访问 ClassB 的私有成员
xlua.hotfix(CS.Namespace.ClassA, 'Method', function(self)
    local classB = self:GetClassB()
    local privateValue = classB.m_internalData  -- 访问 ClassB 的私有成员
end)
```

**总结**：
- **当前类** = 被 `xlua.hotfix` 修复的那个类
- **外部类** = 当前类以外的其他类
- 只有访问**外部类**的私有成员时才需要 `xlua.private_accessible`

### 2. 方法调用语法

- 实例方法用 `:` → `obj:Method()`
- 静态方法/属性用 `.` → `CS.Class.StaticMethod()`
- 属性访问用 `.` → `obj.Property`

### 3. 数组/List 索引

C# 从 0 开始，Lua 中访问 C# 集合也从 0 开始：

```lua
for i = 0, list.Count - 1 do
    local item = list[i]
end
```

### 4. nil 检查

Lua 中 C# 的 null 会变成 nil，需要显式检查：

```lua
if obj ~= nil then
    -- 安全访问
end
```

### 5. 字符串拼接

```lua
-- Lua 字符串拼接用 ..
local msg = "prefix" .. tostring(value) .. "suffix"

-- C# String.Format
local str = CS.System.String.Format("{0}/{1}", a, b)
```

---

## 🐛 历史踩坑记录

### 踩坑 1：xlua.cast vs cast

```lua
-- ❌ 错误：xlua.cast 不存在
local game = xlua.cast(baseGame, typeof(CS.DmzGame.DMZGame))

-- ✅ 正确：使用全局 cast 函数
local game = CS.GameEngine.GamePlay.Game
cast(game, typeof(CS.DmzGame.DMZGame))
```

### 踩坑 2：命名空间 GameBase vs GameEngine

```lua
-- ❌ 错误：GameBase 下没有这些类
CS.GameBase.GamePlay.Game
CS.GameBase.DataStoreManager.Instance
CS.GameBase.EventManager.Instance

-- ✅ 正确：在 GameEngine 命名空间
CS.GameEngine.GamePlay.Game
CS.GameEngine.DataStoreManager.Instance
CS.GameEngine.EventManager.Instance
```

### 踩坑 3：方法参数数量

```lua
-- ❌ 错误：历史代码只传了一个参数
game.CommonMgr:GetAllSubTask(task.SeqId)

-- ✅ 正确：C# 方法需要两个参数
game.CommonMgr:GetAllSubTask(task.ActvId, task.SeqId)
```

### 踩坑 4：Task 类型命名空间

```lua
-- ❌ 错误：DmzGame 下没有 DMZCampTask
CS.DmzGame.DMZCampTask

-- ✅ 正确：在 Network 命名空间
CS.Network.DMZCampTask
```

### 踩坑 5：嵌套泛型创建

```lua
-- ❌ 错误：字符串语法不支持嵌套泛型
CS.System.Collections.Generic["List`1[System.Collections.Generic.List`1[...]]"]()

-- ✅ 正确：使用 typeof + 函数调用
local listType = typeof(CS.System.Collections.Generic.List(CS.Network.DMZCampTask))
local sortedList = CS.System.Collections.Generic.List(listType)()
```

### 踩坑 6：PVE 相关类的命名空间

```lua
-- ❌ 错误：PVE 下没有这些类
CS.PVE.PVEMACHINE_TYPE.eShopping
CS.PVE.PVEShoppingMachine

-- ✅ 正确：在 PVE.MP 命名空间
CS.PVE.MP.PVEMACHINE_TYPE.eShopping
CS.PVE.MP.PVEShoppingMachine
```

### 踩坑 7：GameUIEventEnum 命名空间

```lua
-- ❌ 错误：不在 GameUI 命名空间
CS.GameUI.GameUIEventEnum.Notify_VestValueChanged

-- ✅ 正确：在 GameBase 命名空间
CS.GameBase.GameUIEventEnum.Notify_VestValueChanged
```

### 踩坑 8：自创方法名（严重错误！）

```lua
-- ❌ 严重错误：C# 源码中根本没有这个方法！
machine:RefreshShoppingCarMachine(playerId)  -- 这是 AI 自己编造的！

-- ✅ 正确：必须与 C# 源码中的方法名完全一致
machine:UpdateVestData()  -- C# 源码中就是这个方法
```

**⚠️ 绝对不能添加 C# 源码中不存在的方法调用！**

### 踩坑 9：xlua.private_accessible 滥用

```lua
-- ❌ 错误：热修复当前类时，不需要对当前类声明 private_accessible
xlua.private_accessible(CS.PVE.ZM.ZMGameEventChannel)  -- 多余！
xlua.hotfix(CS.PVE.ZM.ZMGameEventChannel, 'Vest', function(self, item, playerId)
    local myField = self.m_privateField  -- 当前类的私有成员可以直接访问
end)

-- ✅ 正确：只有访问外部类的私有成员才需要声明
xlua.private_accessible(CS.PVE.MP.MPPawn)  -- 因为下面要访问 MPPawn 的私有成员
xlua.hotfix(CS.PVE.ZM.ZMGameEventChannel, 'Vest', function(self, item, playerId)
    local pawn = CS.GameEngine.GamePlay.GetPawn(playerId)
    local externalField = pawn.m_internalValue  -- 访问外部类的私有成员
end)
```

**规则**：
- 当前类（被 hotfix 的类）→ 不需要 `xlua.private_accessible`
- 外部类（其他类）→ 需要 `xlua.private_accessible`

### 踩坑 10：使用 GeneralLog（禁止！）

```lua
-- ❌ 禁止：不要使用 GeneralLog
CS.GameEngine.Log.GeneralLog("[ZMGameEventChannel](Vest) playerID: %d pawn is null", playerId)

-- ✅ 正确：统一使用 PublishLog
CS.GameEngine.Log.PublishLog("[HotFix#21] Vest - pawn is nil, playerId=" .. tostring(playerId))
```

**规则**：所有热修复脚本中的日志必须使用 `PublishLog`，禁止使用 `GeneralLog`！

---

## 📋 转译检查清单

在生成 Lua 代码前，检查以下项目：

### 基础检查
- [ ] C# 原始代码是否能编译通过？
- [ ] 是否获取了完整的 C# 源码（`svn cat`）？
- [ ] 是否对比了 diff 确认实际修改点？

### 命名空间检查（核心！）
- [ ] 每个类/枚举的命名空间是否通过搜索 C# 源码或历史 Lua 代码确认？
- [ ] `GamePlay`、`DataStoreManager`、`EventManager` 是否用 `GameEngine` 命名空间？
- [ ] `GameUIEventEnum` 是否用 `GameBase` 命名空间（不是 `GameUI`）？
- [ ] `PVEMACHINE_TYPE`、`PVEShoppingMachine` 是否用 `PVE.MP` 命名空间（不是 `PVE`）？
- [ ] `EBREquipmentSlotType` 是否用 `GameBase` 命名空间？

### 代码一致性检查（核心！）
- [ ] 方法签名（参数数量、类型）是否与 C# 完全一致？
- [ ] 方法名是否与 C# 源码完全一致？（如 `UpdateVestData` 不能写成其他名字）
- [ ] 是否添加了 C# 源码中不存在的方法调用？（绝对禁止！）
- [ ] 代码逻辑顺序是否与 C# 一致？

### 语法检查
- [ ] 类型转换是否使用 `cast()` 而非 `xlua.cast()`？
- [ ] `DMZCampTask` 是否用 `CS.Network.DMZCampTask`？
- [ ] `xlua.private_accessible` 是否只用于访问**外部类**的私有成员？（当前类不需要！）
- [ ] 泛型类型创建是否使用函数调用语法？
- [ ] 工具类是否使用 `CS.GameUI.UICommonTools` 和 `CS.UnityTool`？

### 日志检查
- [ ] 是否在每个 if-else 分支添加了 `PublishLog` 调试日志？
- [ ] 日志格式是否正确：`[HotFix#<序号>] <方法名> - <描述>`？
- [ ] 是否使用了 `GeneralLog`？（禁止！必须改为 `PublishLog`）

---

## 📂 参考目录

历史 Lua 热修复代码位置：
- `Client\Export\LuaHotFixArchive\Automatic\CN29.0_WWL35.0\` - 上一版本参考
- `Client\Export\LuaHotFixArchive\Automatic\CN30.0_WWL36.0\` - 当前版本

**注意**：参考历史代码时，只参考写法风格，不照抄逻辑和参数！
