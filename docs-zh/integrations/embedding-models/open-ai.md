# OpenAI

!!! note
    这是 `OpenAI` 集成的文档，它使用 OpenAI REST API 的自定义 Java 实现，与 Quarkus 配合效果最好（因为它使用 Quarkus REST 客户端），与 Spring 配合也很好（因为它使用 Spring 的 RestClient）。

    LangChain4j 提供 3 种不同的 OpenAI 集成来使用嵌入模型，这是第 1 种：

    - [OpenAI](../language-models/open-ai.md) 使用 OpenAI REST API 的自定义 Java 实现，与 Quarkus 配合效果最好（因为它使用 Quarkus REST 客户端），与 Spring 配合也很好（因为它使用 Spring 的 RestClient）。
    - [OpenAI Official SDK](../language-models/open-ai-official.md) 使用官方的 OpenAI Java SDK。
    - [Azure OpenAI](../language-models/azure-open-ai.md) 使用 Microsoft 的 Azure SDK，如果你使用 Microsoft Java 技术栈（包括高级 Azure 认证机制），效果最佳。

- https://platform.openai.com/docs/guides/embeddings
- https://platform.openai.com/docs/api-reference/embeddings

## Maven 依赖

### 纯 Java
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

### Spring Boot
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

!!! note
    此 starter 需要 **Spring Boot 4**。在 **Spring Boot 3** 上，请改用 `langchain4j-open-ai-spring-boot-starter`。
    详情参见 [Spring Boot 集成](../../tutorials/spring-boot-integration.md#支持的版本)。

## 创建 `OpenAiEmbeddingModel`

### 纯 Java
```java
EmbeddingModel model = OpenAiEmbeddingModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("text-embedding-3-small")
        .build();
```

### Spring Boot
添加到 `application.properties`：
```properties
# Mandatory properties:
langchain4j.open-ai.embedding-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.embedding-model.model-name=text-embedding-3-small

# Optional properties:
langchain4j.open-ai.embedding-model.base-url=...
langchain4j.open-ai.embedding-model.custom-headers=...
langchain4j.open-ai.embedding-model.dimensions=...
langchain4j.open-ai.embedding-model.log-requests=...
langchain4j.open-ai.embedding-model.log-responses=...
langchain4j.open-ai.embedding-model.max-retries=...
langchain4j.open-ai.embedding-model.organization-id=...
langchain4j.open-ai.embedding-model.project-id=...
langchain4j.open-ai.embedding-model.timeout=...
langchain4j.open-ai.embedding-model.user=...
```

## 设置自定义嵌入请求参数

使用 `OpenAiEmbeddingModel` 时，你可以
在 HTTP 请求的 JSON body 中配置嵌入请求的自定义参数。这对于需要
提供商特定嵌入参数的 OpenAI 兼容提供商很有用：
```java
EmbeddingModel model = OpenAiEmbeddingModel.builder()
        .baseUrl("https://integrate.api.nvidia.com/v1")
        .apiKey(System.getenv("NVIDIA_API_KEY"))
        .modelName("nvidia/nv-embedqa-e5-v5")
        .customParameters(Map.of("input_type", "passage"))
        .build();
```

## 能力

- **每次调用的参数**（通过 `EmbeddingRequest`）：`dimensions` —— 用于
  `text-embedding-3` 模型，降低输出维度。OpenAI 特有的 `user`、`encoding_format` 以及任意透传参数
  通过 `OpenAiEmbeddingRequestParameters` 可用（例如用于 NVIDIA 的 `input_type`）。
- 仅文本（无图像输入）。
- **监听器**：通过 `OpenAiEmbeddingModel.builder().listeners(...)` 配置。

请求/响应 API 请参阅 [嵌入模型](../../tutorials/rag.md#嵌入模型embedding-model)。

## 示例

- [OpenAiEmbeddingModelExamples](https://github.com/langchain4j/langchain4j-examples/blob/main/open-ai-examples/src/main/java/OpenAiEmbeddingModelExamples.java)
