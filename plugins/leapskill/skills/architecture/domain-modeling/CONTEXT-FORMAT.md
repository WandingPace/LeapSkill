# CONTEXT.md 格式

## 结构

```md
# {上下文名称}

{一到两句话：这个上下文是什么，为什么存在。}

## Language

**Order**:
{一到两句术语定义}
_Avoid_: Purchase, transaction

**Invoice**:
交付后发送给客户的付款请求。
_Avoid_: Bill, payment request

**Customer**:
下单的个人或组织。
_Avoid_: Client, buyer, account
```

## 规则

- **要有明确取舍。** 同一概念有多个叫法时，选一个最好的，其余放进 `_Avoid_`。
- **定义要短。** 最多一到两句。定义它**是什么**，不是它做什么。
- **只收录这个项目上下文特有的术语。** 通用编程概念（timeout、错误类型、工具模式）即使项目大量使用，也不属于这里。加术语前先问：这是这个上下文独有的概念，还是通用编程概念？只有前者才收。
- **出现自然分组时，用子标题组织术语。** 如果所有术语都属于一个内聚领域，平铺列表也可以。

## 单上下文与多上下文仓库

**单上下文（多数仓库）：** 仓库根目录放一个 `CONTEXT.md`。

**多上下文：** 仓库根目录放一个 `CONTEXT-MAP.md`，列出各上下文的位置和关系：

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md): 接收并跟踪客户订单
- [Billing](./src/billing/CONTEXT.md): 生成账单并处理付款
- [Fulfillment](./src/fulfillment/CONTEXT.md): 管理仓库拣货和发货

## Relationships

- **Ordering → Fulfillment**：Ordering 发出 `OrderPlaced` 事件；Fulfillment 消费它并开始拣货
- **Fulfillment → Billing**：Fulfillment 发出 `ShipmentDispatched` 事件；Billing 消费它并生成账单
- **Ordering ↔ Billing**：共享 `CustomerId` 和 `Money` 类型
```

skill 会自动推断适用哪种结构：

- 如果存在 `CONTEXT-MAP.md`，读取它找到各上下文
- 如果只有根目录 `CONTEXT.md`，就是单上下文
- 如果两者都不存在，则在第一个术语被确定后，再按需创建根目录 `CONTEXT.md`

存在多上下文时，推断当前主题属于哪个上下文。如果判断不了，直接问。
