# Google Gen AI（实验性）

https://github.com/googleapis/java-genai

!!! warning
    当前该集成被标记为**实验性**。其 API 和实现可能在未来版本中发生变化。
    它使用了 Google 官方新推出的 Java 版 Google Gen AI SDK（`com.google.genai:google-genai`）。

## 目录

- [Maven 依赖](#maven-依赖)
- [身份验证](#身份验证)
- [可用模型](#可用模型)
- [GoogleGenAiChatModel](#googlegenaichatmodel)
    - [配置](#配置)
- [GoogleGenAiStreamingChatModel](#googlegenaistreamingchatmodel)
    - [执行器](#执行器)
- [GoogleGenAiEmbeddingModel](#googlegenaiembeddingmodel)
- [GoogleGenAiImageModel](#googlegenaiimagemodel)
- [请求与响应日志](#请求与响应日志)
- [批量 API](#批量-api)
- [工具](#工具)
- [JSON Schema / 结构化输出](#json-schema-结构化输出)
- [接地元数据](#接地元数据)
- [自定义标签](#自定义标签)
- [文件 API](#文件-api)
- [缓存内容支持](#缓存内容支持)
- [思考模型（Gemini 3.0+）](#思考模型gemini-30)
- [Token 使用情况](#token-使用情况)
- [多模态（音频、视频、PDF）](#多模态音频视频pdf)
- [音频转录](#音频转录)
- [图像生成输出](#图像生成输出)
- [Token 计数估算器](#token-计数估算器)
- [模型目录](#模型目录)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-google-genai</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 身份验证

你可以通过 API 密钥或 Google Cloud Vertex AI 凭据对 Gemini 模型进行身份验证。

### Gemini 开发者 API（API 密钥）

你可以免费在此处获取 API 密钥：https://ai.google.dev/gemini-api/docs/api-key。
你可以通过 `.apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))` 将其提供给构建器。

### Google Cloud Vertex AI

如果你正在使用 Vertex AI，可以结合你的项目 ID 和位置，使用 Google Credentials 进行身份验证。如果可用，该集成会自动使用应用默认凭据（Application Default Credentials，ADC），你也可以显式提供它们：

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    // .googleCredentials(...) // Optional: explicitly provide credentials
    .projectId("your-google-cloud-project-id")
    .location("us-central1")
    .modelName("gemini-2.5-flash")
    .build();
```

## 可用模型

在文档中查看[可用模型](https://ai.google.dev/gemini-api/docs/models/gemini)列表。

* `gemini-3.1-pro-preview`
* `gemini-3.1-flash-lite`
* `gemini-3-pro-preview`
* `gemini-3-flash-preview`
* `gemini-2.5-pro`
* `gemini-2.5-flash`
* `gemini-2.5-flash-lite`

（参阅[官方文档](https://ai.google.dev/gemini-api/docs/models)获取如 `-image`、`-tts` 和 `-live` 等专用预览模型的完整列表。）

## GoogleGenAiChatModel

可以使用常规的 `chat(...)` 方法：

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

String response = gemini.chat("Hello Gemini!");
```

也可以使用 `ChatResponse chat(ChatRequest req)` 方法：

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

ChatResponse chatResponse = gemini.chat(ChatRequest.builder()
    .messages(UserMessage.from(
        "How many R's are there in the word 'strawberry'?"))
    .build());

String response = chatResponse.aiMessage().text();
```

### 配置

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    // or .googleCredentials(...)
    .projectId(...)
    .location(...)
    .modelName("gemini-2.5-flash")
    .temperature(1.0)
    .topP(0.95)
    .topK(64)
    .seed(42)
    .maxOutputTokens(8192)
    .timeout(Duration.ofSeconds(60))
    .maxRetries(2)
    .stopSequences(List.of(...))
    .safetySettings(List.of(...))
    .responseFormat(ResponseFormat.JSON)
    .enableGoogleSearch(true)
    .enableGoogleMaps(true)
    .enableUrlContext(true)
    .allowedFunctionNames(List.of("getWeather"))
    .thinkingLevel("LOW")
    .listeners(...)
    .build();
```

### 进阶：自定义 `GenerateContentConfig`

构建器方法覆盖了最常见的选项。若要设置底层 Google Gen AI Java SDK 中某个尚未通过构建器方法暴露的选项，
可以注册一个 `generateContentConfigCustomizer`。它会在本集成完成填充（生成参数、工具、系统
指令等）之后、配置对象构建之前接收 `GenerateContentConfig.Builder`，因此可以设置额外选项或覆盖现有
选项，同时每次请求的工具和系统指令仍会被保留。

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .generateContentConfigCustomizer(config -> config.responseLogprobs(true).logprobs(5))
    .build();
```

在 `GoogleGenAiStreamingChatModel` 上，用法完全相同。

## 请求与响应日志

你可以在 `GoogleGenAiChatModel`、`GoogleGenAiStreamingChatModel`、`GoogleGenAiEmbeddingModel` 和 `GoogleGenAiImageModel` 上启用请求和响应日志，用于调试、故障排查和审计目的。

要在模型构建器中捕获这些日志，请配置 `.logRequests(true)`、`.logResponses(true)`（或使用 `.logRequestsAndResponses(true)` 同时启用两者）。

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .logRequests(true)
    .logResponses(true)
    // Or: .logRequestsAndResponses(true)
    .build();
```

### 日志配置设置

Google Gen AI 集成模块中的所有日志都通过标准的 **SLF4J** 门面路由。要实际查看输出，你必须确保：
1. 你的依赖中存在 SLF4J 绑定（实现）。
2. 日志框架已配置为以 `INFO` 级别输出包 `dev.langchain4j.model.google.genai` 下的日志。

以下是主流日志环境的常见配置方式：

#### 1. 使用 Logback 配置

在项目中添加 Logback classic 实现：

##### Maven
```xml
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.5.8</version> <!-- or your preferred version -->
</dependency>
```

##### Gradle
```groovy
implementation 'ch.qos.logback:logback-classic:1.5.8'
```

接下来，在你的 `src/main/resources/logback.xml` 文件中配置日志级别。例如：

```xml
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>

    <!-- Configure the package specifically for Google Gen AI logging -->
    <logger name="dev.langchain4j.model.google.genai" level="INFO" />

    <root level="WARN">
        <appender-ref ref="STDOUT" />
    </root>
</configuration>
```

#### 2. 在 Spring Boot 应用中配置

Spring Boot 会自动提供 SLF4J 提供者。只需在你的 `application.properties`（或等效的 `application.yml`）中配置日志级别：

```properties
# Enable logging for Google Gen AI models
logging.level.dev.langchain4j.model.google.genai=INFO
```

#### 3. 使用 SLF4J Simple 配置

如果你在编写脚本或简单的命令行应用，可以使用轻量级的 `slf4j-simple` 后端：

##### Maven
```xml
<dependency>
    <groupId>org.slf4j</groupId>
    <artifactId>slf4j-simple</artifactId>
    <version>2.0.13</version>
</dependency>
```

在启动应用时通过系统属性配置 SLF4J Simple：

```bash
java -Dorg.slf4j.simpleLogger.log.dev.langchain4j.model.google.genai=INFO -jar app.jar
```

或者，在 `src/main/resources/` 中创建一个包含以下内容的 `simplelogger.properties` 文件：

```properties
org.slf4j.simpleLogger.log.dev.langchain4j.model.google.genai=info
```

## GoogleGenAiStreamingChatModel

`GoogleGenAiStreamingChatModel` 支持逐 token 流式输出响应文本。
响应必须由 `StreamingChatResponseHandler` 处理。

```java
StreamingChatModel gemini = GoogleGenAiStreamingChatModel.builder()
        .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
        .modelName("gemini-2.5-flash")
        .build();

CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();

gemini.chat("Tell me a joke about Java", new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.print(partialResponse);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        futureResponse.complete(completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        futureResponse.completeExceptionally(error);
    }
});

futureResponse.join();
```

### 执行器

Google Gen AI SDK 将流式输出暴露为**阻塞式**的 `ResponseStream` 迭代器：每个数据块都由阻塞的 `next()` 调用交付。因此，`GoogleGenAiStreamingChatModel` 需要一个 `ExecutorService`，在调用方线程之外驱动该迭代。

如果你不传入执行器，则会使用来自 `DefaultExecutorProvider` 的共享默认执行器（懒加载初始化，可用时使用虚拟线程）。这可以开箱即用，但**不推荐用于生产环境**：默认执行器是无界的、作用于整个 JVM 的，且与你的应用生命周期不绑定——因此它不提供背压、没有优雅关闭，在你的指标中也不可见。

在几乎任何情况下，你都应该提供自己的执行器——例如你框架管理的任务执行器（Spring `TaskExecutor`、Quarkus `ManagedExecutor` 等）、你自己创建的虚拟线程执行器，或根据你的并发预算调优的有界线程池：

```java
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor(); // or your framework's executor

StreamingChatModel gemini = GoogleGenAiStreamingChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .executor(executor)
    .build();
```

## 工具

支持工具（又称函数调用）。你可以使用 LangChain4j 的 `AiServices` 来定义它们：

```java
class WeatherForecastService {
    @Tool("Get the weather forecast for a location")
    String getForecast(@P("Location to get the forecast for") String location) {
        return "The weather in " + location + " is sunny and 25°C.";
    }
}

interface WeatherAssistant {
    String chat(String userMessage);
}

WeatherForecastService weatherForecastService = new WeatherForecastService();

ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .temperature(0.0)
    .build();

WeatherAssistant weatherAssistant = AiServices.builder(WeatherAssistant.class)
    .chatModel(gemini)
    .tools(weatherForecastService)
    .build();

String response = weatherAssistant.chat("What is the weather forecast for Tokyo?");
```

## JSON Schema / 结构化输出

`langchain4j-google-genai` 集成会将 LangChain4j 的 JSON Schema（`ResponseFormat.jsonSchema()`）直接映射到官方 Google Gen AI SDK 的 `ResponseSchema`。这样就可以原生地提取强类型的 Java record！

```java
record WeatherForecast(
    @Description("minimum temperature") Integer minTemperature,
    @Description("maximum temperature") Integer maxTemperature,
    @Description("chances of rain") boolean rain
) { }

interface WeatherForecastAssistant {
    WeatherForecast extract(String forecast);
}

ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

WeatherForecastAssistant forecastAssistant = AiServices.builder(WeatherForecastAssistant.class)
    .chatModel(gemini)
    .build();

WeatherForecast forecast = forecastAssistant.extract("""
    Morning: The day dawns bright and clear in Osaka...
    Temperatures climb to a comfortable 22°C (72°F) and 
    will drop to 15°C (59°F).
    """);
```

!!! note
    Google Gen AI API 对高级 JSON Schema 特性（如 `anyOf` / 多态类型）有一些限制。简单 POJO、列表和嵌套对象均完全支持。

## 缓存内容支持

当处理非常大的上下文窗口（如庞大的系统提示词、大型文档或庞大的代码库），且这些内容在多个请求之间复用时，通过缓存内容可以显著降低成本和延迟。

一旦你使用官方 Google Gen AI SDK 或 API 创建了缓存内容，就可以轻松地将唯一的缓存标识符传递给 LangChain4j 的聊天模型构建器：

```java
// Pass your cached content URI here
String cachedContentUri = "projects/123456/locations/us-central1/cachedContents/my-cached-content-789";

ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-pro")
    .cachedContent(cachedContentUri)
    .build();

// The model will automatically use the cached context!
String response = gemini.chat("Summarize the cached document in 3 bullet points.");
```

该功能可在 `GoogleGenAiChatModel`、`GoogleGenAiStreamingChatModel` 和 `GoogleGenAiBatchChatModel` 上使用。

### 创建和管理缓存

除了带外创建缓存，你还可以使用 `GoogleGenAiCaches` 直接在 LangChain4j 中创建和管理缓存，它封装了 SDK 的缓存生命周期（创建 / 获取 / 列出 / 更新 TTL / 删除）。消息使用与聊天模型相同的 `GoogleGenAiContentMapper` 进行缓存，因此你仍然处于 LangChain4j 的 `ChatMessage` 域中。

```java
GoogleGenAiCaches caches = GoogleGenAiCaches.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .build();

// Cache a large, reusable context (a system instruction plus a long document)
CachedContent cache = caches.createCache(
    "gemini-2.5-flash",
    List.of(
        SystemMessage.from("You are a precise assistant answering questions about the attached document."),
        UserMessage.from(longDocumentText)),
    Duration.ofHours(1));

// Reuse it across many requests via cachedContent
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .cachedContent(cache.name().orElseThrow())
    .build();

String answer = gemini.chat("Summarize the cached document in 3 bullet points.");

// Manage the cache lifecycle
caches.updateCacheTtl(cache.name().orElseThrow(), Duration.ofHours(2));
caches.listCaches();
caches.deleteCache(cache.name().orElseThrow());
```

> 注意：显式上下文缓存需要付费层级；在免费层级不可用。

## 思考模型（Gemini 3.0+）

Gemini 3.0 模型（如 `gemini-3.0-pro` 和 `gemini-3.0-flash`）支持高级推理（思考）能力。
你可以在模型配置时指定 `thinkingLevel` 来启用该功能。支持的取值为 `"MINIMAL"`、`"LOW"`、`"MEDIUM"` 和 `"HIGH"`：

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-3.0-pro")
    .thinkingLevel("MEDIUM")
    .build();
```

!!! note
    此前，思考功能通过基于 token 的 `thinkingBudget` 进行配置。`thinkingBudget` 参数现在被视为遗留（旧版），但仍受支持。你不能同时指定 `thinkingLevel` 和 `thinkingBudget`。

!!! tip
    LangChain4j 的 `google-genai` 集成能无缝管理使用思考模型进行多轮工具执行所需的复杂状态。它会自动持久化并在各对话轮次之间注入所需的隐藏 `thought_signature` token，确保健壮且不间断的智能体工作流！

### 思考摘要

设置 `includeThoughts(true)`，要求模型在回答的同时返回
[思考摘要](https://ai.google.dev/gemini-api/docs/generate-content/thinking)，
并设置 `returnThinking(true)`，将其映射到 `AiMessage.thinking()`：

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-3.1-pro-preview")
    .thinkingLevel("MEDIUM")
    .includeThoughts(true)
    .returnThinking(true)
    .build();

ChatResponse response = gemini.chat(UserMessage.from("What is 6 times 7?"));

String thinking = response.aiMessage().thinking();
String answer = response.aiMessage().text();
```

流式输出时，思考摘要通过 `StreamingChatResponseHandler.onPartialThinking()` 交付，
而回答继续通过 `onPartialResponse()` 到达。

若要在后续请求中将思考摘要发送回模型，设置 `sendThinking(true)`。多轮工具执行所需的
`thought_signature` token 会被独立处理，并始终保留，无论该设置如何。

!!! note
    `returnThinking` 默认禁用。模型返回的思考摘要随后会被丢弃，且永远不会出现在 `AiMessage.text()` 中。

## Token 使用情况

响应携带 `GoogleGenAiTokenUsage`，它在标准的输入、输出和总数之外，额外增加了 Gemini 报告的思考、缓存内容
和工具结果的 token 数：

```java
GoogleGenAiTokenUsage tokenUsage = (GoogleGenAiTokenUsage) response.metadata().tokenUsage();

Integer thoughtsTokenCount = tokenUsage.thoughtsTokenCount();
Integer cachedContentTokenCount = tokenUsage.cachedContentTokenCount();
Integer toolUsePromptTokenCount = tokenUsage.toolUsePromptTokenCount();
```

当模型未报告某项时，该项为 `null`。`cachedContentTokenCount` 是
`inputTokenCount()` 的一部分，而 `toolUsePromptTokenCount` 和 `thoughtsTokenCount` 则在其之上额外计数：
Gemini 将总数定义为 `inputTokenCount + outputTokenCount + toolUsePromptTokenCount + thoughtsTokenCount`。

## GoogleGenAiEmbeddingModel

`GoogleGenAiEmbeddingModel` 允许你使用 `gemini-embedding-2` 等模型为文本片段生成嵌入。

```java
EmbeddingModel embeddingModel = GoogleGenAiEmbeddingModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-embedding-2")
    .outputDimensionality(768)
    .taskType(GoogleGenAiEmbeddingModel.TaskTypeEnum.RETRIEVAL_DOCUMENT)
    .build();

Response<Embedding> response = embeddingModel.embed("Hello world!");
```

### 批量处理与重试

对多个文本片段进行嵌入（通过 `embedAll`）时，`GoogleGenAiEmbeddingModel` 会自动管理批量处理和 API 请求重试。

```java
EmbeddingModel embeddingModel = GoogleGenAiEmbeddingModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-embedding-2")
    .maxSegmentsPerBatch(100) // Default: 100. Sets maximum segments per batch request.
    .maxRetries(3)             // Default: 3. Automatically retries failed requests.
    .build();
```

#### 基于标题的分组策略
官方 Google Gen AI Java SDK 的 `embedContent` API 每个批量请求只支持一个公共的 `title`。为了干净利落地处理这一限制并保留文档级别的关联关系，`GoogleGenAiEmbeddingModel` 实现了一种**按标题分组**的批量策略：

1. 当 `taskType` 设置为 `RETRIEVAL_DOCUMENT` 时，模型按文本片段的文档标题进行分组（使用 `.titleMetadataKey(...)` 定义的键从片段元数据中提取，默认为 `"title"`）。
2. 共享相同标题的片段会被合并为一批，在单次 API 调用中一起发送。
3. 标题不同（或没有标题）的片段在各自独立、经过优化的批次中处理。
4. 生成的嵌入会被无缝地重新组装，并按原始顺序返回。

这可以在不丢失文档元数据上下文或单个片段标题的情况下，最大化 API 吞吐量。


## GoogleGenAiImageModel

`GoogleGenAiImageModel` 允许你从文本提示词生成图像。它支持自定义配置，例如宽高比、图像尺寸和人物生成策略。

```java
ImageModel imageModel = GoogleGenAiImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-3.1-flash-image-preview")
    .aspectRatio("16:9")
    .build();

Response<Image> response = imageModel.generate("A futuristic city at sunset");
```

## 批量 API

Google Gen AI 集成提供了对 Batch API 的支持，允许你在后台异步运行操作。支持的批量模型如下：
- `GoogleGenAiBatchChatModel`
- `GoogleGenAiBatchEmbeddingModel`
- `GoogleGenAiBatchImageModel`

你可以以内联方式创建批量作业，也可以从上传到 Google Cloud 的文件创建。

```java
GoogleGenAiBatchChatModel batchChatModel = GoogleGenAiBatchChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

BatchResponse<ChatResponse> batchResponse = batchChatModel.submit(
    "My Batch Job",
    List.of(
        ChatRequest.builder().messages(UserMessage.from("What is 2+2?")).build(),
        ChatRequest.builder().messages(UserMessage.from("What is the capital of France?")).build()
    )
);

System.out.println("Batch Job ID: " + batchResponse.batchId());
```

然后，你可以使用 `batchChatModel.retrieve(batchResponse.batchId())` 检索该作业的状态和结果。

## 接地元数据

如果你启用了 Google Search 接地功能，或使用了 Vertex AI Search 数据存储，Google Gen AI 聊天模型会直接在 `ChatResponse` 中暴露原生的 `GroundingMetadata`。你可以通过响应元数据，经由底层的原始 `GenerateContentResponse` 获取它。

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .enableGoogleSearch(true)
    .build();

ChatResponse response = gemini.chat(ChatRequest.builder()
    .messages(UserMessage.from("Who won the super bowl in 2024?"))
    .build());

GoogleGenAiChatResponseMetadata metadata = 
    (GoogleGenAiChatResponseMetadata) response.metadata();

if (metadata.rawResponse() != null 
        && metadata.rawResponse().candidates() != null 
        && !metadata.rawResponse().candidates().isEmpty()) {
    var groundingMetadata = metadata.rawResponse().candidates().get(0).groundingMetadata();
    if (groundingMetadata != null && groundingMetadata.webSearchQueries() != null) {
        System.out.println("Search Queries: " + groundingMetadata.webSearchQueries());
    }
}
```

## 自定义标签

你可以为 Google Gen AI 请求应用自定义的键值标签，这对计费、指标和跟踪很有用。支持自定义标签的组件有：
- `GoogleGenAiChatModel`
- `GoogleGenAiStreamingChatModel`
- `GoogleGenAiBatchChatModel`
- `GoogleGenAiImageModel`
- `GoogleGenAiBatchImageModel`

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .labels(Map.of("environment", "production", "team", "backend"))
    .build();
```

## 文件 API

Google Gen AI 集成提供了 `GoogleGenAiFiles` 工具，用于在 Google 服务器上上传和管理文件。这对于传递可能超出标准请求限制的大型多模态输入（如较长的视频、音频文件或篇幅较大的 PDF）特别有用。

```java
GoogleGenAiFiles fileApi = GoogleGenAiFiles.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .build();

String uploadedFileUri = fileApi.uploadFile(
    Paths.get("path/to/my-video.mp4"), 
    "video/mp4", 
    "My Video Demo"
);

// You can now use this URI in your chat requests
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

ChatResponse response = gemini.chat(ChatRequest.builder()
    .messages(UserMessage.from(
        VideoContent.from(uploadedFileUri, "video/mp4"),
        TextContent.from("What happens in this video?")
    ))
    .build());
```

## 多模态（音频、视频、PDF）

该集成完全支持 LangChain4j 的多模态内容类型。底层的 `GoogleGenAiContentMapper` 会自动将它们转换为相应的 Gemini `Part` 对象。

```java
ChatModel gemini = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

ChatResponse response = gemini.chat(ChatRequest.builder()
    .messages(UserMessage.from(
        AudioContent.from("https://example.com/audio.mp3"),
        PdfFileContent.from("https://example.com/document.pdf"),
        TextContent.from("Summarize the document and the audio recording.")
    ))
    .build());
```

## 音频转录

为语音识别构建的模型（如 `gemini-3.5-transcribe`）可以将音频转换为文本。
将音频作为 `AudioContent` 发送即可，无需文本指令。转录结果作为 `AiMessage` 的文本返回。

使用 `audioTranscriptionConfig` 控制音频的转录方式：

```java
ChatModel transcriber = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-3.5-transcribe")
    .audioTranscriptionConfig(AudioTranscriptionConfig.builder()
        .mode(AudioTranscriptionConfigMode.Known.VERBATIM)
        .languageCodes("en-US")
        .customVocabulary("LangChain4j", "Gemini")
        .wordTimestamp(true)
        .diarization(true)
        .build())
    .build();

ChatResponse response = transcriber.chat(ChatRequest.builder()
    .messages(UserMessage.from(AudioContent.from("https://example.com/meeting.mp3")))
    .build());

String transcript = response.aiMessage().text();
```

- `mode`：`VERBATIM`（默认值）保留所有词语，包括填充词、重复和口误。
  `SMART` 会移除这些内容，并对文本进行轻度格式化。`SMART` 不能与单词时间戳和说话人分离一起使用。
- `languageCodes`：音频中所说语言的 BCP-47 代码。省略时，语言会被自动检测。
- `customVocabulary`：模型应当识别的词语和短语，例如产品名或人名。
- `wordTimestamp`：返回每个单词的起始和结束偏移。
- `diarization`：标注哪个说话人说了什么。

单词时间戳和说话人标签不是 `AiMessage` 文本的一部分。请从原始响应中读取它们：

```java
GoogleGenAiChatResponseMetadata metadata = (GoogleGenAiChatResponseMetadata) response.metadata();

for (Part part : metadata.rawResponse().parts()) {
    part.audioTranscription().ifPresent(transcription -> {
        String speaker = transcription.speakerLabel().orElse("");
        for (WordInfo word : transcription.words().orElse(List.of())) {
            System.out.printf("[%s] %s - %s %s%n",
                speaker, word.startOffset().orElse(""), word.endOffset().orElse(""), word.word().orElse(""));
        }
    });
}
```

`GoogleGenAiStreamingChatModel` 接受相同的 `audioTranscriptionConfig`，但其原始响应只保存最后流式传输的数据块，
因此当你需要单词时间戳或说话人标签时，请使用 `GoogleGenAiChatModel`。

## 图像生成输出

某些 Gemini 模型（如 `gemini-2.5-flash-image`）会在聊天响应文本的同时返回生成的图片。
它们以 `inlineData` 部分的形式到达，`GoogleGenAiChatModel` 会将它们映射到 `AiMessage` 的
`GENERATED_IMAGES_KEY` 属性下，而 `AiMessage.images()` 读取的正是它：

```java
ChatModel model = GoogleGenAiChatModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash-image")
    .build();

ChatResponse response = model.chat(UserMessage.from("A watercolor sketch of a lighthouse at dusk"));

for (Image image : response.aiMessage().images()) {
    System.out.println("Generated image: " + image.mimeType());

    // Save it, display it, or hand it to another model
    Files.write(Paths.get("generated_image.png"), Base64.getDecoder().decode(image.base64Data()));
}
```

只有 `image/*` 类型的二进制数据会成为生成的图像；其他任何类型的内联数据都会被忽略。

流式响应的工作方式相同。`GoogleGenAiStreamingChatModel` 一次接收一个数据块的回答，每个
数据块都会将其图像贡献给最终消息，因此即使在独立的数据块中到达的图片也不会丢失。

`langchain4j-google-ai-gemini` 将生成的图像存储在相同的键下，因此相同的读取代码在
两个模块中都可以使用。

## Token 计数估算器

你可以使用 `GoogleGenAiTokenCountEstimator` 精确估算提示词和消息中的 token 数量，它使用官方 SDK 的计数端点。

```java
TokenCountEstimator estimator = GoogleGenAiTokenCountEstimator.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

int tokenCount = estimator.estimateTokenCount("How many tokens is this sentence?");
System.out.println("Tokens: " + tokenCount);
```

## 模型目录

你可以使用 `GoogleGenAiModelCatalog` 以编程方式查询可用的 Gemini 模型列表。这对于动态发现模型能力、上下文窗口和支持的方法很有帮助。

```java
GoogleGenAiModelCatalog catalog = GoogleGenAiModelCatalog.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .build();

List<Model> availableModels = catalog.listModels();
availableModels.forEach(model -> {
    System.out.println("Model Name: " + model.name());
    System.out.println("Supported Generation Methods: " + model.supportedGenerationMethods());
});
```
