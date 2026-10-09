# OpenAI 图像模型

!!! note
    这是 `OpenAI` 集成的文档，它使用一个自定义的 OpenAI REST API Java 实现，与 Quarkus（因为它使用 Quarkus REST 客户端）和 Spring（因为它使用 Spring 的 RestClient）配合效果最佳。
    
    
    LangChain4j 提供了 3 种不同的用于生成图像的 OpenAI 集成，这是其中的第 1 种：
    
    - [OpenAI](../language-models/open-ai.md) 使用一个自定义的 OpenAI REST API Java 实现，与 Quarkus（因为它使用 Quarkus REST 客户端）和 Spring（因为它使用 Spring 的 RestClient）配合效果最佳。
    
    - [OpenAI 官方 SDK](../language-models/open-ai-official.md) 使用官方的 OpenAI Java SDK。
    - [Azure OpenAI](../language-models/azure-open-ai.md) 使用来自 Microsoft 的 Azure SDK，如果你正在使用 Microsoft Java 技术栈（包括高级 Azure 认证机制），则配合效果最佳。

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
    此 starter 要求 **Spring Boot 4**。如果使用 **Spring Boot 3**，请改用 `langchain4j-open-ai-spring-boot-starter`。
    详情参见 [Spring Boot 集成](../../tutorials/spring-boot-integration.md#支持的版本)。



!!! note
    OpenAI 已弃用 DALL·E 2 和 DALL·E 3 模型，转而采用新的 GPT 图像模型
    （`gpt-image-1`、`gpt-image-1-mini`、`gpt-image-1.5`、`gpt-image-2`、`chatgpt-image-latest`）。
    DALL·E 专属参数 `style` 和 `response-format` 不再受 API 支持，
    已被移除。取而代之的是新参数 `background`、`output-format`、`output-compression` 和 `moderation`。

## 创建 `OpenAiImageModel`

### 纯 Java
```java
ImageModel model = OpenAiImageModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-image-1")
        .build();
```

### Spring Boot
添加到 `application.properties`：
```properties
# Mandatory properties:
langchain4j.open-ai.image-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.image-model.model-name=gpt-image-1

# Optional properties:
langchain4j.open-ai.image-model.background=...
langchain4j.open-ai.image-model.base-url=...
langchain4j.open-ai.image-model.custom-headers=...
langchain4j.open-ai.image-model.log-requests=...
langchain4j.open-ai.image-model.log-responses=...
langchain4j.open-ai.image-model.max-retries=...
langchain4j.open-ai.image-model.moderation=...
langchain4j.open-ai.image-model.organization-id=...
langchain4j.open-ai.image-model.output-compression=...
langchain4j.open-ai.image-model.output-format=...
langchain4j.open-ai.image-model.project-id=...
langchain4j.open-ai.image-model.quality=...
langchain4j.open-ai.image-model.size=...
langchain4j.open-ai.image-model.timeout=...
langchain4j.open-ai.image-model.user=...
```

## Token 用量

GPT 图像模型会报告一个请求使用了多少 token。`OpenAiImageModel` 将其作为
`OpenAiImageTokenUsage` 返回，它还将输入和输出 token 拆分为图像 token 和文本
token（OpenAI 对两者的定价不同）：

```java
Response<Image> response = model.generate("A watercolor painting of a lighthouse");

OpenAiImageTokenUsage tokenUsage = (OpenAiImageTokenUsage) response.tokenUsage();
tokenUsage.inputTokenCount();                    // all input tokens
tokenUsage.inputTokensDetails().textTokens();    // input tokens from the prompt
tokenUsage.inputTokensDetails().imageTokens();   // input tokens from input images (edits)
tokenUsage.outputTokenCount();                   // all output tokens
```

当 OpenAI 不报告这些详情时，它们为 `null`。DALL·E 模型根本不报告用量，
因此对它们而言 `response.tokenUsage()` 为 `null`。

## 示例

- [OpenAiImageModelExamples](https://github.com/langchain4j/langchain4j-examples/blob/main/open-ai-examples/src/main/java/OpenAiImageModelExamples.java)
