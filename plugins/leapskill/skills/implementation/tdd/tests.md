# 好测试与坏测试

## 好测试

**Integration 风格**：通过真实接口测试，不要 mock 内部组件。

```typescript
// GOOD：测试可观察行为
test("user can checkout with valid cart", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

特征：

- 测试用户或调用方关心的行为
- 只使用 public API
- 内部重构后仍然有效
- 描述“做了什么”，不描述“怎么做”
- 每个测试只有一个逻辑断言

## 坏测试

**实现细节测试**：与内部结构耦合。

```typescript
// BAD：测试实现细节
test("checkout calls paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

危险信号：

- mock 内部协作对象
- 测试 private 方法
- 断言调用次数或调用顺序
- 行为没变、只是重构，测试却挂了
- 测试名描述“怎么做”，而不是“做了什么”
- 绕过接口，用外部手段验证结果

```typescript
// BAD：绕过接口验证
test("createUser saves to database", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// GOOD：通过接口验证
test("createUser makes user retrievable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```

**同义反复测试**：期望值只是把实现重算一遍，测试天然会通过。

```typescript
// BAD：期望值用与实现相同的方式重新算出来
test("calculateTotal sums line items", () => {
  const items = [{ price: 10 }, { price: 5 }];
  const expected = items.reduce((sum, i) => sum + i.price, 0);
  expect(calculateTotal(items)).toBe(expected);
});

// GOOD：期望值是独立的已知字面量
test("calculateTotal sums line items", () => {
  expect(calculateTotal([{ price: 10 }, { price: 5 }])).toBe(15);
});
```
