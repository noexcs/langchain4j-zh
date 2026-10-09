# OpenAI

!!! note
   这是 `OpenAI` 集成的文档。该集成使用自定义的 Java 实现的 OpenAI REST API，
   与 Quarkus（因为它使用 Quarkus REST 客户端）和 Spring（因为它使用 Spring 的 RestClient）最为契合。

   如果你使用的是 Quarkus，请参阅
   [Quarkus LangChain4j 文档](https://docs.quarkiverse.io/quarkus-langchain4j/dev/openai.html)。

   LangChain4j 提供了 3 种不同的 OpenAI 集成来使用聊天模型，本文档是其中第 1 种：

   - [OpenAI](open-ai.md) 使用自定义的 Java 实现的 OpenAI REST API，与 Quarkus（因为它使用 Quarkus REST 客户端）和 Spring（因为它使用 Spring 的 RestClient）最为契合。
   - [OpenAI Official SDK](open-ai-official.md) 使用官方 OpenAI Java SDK。
   - [Azure OpenAI](azure-open-ai.md) 使用 Microsoft 的 Azure SDK，如果你使用的是 Microsoft Java 技术栈（包括高级 Azure 认证机制），它最为契合。

## OpenAI 文档

- [OpenAI API 文档](https://platform.openai.com/docs/introduction)
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference)

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
   此 starter 需要 **Spring Boot 4**。如果你使用的是 **Spring Boot 3**，请改用 `langchain4j-open-ai-spring-boot-starter`。
   详见 [Spring Boot 集成](../../tutorials/spring-boot-integration.md#支持的版本)。

## API 密钥

要使用 OpenAI 模型，你需要一个 API 密钥。
你可以在[这里](https://platform.openai.com/api-keys)创建一个。

## 创建 `OpenAiChatModel`

### 纯 Java
```java
ChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();


// You can also specify default chat request parameters using ChatRequestParameters or OpenAiChatRequestParameters
ChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .defaultRequestParameters(OpenAiChatRequestParameters.builder()
                .modelName("gpt-4o-mini")
                .build())
        .build();
```
这将使用指定的默认参数创建一个 `OpenAiChatModel` 实例。

### Spring Boot
添加到 `application.properties`：
```properties
# Mandatory properties:
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.chat-model.model-name=gpt-4o-mini

# Optional properties:
langchain4j.open-ai.chat-model.base-url=...
langchain4j.open-ai.chat-model.custom-headers=...
langchain4j.open-ai.chat-model.frequency-penalty=...
langchain4j.open-ai.chat-model.log-requests=...
langchain4j.open-ai.chat-model.log-responses=...
langchain4j.open-ai.chat-model.logit-bias=...
langchain4j.open-ai.chat-model.max-retries=...
langchain4j.open-ai.chat-model.max-completion-tokens=...
langchain4j.open-ai.chat-model.max-tokens=...
langchain4j.open-ai.chat-model.metadata=...
langchain4j.open-ai.chat-model.organization-id=...
langchain4j.open-ai.chat-model.parallel-tool-calls=...
langchain4j.open-ai.chat-model.presence-penalty=...
langchain4j.open-ai.chat-model.project-id=...
langchain4j.open-ai.chat-model.reasoning-effort=...
langchain4j.open-ai.chat-model.response-format=...
langchain4j.open-ai.chat-model.return-thinking=...
langchain4j.open-ai.chat-model.seed=...
langchain4j.open-ai.chat-model.service-tier=...
langchain4j.open-ai.chat-model.stop=...
langchain4j.open-ai.chat-model.store=...
langchain4j.open-ai.chat-model.strict-schema=...
langchain4j.open-ai.chat-model.strict-tools=...
langchain4j.open-ai.chat-model.supported-capabilities=...
langchain4j.open-ai.chat-model.temperature=...
langchain4j.open-ai.chat-model.timeout=...
langchain4j.open-ai.chat-model.top-p=
langchain4j.open-ai.chat-model.user=...

# Optional Property: Custom Parameters (user-defined key=value) 
langchain4j.open-ai.chat-model.custom-parameters.<key>=<value>
```
上面大多数参数的说明见[这里](https://platform.openai.com/docs/api-reference/chat/create)。

此配置将创建一个 `OpenAiChatModel` bean，
它既可以被 [AI 服务](../../tutorials/spring-boot-integration.md#spring-boot-starters) 使用，
也可以在需要的地方自动装配，例如：

```java
@RestController
class ChatModelController {

    ChatModel chatModel;

    ChatModelController(ChatModel chatModel) {
        this.chatModel = chatModel;
    }

    @GetMapping("/model")
    public String model(@RequestParam(value = "message", defaultValue = "Hello") String message) {
        return chatModel.chat(message);
    }
}
```

## 结构化输出
[Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) 功能
同时支持[工具](../../tutorials/tools.md)和[response format](../../tutorials/ai-services.md#json-模式)。

关于结构化输出的更多信息见[这里](../../tutorials/structured-outputs.md)。

### 工具的结构化输出
要为工具启用结构化输出功能，在构建模型时设置 `.strictTools(true)`：
```java
OpenAiChatModel.builder()
    ...
    .strictTools(true)
    .build(),
```
请注意，这将自动使所有工具参数变为必填（json schema 中的 `required`），
并为 json schema 中的每个 `object` 设置 `additionalProperties=false`。这是由于当前 OpenAI 的限制所致。

### Response Format 的结构化输出
在使用 AI 服务时，要为响应格式化启用结构化输出功能，
在构建模型时设置 `.supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)` 和 `.strictJsonSchema(true)`：
```java
OpenAiChatModel.builder()
    ...
    .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)
    .strictJsonSchema(true)
    .build();
```
在这种情况下，AI 服务将自动从给定的 POJO 生成 JSON schema 并传递给 LLM。

### 思考 / 推理
此设置面向 [DeepSeek](https://api-docs.deepseek.com/guides/reasoning_model)。

在构建 `OpenAiChatModel` 或 `OpenAiStreamingChatModel` 时启用 `returnThinking` 参数后，
DeepSeek API 响应中的 `reasoning_content` 字段将被解析
并返回在 `AiMessage.thinking()` 中。

对 `OpenAiStreamingChatModel` 启用 `returnThinking` 参数后，
当 DeepSeek API 流式传输 `reasoning_content` 时，
将调用 `StreamingChatResponseHandler.onPartialThinking()` 和 `TokenStream.onPartialThinking()`
回调。

以下是配置思考的示例：
```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://api.deepseek.com/v1")
        .apiKey(System.getenv("DEEPSEEK_API_KEY"))
        .modelName("deepseek-reasoner")
        .returnThinking(true)
        .build();
```

在构建 `OpenAiChatModel` 或 `OpenAiStreamingChatModel` 时启用 `sendThinking` 参数后，
`AiMessage.thinking()` 将随请求发送给 DeepSeek API。
可以通过 `sendThinking(boolean, String)` 构建器方法配置该字段的名称。
默认使用 `reasoning_content` 字段名。

## 创建 `OpenAiStreamingChatModel`

### 纯 Java
```java
StreamingChatModel model = OpenAiStreamingChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();

// You can also specify default chat request parameters using ChatRequestParameters or OpenAiChatRequestParameters
StreamingChatModel model = OpenAiStreamingChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .defaultRequestParameters(OpenAiChatRequestParameters.builder()
                .modelName("gpt-4o-mini")
                .build())
        .build();
```

### Spring Boot
添加到 `application.properties`：
```properties
# Mandatory properties:
langchain4j.open-ai.streaming-chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.streaming-chat-model.model-name=gpt-4o-mini

# Optional properties:
langchain4j.open-ai.streaming-chat-model.base-url=...
langchain4j.open-ai.streaming-chat-model.custom-headers=...
langchain4j.open-ai.streaming-chat-model.frequency-penalty=...
langchain4j.open-ai.streaming-chat-model.log-requests=...
langchain4j.open-ai.streaming-chat-model.log-responses=...
langchain4j.open-ai.streaming-chat-model.logit-bias=...
langchain4j.open-ai.streaming-chat-model.max-retries=...
langchain4j.open-ai.streaming-chat-model.max-completion-tokens=...
langchain4j.open-ai.streaming-chat-model.max-tokens=...
langchain4j.open-ai.streaming-chat-model.metadata=...
langchain4j.open-ai.streaming-chat-model.organization-id=...
langchain4j.open-ai.streaming-chat-model.parallel-tool-calls=...
langchain4j.open-ai.streaming-chat-model.presence-penalty=...
langchain4j.open-ai.streaming-chat-model.project-id=...
langchain4j.open-ai.streaming-chat-model.reasoning-effort=...
langchain4j.open-ai.streaming-chat-model.response-format=...
langchain4j.open-ai.streaming-chat-model.return-thinking=...
langchain4j.open-ai.streaming-chat-model.seed=...
langchain4j.open-ai.streaming-chat-model.service-tier=...
langchain4j.open-ai.streaming-chat-model.stop=...
langchain4j.open-ai.streaming-chat-model.store=...
langchain4j.open-ai.streaming-chat-model.strict-schema=...
langchain4j.open-ai.streaming-chat-model.strict-tools=...
langchain4j.open-ai.streaming-chat-model.temperature=...
langchain4j.open-ai.streaming-chat-model.timeout=...
langchain4j.open-ai.streaming-chat-model.top-p=...
langchain4j.open-ai.streaming-chat-model.user=...

# Optional Property: Custom Parameters (user-defined key=value) 
langchain4j.open-ai.streaming-chat-model.custom-parameters.<key>=<value>
```


## 创建 `OpenAiModerationModel`

### 纯 Java
```java
ModerationModel model = OpenAiModerationModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("text-moderation-stable")
        .build();
```

### Spring Boot
添加到 `application.properties`：
```properties
# Mandatory properties:
langchain4j.open-ai.moderation-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.moderation-model.model-name=text-moderation-stable

# Optional properties:
langchain4j.open-ai.moderation-model.base-url=...
langchain4j.open-ai.moderation-model.custom-headers=...
langchain4j.open-ai.moderation-model.log-requests=...
langchain4j.open-ai.moderation-model.log-responses=...
langchain4j.open-ai.moderation-model.max-retries=...
langchain4j.open-ai.moderation-model.organization-id=...
langchain4j.open-ai.moderation-model.project-id=...
langchain4j.open-ai.moderation-model.timeout=...
```


## 创建 `OpenAiTextToSpeechModel`

`OpenAiTextToSpeechModel` 使用
[OpenAI Speech API](https://platform.openai.com/docs/api-reference/audio/createSpeech) 执行语音合成（TTS）。
它将生成的音频作为原始字节，包装在 `Audio` 对象中返回。

支持的模型为 `tts-1`、`tts-1-hd`、`gpt-4o-mini-tts` 和 `gpt-4o-mini-tts-2025-12-15`
（参见 `OpenAiTextToSpeechModelName`）。默认音色为 `alloy`。

### 纯 Java
```java
import dev.langchain4j.model.audio.TextToSpeechModel;
import dev.langchain4j.model.audio.TextToSpeechRequest;
import dev.langchain4j.model.audio.TextToSpeechResponse;
import dev.langchain4j.model.openai.OpenAiTextToSpeechModel;
import dev.langchain4j.model.openai.OpenAiTextToSpeechModelName;

TextToSpeechModel model = OpenAiTextToSpeechModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(OpenAiTextToSpeechModelName.TTS_1)
        .voice("alloy") // optional, defaults to "alloy"
        .build();

// Convenience method (uses the model's default voice):
TextToSpeechResponse response = model.synthesize("Hello world!");

// Or with an explicit request (the voice here overrides the model default):
TextToSpeechRequest request = TextToSpeechRequest.builder()
        .text("Hello world!")
        .voice("nova")
        .build();
TextToSpeechResponse response2 = model.synthesize(request);

byte[] audioBytes = response.audio().binaryData(); // e.g. write to an .mp3 file
String mimeType = response.audio().mimeType();      // e.g. "audio/mpeg"
```

输入文本不得超过 4096 个字符（OpenAI Speech API 的限制）；
更长的输入会导致 `IllegalArgumentException`。

## 创建 `OpenAiTextToSpeechModel`

`OpenAiTextToSpeechModel` 使用
[OpenAI Speech API](https://platform.openai.com/docs/api-reference/audio/createSpeech) 执行语音合成（TTS）。
它将生成的音频作为原始字节，包装在 `Audio` 对象中返回。

支持的模型为 `tts-1`、`tts-1-hd`、`gpt-4o-mini-tts` 和 `gpt-4o-mini-tts-2025-12-15`
（参见 `OpenAiTextToSpeechModelName`）。默认音色为 `alloy`。

### 纯 Java
```java
import dev.langchain4j.model.audio.TextToSpeechModel;
import dev.langchain4j.model.audio.TextToSpeechRequest;
import dev.langchain4j.model.audio.TextToSpeechResponse;
import dev.langchain4j.model.openai.OpenAiTextToSpeechModel;
import dev.langchain4j.model.openai.OpenAiTextToSpeechModelName;

TextToSpeechModel model = OpenAiTextToSpeechModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(OpenAiTextToSpeechModelName.TTS_1)
        .voice("alloy") // optional, defaults to "alloy"
        .build();

// Convenience method (uses the model's default voice):
TextToSpeechResponse response = model.synthesize("Hello world!");

// Or with an explicit request (the voice here overrides the model default):
TextToSpeechRequest request = TextToSpeechRequest.builder()
        .text("Hello world!")
        .voice("nova")
        .build();
TextToSpeechResponse response2 = model.synthesize(request);

byte[] audioBytes = response.audio().binaryData(); // e.g. write to an .mp3 file
String mimeType = response.audio().mimeType();      // e.g. "audio/mpeg"
```

输入文本不得超过 4096 个字符（OpenAI Speech API 的限制）；
更长的输入会导致 `IllegalArgumentException`。

## 创建 `OpenAiTokenCountEstimator`

```java
TokenCountEstimator tokenCountEstimator = new OpenAiTokenCountEstimator("gpt-4o-mini");
```

## 设置自定义聊天请求参数

使用 `OpenAiChatModel` 和 `OpenAiStreamingChatModel` 时，
你可以在 HTTP 请求的 JSON 请求体中为聊天请求配置自定义参数。
以下是启用网页搜索的示例：
```java
record ApproximateLocation(String city) {}
record UserLocation(String type, ApproximateLocation approximate) {}
record WebSearchOptions(UserLocation user_location) {}
WebSearchOptions webSearchOptions = new WebSearchOptions(new UserLocation("approximate", new ApproximateLocation("London")));
Map<String, Object> customParameters = Map.of("web_search_options", webSearchOptions);

ChatRequest chatRequest = ChatRequest.builder()
    .messages(UserMessage.from("Where can I buy good coffee?"))
    .parameters(OpenAiChatRequestParameters.builder()
        .modelName("gpt-4o-mini-search-preview")
        .customParameters(customParameters)
        .build())
    .build();

ChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .logRequests(true)
        .build();

ChatResponse chatResponse = model.chat(chatRequest);
```

这将产生一个具有如下请求体的 HTTP 请求：
```json
{
  "model" : "gpt-4o-mini-search-preview",
  "messages" : [ {
    "role" : "user",
    "content" : "Where can I buy good coffee?"
  } ],
  "web_search_options" : {
    "user_location" : {
      "type" : "approximate",
      "approximate" : {
        "city" : "London"
      }
    }
  }
}
```

或者，自定义参数也可以指定为嵌套 map 的结构：
```java
Map<String, Object> customParameters = Map.of(
    "web_search_options", Map.of(
        "user_location", Map.of(
            "type", "approximate",
            "approximate", Map.of("city", "London")
        )
    )
);
```

## 提示词缓存

OpenAI 会缓存较长的、重复的提示词前缀，缓存读取的计费价格仅为输入价格的一小部分。
以下控制项同时适用于 `OpenAiChatModel`/`OpenAiStreamingChatModel`（Chat Completions API）
和 `OpenAiResponsesChatModel`/`OpenAiResponsesStreamingChatModel`（Responses API）。

关于提示词缓存的更多信息见[这里](https://developers.openai.com/api/docs/guides/prompt-caching)。

### `promptCacheKey`

`promptCacheKey` 是一个可选字符串，用于引导路由，使相关请求更有可能
到达持有缓存条目的机器。它不会将请求固定到某台机器，也不保证缓存命中。

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5.6")
        .promptCacheKey("satisfaction_judge_v1")
        .build();
```

### `promptCacheOptions`

`gpt-5.6` 及之后的模型会在*断点*处精确匹配缓存前缀，而不会回退到较短的
未标记前缀。`promptCacheOptions` 控制断点的来源：

- `implicit` - OpenAI 在最新符合条件消息的末尾放置断点。
- `explicit` - 只使用你设置的断点。如果没有设置任何断点，则什么都不会被缓存。

```java
OpenAiChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5.6")
        .promptCacheOptions(OpenAiPromptCacheOptions.builder()
                .mode(OpenAiPromptCacheOptions.MODE_EXPLICIT)
                .ttl(OpenAiPromptCacheOptions.TTL_30M)
                .build())
        .build();
```

`OpenAiPromptCacheOptions.implicit()` 和 `OpenAiPromptCacheOptions.explicit()` 是
仅设置模式的选项的简写形式。

`promptCacheOptions.ttl` 取代了 `promptCacheRetention`，后者适用于比 `gpt-5.6` 更早的模型。
OpenAI 会拒绝同时携带两者的请求。

### `promptCacheBreakpoint`

`SystemMessage`、`UserMessage` 和 `ToolExecutionResultMessage` 都可以各自被标记为提示词缓存
断点。由于提示词缓存是基于前缀的，断点应用于被标记消息的**最后一个内容
块**，从而使得包括该消息在内的所有内容构成缓存前缀。

`OpenAiPromptCacheBreakpoint.mark()` 返回消息的已标记副本，原消息
保持不变：

```java
SystemMessage systemMessage = OpenAiPromptCacheBreakpoint.mark(SystemMessage.from(SHARED_INSTRUCTIONS));

UserMessage userMessage = OpenAiPromptCacheBreakpoint.mark(UserMessage.from(LONG_DOCUMENT));

ToolExecutionResultMessage toolResult = OpenAiPromptCacheBreakpoint.mark(someToolExecutionResultMessage);
```

标记实际上只是消息上的一个属性，因此也可以手动完成——例如当你
本来就在构建该消息时：

```java
SystemMessage systemMessage = SystemMessage.builder()
        .text(SHARED_INSTRUCTIONS)
        .attributes(Map.of(OpenAiPromptCacheBreakpoint.ATTRIBUTE_KEY,
                           OpenAiPromptCacheBreakpoint.MODE_EXPLICIT))
        .build();
```

标记消息后，LangChain4j 会将该消息的内容作为内容块列表发送，因为
纯字符串形式无法携带断点。

`AiMessage` 无法携带断点：助手输出块不在 OpenAI
接受断点的块类型之列。标记 `AiMessage` 或使用 `explicit` 以外的任何模式，
都会快速失败（fail fast），而不是产生 HTTP 400。

每个请求最多支持四次缓存写入，其中一次会被 `implicit` 模式消耗。

### 读取缓存 token 数

`OpenAiTokenUsage.InputTokensDetails` 报告从提示词缓存中读取和写入的
输入 token 数量：

```java
OpenAiTokenUsage tokenUsage = (OpenAiTokenUsage) chatResponse.tokenUsage();

tokenUsage.inputTokensDetails().cachedTokens();      // tokens read from the cache
tokenUsage.inputTokensDetails().cacheWriteTokens();  // tokens written to the cache
```

当模型提供商未报告该值时，`cacheWriteTokens()` 返回 `null`，这与
报告的零值不同。

## 访问原始 HTTP 响应和服务器发送事件（SSE）

使用 `OpenAiChatModel` 时，你可以访问原始 HTTP 响应：
```java
SuccessfulHttpResponse rawHttpResponse = ((OpenAiChatResponseMetadata) chatResponse.metadata()).rawHttpResponse();
System.out.println(rawHttpResponse.body());
System.out.println(rawHttpResponse.headers());
System.out.println(rawHttpResponse.statusCode());
```

使用 `OpenAiStreamingChatModel` 时，你可以访问原始 HTTP 响应（见上文）和原始服务器发送事件：
```java
List<ServerSentEvent> rawServerSentEvents = ((OpenAiChatResponseMetadata) chatResponse.metadata()).rawServerSentEvents();
System.out.println(rawServerSentEvents.get(0).data());
System.out.println(rawServerSentEvents.get(0).event());
```

## HTTP 客户端

### 纯 Java
使用 `langchain4j-open-ai` 模块时，
JDK 的 `java.net.http.HttpClient` 用作默认 HTTP 客户端。

你可以自定义它，或使用你选择的任何其他 HTTP 客户端。
更多信息见[这里](../../tutorials/customizable-http-client.md)。

### Spring Boot
使用 `langchain4j-open-ai-spring-boot4-starter`/`langchain4j-open-ai-spring-boot-starter` Spring Boot starter 时，
Spring 的 `RestClient` 用作默认 HTTP 客户端。

你可以自定义它，或使用你选择的任何其他 HTTP 客户端。
更多信息见[这里](../../tutorials/customizable-http-client.md)。

## OpenAI Responses API

!!! note
   此功能为实验性功能，可能在未来的版本中发生变化。

OpenAI 的 [Responses API](https://platform.openai.com/docs/api-reference/responses)（`/v1/responses`）是 Chat Completions API 的一种替代方案。

### 创建 `OpenAiResponsesChatModel`

```java
ChatModel model = OpenAiResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5.4")
        .build();
```

### 创建 `OpenAiResponsesStreamingChatModel`

```java
StreamingChatModel model = OpenAiResponsesStreamingChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();
```

### 自定义 HTTP 头

如果 OpenAI API 是通过认证代理或期望额外 HTTP 头的网关访问的，
可以在构建器上设置这些头。它们会随每个请求发送：
```java
ChatModel model = OpenAiResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .customHeaders(Map.of("Proxy-Authorization", "Basic dXNlcjpwYXNz"))
        .build();
```

如果头的值不是固定的（例如会过期且需要刷新的 OAuth2 token），
也可以提供一个 `Supplier`。它会在每个请求之前被调用：
```java
ChatModel model = OpenAiResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .customHeaders(() -> Map.of("Authorization", "Bearer " + tokenProvider.currentToken()))
        .build();
```

自定义头最后应用，因此也可用于覆盖
LangChain4j 默认设置的头（例如 `Authorization`）。

`OpenAiResponsesStreamingChatModel` 同理。

### `OpenAiResponsesChatRequestParameters`

`OpenAiResponsesChatRequestParameters` 在 `DefaultChatRequestParameters` 的基础上扩展了 Responses API 特有的字段：
`previousResponseId`、`maxToolCalls`、`parallelToolCalls`、`topLogprobs`、`truncation`、`include`、
`serviceTier`、`safetyIdentifier`、`promptCacheKey`、`promptCacheRetention`、`promptCacheOptions`、
`reasoningEffort`、`reasoningSummary`、`textVerbosity`、`streamIncludeObfuscation`、`store`、`strictTools`、
`strictJsonSchema`。

这些参数可以在创建模型时配置为默认值（通过构建器上的 `defaultRequestParameters`），
也可以通过 `ChatRequest` 按请求传递（按请求的参数覆盖默认值）：
```java
ChatRequest chatRequest = ChatRequest.builder()
        .messages(UserMessage.from("Hello"))
        .parameters(OpenAiResponsesChatRequestParameters.builder()
                .modelName("gpt-4o-mini")
                .previousResponseId("resp_abc123")
                .store(true)
                .build())
        .build();
```

### 配置内置 / 服务端工具

OpenAI Responses API 集成通过 `serverTools` 支持 OpenAI 内置工具。

- `serverTools` 用于以原始 OpenAI 形式表示的 OpenAI 内置工具

当你想在不引入额外类型化包装的情况下发送 `web_search`、`file_search` 或其他
OpenAI Responses API 工具对象时，请使用 `serverTools`：

```java
ChatModel model = OpenAiResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5.4")
        .serverTools(List.of(
                Map.of(
                        "type", "web_search",
                        "filters", Map.of("allowed_domains", List.of("openai.com", "developers.openai.com")),
                        "user_location", Map.of(
                                "type", "approximate",
                                "country", "US")),
                Map.of(
                        "type", "file_search",
                        "vector_store_ids", List.of("vs_abc123"),
                        "max_num_results", 3,
                        "filters", Map.of(
                                "type", "eq",
                                "key", "category",
                                "value", "blog"))))
        .build();
```

你也可以按请求配置内置工具：

```java
ChatRequest chatRequest = ChatRequest.builder()
        .messages(UserMessage.from("What's the weather in Berlin?"))
        .parameters(OpenAiResponsesChatRequestParameters.builder()
                .serverTools(List.of(Map.of("type", "web_search")))
                .build())
        .build();

ChatResponse response = model.chat(chatRequest);
```

`serverTools` 既可以在模型构建器上配置为默认值，也可以通过
`OpenAiResponsesChatRequestParameters` 按请求配置。当两者都提供时，按请求的值优先，
并替换该请求的模型级 `serverTools`。

`serverTools` 是提供商特定的，并且有意镜像 OpenAI 的线上格式（wire format），
因此嵌套的工具字段应以普通的 `Map` / `List` 值提供。

### 思考 / 推理
OpenAI 推理模型（如 `gpt-5.4`、`gpt-5-mini`）支持
[推理摘要](https://developers.openai.com/api/docs/guides/reasoning#reasoning-summaries)，
它公开模型内部推理的摘要。

要启用推理摘要，在构建器上将 `reasoningSummary` 设置为 `"auto"`
（或通过 `OpenAiResponsesChatRequestParameters` 设置）。
你还可以使用 `reasoningEffort` 控制模型在推理上投入多少精力。

```java
ChatModel model = OpenAiResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5-mini")
        .reasoningEffort("low")
        .reasoningSummary("auto")
        .build();

ChatResponse response = model.chat("What is the capital of Germany?");
response.aiMessage().text();     // "The capital of Germany is Berlin."
response.aiMessage().thinking(); // reasoning summary text
```

当为 `OpenAiResponsesStreamingChatModel` 设置了 `reasoningSummary` 时，
随着推理摘要 token 的流式传输，
将调用 `StreamingChatResponseHandler.onPartialThinking()` 回调：

```java
StreamingChatModel model = OpenAiResponsesStreamingChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5-mini")
        .reasoningEffort("low")
        .reasoningSummary("auto")
        .build();
```

`AiMessage.thinking()` 中的推理摘要仅供参考，无需在
后续请求中回传——OpenAI 会在轮次之间丢弃它。要真正跨轮次保留模型的推理
状态（例如在工具调用之间），请使用下面描述的加密推理。

#### 加密推理（在上下文中保留推理）

当 `store` 为 `false`（默认值）或你的组织启用了零数据保留时，
模型的推理上下文会在轮次之间丢失。
要保留推理上下文，请通过 `include` 参数请求[加密推理内容](https://developers.openai.com/api/docs/guides/reasoning#keeping-reasoning-items-in-context)：

```java
ChatModel model = OpenAiResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5-mini")
        .reasoningEffort("medium")
        .include(List.of("reasoning.encrypted_content"))
        .build();
```

当 `include` 包含 `"reasoning.encrypted_content"` 时，响应中的推理项
将包含一个不透明的加密数据块。它会自动存储在
`AiMessage.attributes()` 中，键为 `"encrypted_reasoning"`。

当你在后续请求中回传该 `AiMessage` 时（例如在工具调用之后），
加密推理会自动包含在请求中，
使模型能够恢复其推理上下文：

```java
// Turn 1: model calls a tool
ChatResponse response1 = model.chat(ChatRequest.builder()
        .messages(userMessage)
        .parameters(ChatRequestParameters.builder()
                .toolSpecifications(weatherTool)
                .build())
        .build());

AiMessage aiMessage1 = response1.aiMessage();
// aiMessage1.attribute("encrypted_reasoning", String.class) is not null

// Turn 2: send tool result back — encrypted reasoning is sent automatically
ChatResponse response2 = model.chat(ChatRequest.builder()
        .messages(
                userMessage,
                aiMessage1, // contains encrypted reasoning in attributes
                ToolExecutionResultMessage.from(aiMessage1.toolExecutionRequests().get(0), "sunny"))
        .parameters(ChatRequestParameters.builder()
                .toolSpecifications(weatherTool)
                .build())
        .build());
```

`OpenAiResponsesStreamingChatModel` 的行为与此完全相同。

### `OpenAiResponsesChatResponseMetadata`

Responses API 的响应元数据在标准 `ChatResponseMetadata` 之外提供了额外的字段：

```java
OpenAiResponsesChatResponseMetadata metadata =
        (OpenAiResponsesChatResponseMetadata) chatResponse.metadata();

metadata.id();               // Response ID (can be used as previousResponseId)
metadata.modelName();        // Model name used for the request
metadata.finishReason();     // Finish reason (STOP, LENGTH, TOOL_EXECUTION, CONTENT_FILTER, OTHER)
metadata.tokenUsage();       // Returns OpenAiTokenUsage with detailed token counts
metadata.createdAt();        // Timestamp when the response was created
metadata.completedAt();      // Timestamp when the response was completed
metadata.serviceTier();      // Service tier used for the request

// Raw HTTP access (same as Chat Completions API)
metadata.rawHttpResponse();
metadata.rawServerSentEvents();
```

## 示例
- [OpenAI 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/open-ai-examples/src/main/java)
