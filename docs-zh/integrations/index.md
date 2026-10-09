# 集成

LangChain4j 为大量 LLM 提供商、向量存储与其他组件提供了开箱即用的集成，每个集成都有独立的 Maven 依赖。

- [语言模型](language-models/index.md) — 聊天与文本生成
- [嵌入模型](embedding-models/1-in-process.md) — 文本向量化
- [向量存储](embedding-stores/index.md) — 向量数据库与检索
- [聊天记忆存储](chat-memory-stores/index.md) — 会话持久化
- [图像模型](image-models/dall-e.md) — 图像生成
- [文档加载器](document-loaders/amazon-s3.md) — 从各种来源加载文档
- [文档解析器](document-parsers/text.md) — 解析 PDF、Office 等格式
- [评分（重排）模型](scoring-reranking-models/in-process.md) — 相关性评分与重排
- [决策模型](decision-models/typesafe.md) — 基于决策的路由
- [代码执行引擎](code-execution-engines/local.md) — 执行模型生成的代码
- [框架](frameworks/spring-boot.md) — Spring Boot / Quarkus / Micronaut / Helidon / CDI
- [网页搜索引擎](web-search-engines/google-custom-search.md) — 联网搜索
- [浏览器执行引擎](browser-execution-engines/playwright.md) — 浏览器自动化
- [模型路由](model-router/model-router.md) — 多模型路由
- [提示词重复](prompt-repetition/prompt-repetition.md) — 提示词重复防护
