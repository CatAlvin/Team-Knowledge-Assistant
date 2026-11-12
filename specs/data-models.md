# 数据模型

所有公共响应模型定义在 models.py；OpenAPI components.schemas 是机器契约。

| 模型 | 字段与约束 |
| --- | --- |
| Message | id、sim_ts、channel、author、text 为字符串；ID 唯一；sim_ts 可解析为 ISO 日期时间 |
| Task | task 非空；owner 可空；due 为日期或 null；priority 为 high / medium / low |
| Alert | message_id、severity、channel、matched 关键词数组、text 原文前 100 字符 |
| Answer | question、answer、sources 数组、top_score、refused 布尔值、mode |
| Digest | message_count、alerts、summaries 映射、tasks、faq、mode |

AskRequest.question 去除空白后长度 3 至 2000，k 为 1 至 5。DigestRequest.faq_queries 最多 10 个，每个问题长度 3 至 2000。频道名允许省略 #，规范化后检索。

示例数据为离线功能演示输入，原文件随项目提供。输出 JSON 进入 outputs/，不提交密钥或本机绝对路径。

## Workspace 展示数据

/workspace 返回 kind、title、records、tasks、risks、groups、briefs、documents、period_start、period_end、projects。records 统一包含 id、title、text、author、time、channel、labels、state、url；documents 包含 name 与 title；projects 包含 id、title 与 url。来源正文由 /workspace/documents/{name} 返回 name、text。

前端完成记录以任务文本、负责人和日期为键。导出 JSON 中 review_state 包含 task 与 completed；该字段表示当前浏览器的跟进状态。
