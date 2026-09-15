# XLua 数值互操作

Lua number 传入 C# 参数、字段或属性时不会自动保留 `uint`、`int`、`float` 等具体类型。先读取接收端真实 C# 签名，再按需使用匹配的 `CS.XLua.Cast.UInt32`、`Int32`、`Float` 等 helper；否则接收端的强类型转换可能在运行时失败。

当前 CGame Hotfix 已有两类有效先例：返回 `uint` 的目标值经 `CS.XLua.Cast.UInt32` 后传给 UI 事件，整数状态经 `CS.XLua.Cast.Int32` 后广播。事件数字 ID 本身不能证明 payload 类型；找不到目标类型对应的 Cast helper 或同版本先例时保留未决，不猜测装箱类型。
