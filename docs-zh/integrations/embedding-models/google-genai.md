# Google Gen AI 嵌入（实验性）

https://github.com/googleapis/java-genai

此集成使用 Google Gen AI 的官方 Java SDK（`com.google.genai:google-genai`）。它被标记为
**实验性**：API 和实现可能会在未来的版本中变化。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-google-genai</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API 密钥

在此处免费获取 API 密钥：https://ai.google.dev/gemini-api/docs/api-key 。

## 可用模型

参阅[可用的嵌入模型](https://ai.google.dev/gemini-api/docs/embeddings#model-versions)，例如：

* `gemini-embedding-001` — 仅支持文本；支持任务类型和输出维度（128–3072）。
* `gemini-embedding-2` — 原生多模态；不使用任务类型参数（参见
  [Google AI Gemini Embeddings](google-ai-gemini.md) 了解任务指令在 Gemini Embedding 2 中如何工作）。

## GoogleGenAiEmbeddingModel

### 基本用法

```java
EmbeddingModel embeddingModel = GoogleGenAiEmbeddingModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-embedding-001")
    .build();

Response<Embedding> response = embeddingModel.embed("Hello, world!");
Embedding embedding = response.content();
```

### 配置嵌入模型

```java
EmbeddingModel embeddingModel = GoogleGenAiEmbeddingModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-embedding-001")
    .taskType(GoogleGenAiEmbeddingModel.TaskTypeEnum.RETRIEVAL_DOCUMENT) // default task type
    .outputDimensionality(768)      // reduce the embedding size (for models that support it)
    .titleMetadataKey("title")      // metadata key used as the document title for RETRIEVAL_DOCUMENT
    .maxRetries(3)
    .timeout(Duration.ofSeconds(30))
    .build();
```

## 请求/响应 API 与能力

除了便捷方法和构建器级别的 `taskType(...)` 之外，`GoogleGenAiEmbeddingModel` 还支持带有每次调用参数的请求/响应 API：

- **输入类型**：`EmbeddingInputType.QUERY` / `DOCUMENT` 映射到 SDK 的 `RETRIEVAL_QUERY` /
  `RETRIEVAL_DOCUMENT` 任务类型，因此你可以在不配置两个模型实例的情况下以不同方式嵌入查询和文档。（这适用于支持任务类型的模型，例如 `gemini-embedding-001`。）
- **维度**：每次调用的 `dimensions(...)` 会覆盖构建器的 `outputDimensionality`，适用于支持缩减输出大小的模型。
- **多模态**（`gemini-embedding-2`）：原生地将交错的文本 + 图像嵌入到单个嵌入中。
  较早的模型（例如 `gemini-embedding-001`）仅支持文本。图像必须以 base64 形式提供（`ImageContent`）。
- **监听器**：通过 `GoogleGenAiEmbeddingModel.builder().listeners(...)` 配置，以观察请求、
  响应和错误。

```java
EmbeddingResponse response = embeddingModel.embed(EmbeddingRequest.builder()
    .input("What is the capital of France?")
    .inputType(EmbeddingInputType.QUERY) // embed as a query
    .dimensions(256)                     // reduce output dimensionality
    .build());

List<Embedding> embeddings = response.embeddings();
```

多模态示例（Gemini Embedding 2 — 文本和图像融合为一个嵌入）：

```java
EmbeddingModel embeddingModel = GoogleGenAiEmbeddingModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-embedding-2")
    .build();

EmbeddingResponse response = embeddingModel.embed(EmbeddingRequest.builder()
    .input(TextContent.from("a photo of a cat"), ImageContent.from(base64Image, "image/png"))
    .build());

Embedding embedding = response.embeddings().get(0);
```

有关请求/响应 API，参见[嵌入模型](../../tutorials/rag.md#嵌入模型embedding-model)；
有关监听器，参见[可观测性](../../tutorials/observability.md)。

## 了解更多

有关 Gemini 嵌入模型的更多详细信息，请参见
[文档](https://ai.google.dev/gemini-api/docs/embeddings)。