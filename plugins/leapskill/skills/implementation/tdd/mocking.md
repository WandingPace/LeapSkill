# 什么时候用 Mock

只在**系统边界**上 mock：

- 外部 API（支付、邮件等）
- 数据库（有时；优先用测试数据库）
- 时间/随机数
- 文件系统（有时）

不要 mock：

- 你自己的类/模块
- 内部协作对象
- 任何你能控制的东西

## 为可 Mock 性设计

在系统边界上，把接口设计得容易 mock：

**1. 使用依赖注入**

外部依赖从外部传入，不要在函数内部创建：

```typescript
// 容易 mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// 难以 mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. 优先用 SDK 风格接口，而不是通用 fetcher**

为每个外部操作提供具体函数，而不是一个带条件分支的通用函数：

```typescript
// GOOD：每个函数都可以独立 mock
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD：mock 里还要写条件逻辑
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

SDK 风格意味着：

- 每个 mock 只返回一种明确的数据结构
- 测试准备代码里没有条件逻辑
- 更容易看出测试覆盖了哪些 endpoint
- 每个 endpoint 都有自己的类型安全
