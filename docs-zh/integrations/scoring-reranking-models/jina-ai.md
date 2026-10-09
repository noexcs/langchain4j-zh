# Jina

- [Jina Reranker 文档](https://jina.ai/reranker)
- [Jina Reranker API](https://api.jina.ai/redoc#tag/rerank)

### 简介

重排模型（reranker）是一种先进的 AI 模型，它接收来自搜索的初始结果集（通常由嵌入/基于 token 的搜索提供），并对其进行重新评估，以确保结果更贴合用户的意图。
它不局限于词汇层面的表面匹配，而是深入考量搜索查询与文档内容之间的深层交互。

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-jina</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

### 用法

```java


ScoringModel scoringModel = JinaScoringModel.builder()
    .apiKey(System.getenv("JINA_API_KEY"))
    .modelName("jina-reranker-v2-base-multilingual")
    .build();

ContentAggregator contentAggregator = ReRankingContentAggregator.builder()
    .scoringModel(scoringModel)
    ... 
    .build();

RetrievalAugmentor retrievalAugmentor = DefaultRetrievalAugmentor.builder()
    ...
    .contentAggregator(contentAggregator)
    .build();

return AiServices.builder(Assistant.class)
    .chatModel(...)
    .retrievalAugmentor(retrievalAugmentor)
    .build();
```
