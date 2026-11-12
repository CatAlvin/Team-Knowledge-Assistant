# 演示步骤

## 浏览器演示

启动 python -m uvicorn api:app --host 127.0.0.1 --port 8001，打开 http://127.0.0.1:8001。

1. 在概览查看频道摘要、行动项、消息分布和关注事项。
2. 在消息记录搜索 webhook，并筛选 #customer-support，打开完整上下文。
3. 勾选一项任务，切换已完成列表，刷新后查看完成状态。
4. 在知识问答选择 Are webhooks signed?，查找内容并打开来源。
5. 回到概览生成简报，导出 JSON 查看摘要、任务和 review_state。

## 代码与接口

1. 运行 python demo.py，打开 outputs/digest.json。
2. 查看 55 条消息形成的两个频道摘要、任务列表和带 message_id 的提醒。
3. 展示任务的负责人、日期和优先级字段；说明畸形 JSON 会导致失败而非空数组。
4. 对比 Webhook 签名问题的来源列表与无关问题的 refused=true。
5. 启动 REST，调用 /digest，再调用 /tasks 和 /alerts 对照业务结果。
6. 运行 python scripts/verify.py，展示输入校验、接口一致性、鉴权和 MCP 子进程测试。

可追问点：为什么使用同步接口；如何处理多副本与长任务；为什么缓存按知识库路径区分；为什么离线规则输出不能当作真实模型质量。
