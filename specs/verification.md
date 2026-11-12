# 验证记录

日期：2026-11-03。环境：Windows、Python 3.12.1、APP_MODE=offline。

## 结果

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 自动测试 | 15/15 通过 | python -m unittest discover -s tests -v |
| HTTP / MCP 契约 | 一致 | python scripts/contracts.py |
| 全流程演示 | 通过 | python demo.py；55 条消息、两个频道摘要、4 个任务和带引用问答 |
| 本地 REST | 通过 | python scripts/smoke_http.py；真实 Uvicorn、鉴权与 digest |
| 干净依赖环境 | 通过 | 新建 venv 安装依赖后重跑验证；pip check 无冲突 |
| 独立压缩包 | 通过 | 35 个文件逐项 SHA-256 校验；解压后在专用依赖环境重新执行 verify.py 与 smoke_http.py |

## 验收追踪

| 需求 / 验收 | 测试证据 |
| --- | --- |
| TK-01 / TK-AC01 | test_snapshot_and_pipeline_contract、test_invalid_input_and_duplicate_id |
| TK-02 / TK-AC02 | test_summary_empty_channel、test_digest_matches_individual_capabilities |
| TK-03 / TK-AC03 | test_task_year_comes_from_source、test_invalid_model_output_fails |
| TK-04 / TK-AC04 | test_risk_precedence_and_skip |
| TK-05 / TK-AC05 | test_citations_and_refusal、test_index_cache_key_is_directory |
| TK-06 / TK-AC06 | test_request_validation、test_token_auth、test_model_error_not_success_or_payload_leak |
| TK-07 / TK-AC07 | test_real_stdio_handshake_and_tool_calls、scripts/contracts.py |

TK-T01 至 TK-T05 的业务实现和接口验证完成。任务输出畸形、日期年份、索引缓存路径等问题均有回归用例。

## 过程与限制

Windows 沙箱的 asyncio 回环初始化曾阻塞；允许本机回环后，测试与实际 HTTP 服务均通过。新依赖环境中的 Starlette 1.10.0 提示测试客户端的 httpx 用法未来将弃用，当前验证通过。

本次未运行付费模型、Docker 构建或公网部署。关键词规则可能命中已经恢复的事件或含关键词的普通讨论；离线任务规则只覆盖明确编号格式。样例消息及其中的业务指标属于演示场景，不能作为真实业务效果。

## 2026-11-05 前端工作台验收

完整测试 20/20 通过，包含新增 5 项工作台接口检查。运行时 HTTP 与 MCP 契约已重新导出并检查一致。TK-UI-AC01 至 TK-UI-AC04 通过浏览器检查：搜索筛选、详情关闭、相关问答与来源、简报生成、项目切换、键盘焦点、主题与窄屏布局。

静态资源随独立项目导出。scripts/smoke_http.py 同时验证页面、资源、工作台鉴权和来源问答。
