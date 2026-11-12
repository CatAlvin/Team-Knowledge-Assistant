# 实施任务

| 任务 | 输入 | 产出 | 依赖 | 验收 |
| --- | --- | --- | --- | --- |
| TK-T01 输入与输出模型 | TK-01、TK-03、data-models | models.py、load_messages | 无 | TK-AC01、TK-AC03 |
| TK-T02 摘要与任务 | TK-02、TK-03、ADR-002 | common/nlp.py | TK-T01 | TK-AC02、TK-AC03 |
| TK-T03 风险与检索 | TK-04、TK-05、ADR-003 | common/assistant.py | TK-T01 | TK-AC04、TK-AC05 |
| TK-T04 协议入口 | TK-06、api-spec | api.py、mcp_server.py、demo.py | TK-T02、TK-T03 | TK-AC06 |
| TK-T05 打包与验收 | TK-07、全部规格 | tests/、scripts/、Dockerfile | TK-T04 | TK-AC07 |
| TK-T06 前端工作台 | [workbench](workbench.md) | workbench_api.py、web/、test_workbench.py | TK-T04 | TK-UI-AC01 至 TK-UI-AC05 |

状态与验证证据见 [verification.md](verification.md)。真实模型质量、消息在线接入和持久化队列不属于已完成的离线功能验收。
