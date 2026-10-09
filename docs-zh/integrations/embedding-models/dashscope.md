# DashScope

[DashScope](https://dashscope.aliyun.com/) 是由 [Alibaba Cloud](https://www.alibabacloud.com/) 开发的平台。
它提供了模型可视化、监控和调试的界面，特别是在生产环境中处理 AI/ML 模型时。该平台允许用户可视化性能指标、跟踪模型行为，并在部署周期早期识别潜在问题。

[Qwen](https://tongyi.aliyun.com/) 模型系列是由 [Alibaba Cloud](https://www.alibabacloud.com/) 开发的一系列生成式 AI 模型。Qwen 模型家族专为文本生成、摘要、问答和各种 NLP 任务而设计。

有关更多详细信息，请参见[DashScope 文档](https://help.aliyun.com/zh/model-studio/getting-started/?spm=a2c4g.11186623.help-menu-2400256.d_0.6655453aLIyxGp)。LangChain4j 通过使用 [DashScope Java SDK](https://help.aliyun.com/zh/dashscope/java-sdk-best-practices?spm=a2c4g.11186623.0.0.272a1507Ne69ja) 与 DashScope 集成。

## Maven 依赖

!!! note
    自 `1.0.0-alpha1` 起，`langchain4j-dashscope` 已迁移至 `langchain4j-community`，并更名为
    `langchain4j-community-dashscope`。

`1.0.0-alpha1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-dashscope</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及以后：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-dashscope</artifactId>
    <version>${latest version here}</version>
</dependency>
```

或者，你可以使用 BOM 来统一依赖管理：

```xml

<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-community-bom</artifactId>
        <version>${latest version here}</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencyManagement>
```

## 可配置参数

初始化 `QwenEmbeddingModel` 时，可以配置以下参数：

| 属性      | 描述                                                                  | 默认值                                                                           |
|-----------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| baseUrl   | 要连接的 URL。你可以使用 HTTP 或 websocket 连接 DashScope | https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding |
| apiKey    | API 密钥                                                                  |                                                                                         |
| modelName | 要使用的模型。                                                            | text-embedding-v2                                                                       |

## 示例

- [QwenEmbeddingModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-dashscope/src/test/java/dev/langchain4j/community/model/dashscope/QwenEmbeddingModelIT.java)