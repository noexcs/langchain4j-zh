# OpenAI 官方 SDK

!!! note
   本文档介绍 `OpenAI Official SDK` 集成，该集成使用[官方 OpenAI Java SDK](https://github.com/openai/openai-java)。
   LangChain4j 提供了 3 种不同的 OpenAI 集成用于使用聊天模型，这是其中的第 2 种：
   - [OpenAI](open-ai.md) 使用自定义的 OpenAI REST API Java 实现，与 Quarkus（使用 Quarkus REST 客户端）和 Spring（使用 Spring 的 RestClient）配合效果最佳。
   - [OpenAI Official SDK](open-ai-official.md) 使用官方 OpenAI Java SDK。
   - [Azure OpenAI](azure-open-ai.md) 使用微软的 Azure SDK，如果你使用微软 Java 技术栈（包括高级 Azure 认证机制），它与你的环境配合效果最佳。

## 此集成的适用场景

此集成使用 [OpenAI Java SDK GitHub 仓库](https://github.com/openai/openai-java)，将适用于所有可由以下渠道提供的 OpenAI 模型：

- OpenAI
- Microsoft Foundry
- GitHub Models

它也适用于支持 OpenAI API 的模型，例如 DeepSeek。

## OpenAI 文档

- [OpenAI Java SDK GitHub 仓库](https://github.com/openai/openai-java)
- [OpenAI API 文档](https://platform.openai.com/docs/introduction)
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-official</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 配置模型

!!! note
   本配置以及下一节关于其用法的说明均针对非流式模式（也称为"阻塞"或"同步"模式）。
   流式模式将在下面第 2 节中详细介绍：它允许与模型实时聊天，但使用更复杂。

要使用 OpenAI 模型，你通常需要端点 URL、API 密钥和模型名称。这取决于模型的托管位置，此集成通过一些自动配置使这一点更简单：

### 通用配置

```java
import com.openai.models.ChatModel;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openaiofficial.OpenAiOfficialChatModel;

import static com.openai.models.ChatModel.GPT_5_MINI;

// ....

ChatModel model = OpenAiOfficialChatModel.builder()
        .baseUrl(System.getenv("OPENAI_BASE_URL"))
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(GPT_5_MINI)
        .build();
```

### OpenAI 配置

OpenAI 的 `baseUrl`（`https://api.openai.com/v1`）是默认值，因此你可以省略它：

```java
ChatModel model = OpenAiOfficialChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(GPT_5_MINI)
        .build();
```

### Azure OpenAI 配置

#### 通用配置

对于 Azure OpenAI，设置 `baseUrl` 是必需的；如果该 URL 以 `openai.azure.com` 结尾，将自动检测到 Azure OpenAI：

```java
ChatModel model = OpenAiOfficialChatModel.builder()
        .baseUrl(System.getenv("AZURE_OPENAI_ENDPOINT"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .modelName(GPT_5_MINI)
        .build();
```

如果你想要强制使用 Azure OpenAI，也可以使用 `isAzure()` 方法：

```java
ChatModel model = OpenAiOfficialChatModel.builder()
        .baseUrl(System.getenv("AZURE_OPENAI_ENDPOINT"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .isAzure(true)
        .modelName(GPT_5_MINI)
        .build();
```

#### 无密码认证

你可以使用"无密码"（passwordless）认证来访问 Azure OpenAI，这更安全，因为你无需管理 API 密钥。

为此，你必须先配置你的 Azure OpenAI 实例以支持托管标识（managed identity），然后授予此应用访问权限，例如：

```bash
# Enable system managed identity on the Azure OpenAI instance
az cognitiveservices account identity assign \
    --name <your-openai-instance-name> \
    --resource-group <your-resource-group>

# Get your logged-in identity
az ad signed-in-user show \
    --query id -o tsv
    
# Give access to the Azure OpenAI instance
az role assignment create \
    --role "Cognitive Services OpenAI User" \
    --assignee <your-logged-identity-from-the-previous-command> \
    --scope "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group>"
```

然后，你需要在 Maven `pom.xml` 中添加 `azure-identity` 依赖：

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
</dependency>
```

当未配置 API 密钥时，LangChain4j 将自动使用无密码认证访问 Azure OpenAI。

### GitHub Models 配置

对于 GitHub Models，你可以使用默认的 `baseUrl`（`https://models.inference.ai.azure.com`）：

```java
ChatModel model = OpenAiOfficialChatModel.builder()
        .baseUrl("https://models.inference.ai.azure.com")
        .apiKey(System.getenv("GITHUB_TOKEN"))
        .modelName(GPT_5_MINI)
        .build();
```

或者，你可以使用 `isGitHubModels()` 方法来强制使用 GitHub Models，该方法会自动设置 `baseUrl`：

```java
ChatModel model = OpenAiOfficialChatModel.builder()
        .apiKey(System.getenv("GITHUB_TOKEN"))
        .modelName(GPT_5_MINI)
        .isGitHubModels(true)
        .build();
```

由于 GitHub Models 通常使用 `GITHUB_TOKEN` 环境变量配置，而在使用 GitHub Actions 或 GitHub Codespaces 时该变量会自动填充，因此它会被自动检测到：

```java
ChatModel model = OpenAiOfficialChatModel.builder()
        .modelName(GPT_5_MINI)
        .isGitHubModels(true)
        .build();
```

最后这种配置使用起来更简单，也更安全，因为 `GITHUB_TOKEN` 环境变量不会暴露在代码或 GitHub 日志中。

## 使用模型

在上一节中，创建了一个 `OpenAiOfficialChatModel` 对象，它实现了 `ChatModel` 接口。

它既可以由 [AI 服务](../../tutorials/spring-boot-integration.md#spring-boot-starters) 使用，也可以直接在 Java 应用中使用。

在这个示例中，它作为 Spring Bean 自动注入：

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

[Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) 功能同时支持 [tools](../../tutorials/tools.md) 和 [response format](../../tutorials/ai-services.md#json-模式)。

有关结构化输出的更多信息见 [这里](../../tutorials/structured-outputs.md)。

### 用于工具的 Structured Outputs

要为工具启用 Structured Outputs 功能，在构建模型时设置 `.strictTools(true)`：

```java
OpenAiOfficialChatModel.builder()
        // ...
        .strictTools(true)
        .build();
```

请注意，这将自动使所有工具参数变为必填项（json schema 中的 `required`），
并为 json schema 中的每个 `object` 设置 `additionalProperties=false`。这是由 OpenAI 当前的限制导致的。

### 用于响应格式的 Structured Outputs

要在 AI 服务中使用响应格式化时启用 Structured Outputs 功能，
在构建模型时设置 `supportedCapabilities(Set.of(RESPONSE_FORMAT_JSON_SCHEMA))` 和 `.strictJsonSchema(true)`：

```java
import static dev.langchain4j.model.chat.Capability.RESPONSE_FORMAT_JSON_SCHEMA;

// ...

OpenAiChatModel.builder()
        // ...
        .supportedCapabilities(Set.of(RESPONSE_FORMAT_JSON_SCHEMA))
        .strictJsonSchema(true)
        .build();
```

在这种情况下，AI 服务将自动从给定的 POJO 生成 JSON schema 并将其传递给 LLM。

## 为流式配置模型

!!! note
   在上面两节中，我们详细介绍了如何为非流式模式（也称为"阻塞"或"同步"模式）配置模型。
   本节针对流式模式，它允许与模型实时聊天，但使用更复杂。

这与非流式模式类似，但你需要使用 `OpenAiOfficialStreamingChatModel` 类而不是 `OpenAiOfficialChatModel`：

```java
StreamingChatModel model = OpenAiOfficialStreamingChatModel.builder()
        .baseUrl(System.getenv("OPENAI_BASE_URL"))
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(GPT_5_MINI)
        .build();
```

你也可以使用特定的 `isAzure()` 和 `isGitHubModels()` 方法来强制使用 Azure OpenAI 或 GitHub Models，详见非流式配置章节。

## 提示词缓存

OpenAI 会缓存较长、重复的提示词前缀，并按输入单价的一小部分对缓存读取计费。
以下控制项同时适用于 Chat Completions API 模型和 Responses API 模型。

有关提示词缓存的更多信息见 [这里](https://developers.openai.com/api/docs/guides/prompt-caching)。

### `promptCacheKey` 与 `promptCacheOptions`

`promptCacheKey` 是一个可选字符串，用于引导路由，使相关请求更有可能到达持有缓存条目的机器。它不会将请求固定到某台机器，也不保证缓存命中。

`gpt-5.6` 及之后的版本会在*断点（breakpoint）*处精确匹配缓存的前缀，而不会回退到更短的未标记前缀。`promptCacheOptions` 控制断点的来源：

- `implicit` - OpenAI 在最新合格消息的末尾放置断点。
- `explicit` - 只使用你设置的断点。如果没有断点，则什么都不会被缓存。

对于 Responses API 模型，两者都可以在模型构建器上使用：

```java
OpenAiOfficialResponsesChatModel model = OpenAiOfficialResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5.6")
        .promptCacheKey("satisfaction_judge_v1")
        .promptCacheOptions(OpenAiOfficialPromptCacheOptions.builder()
                .mode(OpenAiOfficialPromptCacheOptions.MODE_EXPLICIT)
                .ttl(OpenAiOfficialPromptCacheOptions.TTL_30M)
                .build())
        .build();
```

对于 Chat Completions API 模型，通过 `OpenAiOfficialChatRequestParameters` 设置，既可以作为模型默认值，也可以逐请求设置：

```java
OpenAiOfficialChatModel model = OpenAiOfficialChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5.6")
        .defaultRequestParameters(OpenAiOfficialChatRequestParameters.builder()
                .promptCacheKey("satisfaction_judge_v1")
                .promptCacheOptions(OpenAiOfficialPromptCacheOptions.explicit())
                .build())
        .build();
```

`OpenAiOfficialPromptCacheOptions.implicit()` 和 `OpenAiOfficialPromptCacheOptions.explicit()` 是只设置 mode 的选项的简写。

`promptCacheOptions.ttl` 取代 `promptCacheRetention`，后者适用于早于 `gpt-5.6` 的模型。
OpenAI 会拒绝同时携带两者的请求。

### `promptCacheBreakpoint`

`SystemMessage`、`UserMessage` 和 `ToolExecutionResultMessage` 都可以各自被标记为提示词缓存断点。由于提示词缓存基于前缀，断点会应用于被标记消息的**最后一个内容块**，使得从开头到该消息（含）的所有内容都构成缓存前缀。

`OpenAiOfficialPromptCacheBreakpoint.mark()` 返回一个被标记的消息副本，原消息保持不变：

```java
SystemMessage systemMessage = OpenAiOfficialPromptCacheBreakpoint.mark(SystemMessage.from(SHARED_INSTRUCTIONS));

UserMessage userMessage = OpenAiOfficialPromptCacheBreakpoint.mark(UserMessage.from(LONG_DOCUMENT));

ToolExecutionResultMessage toolResult = OpenAiOfficialPromptCacheBreakpoint.mark(someToolExecutionResultMessage);
```

标记实际上只是消息上的一个属性，因此也可以手动完成——例如，当你本来就在构建消息时：

```java
SystemMessage systemMessage = SystemMessage.builder()
        .text(SHARED_INSTRUCTIONS)
        .attributes(Map.of(OpenAiOfficialPromptCacheBreakpoint.ATTRIBUTE_KEY,
                           OpenAiOfficialPromptCacheBreakpoint.MODE_EXPLICIT))
        .build();
```

标记一个消息后，LangChain4j 会以内容块列表的形式发送该消息的内容，因为纯字符串形式无法携带断点。

`AiMessage` 无法携带断点：助手输出块不属于 OpenAI 接受断点的块类型。对 `AiMessage` 进行标记，或使用 `explicit` 以外的任何 mode，都会快速失败，而不是产生 HTTP 400。

每个请求最多支持四次缓存写入，其中 `implicit` 模式会消耗其中一次。

### 读取缓存 token 计数

`OpenAiOfficialTokenUsage.InputTokensDetails` 报告从提示词缓存读取和写入的输入 token 数：

```java
OpenAiOfficialTokenUsage tokenUsage = (OpenAiOfficialTokenUsage) chatResponse.tokenUsage();

tokenUsage.inputTokensDetails().cachedTokens();      // tokens read from the cache
tokenUsage.inputTokensDetails().cacheWriteTokens();  // tokens written to the cache
```

当模型提供商未报告 `cacheWriteTokens()` 时，它返回 `null`，这与报告的零值不同。

## OpenAI Responses API

!!! note
   此功能是实验性的，可能在未来版本中变化。

OpenAI 的 [Responses API](https://platform.openai.com/docs/api-reference/responses)（`/v1/responses`）是 Chat Completions API 的替代方案。

### 创建 `OpenAiOfficialResponsesChatModel`

```java
ChatModel model = OpenAiOfficialResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5.4")
        .build();
```

### 创建 `OpenAiOfficialResponsesStreamingChatModel`

```java
StreamingChatModel model = OpenAiOfficialResponsesStreamingChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(GPT_5_MINI)
        .build();
```

你还可以使用 `OpenAiOfficialResponsesChatRequestParameters` 配置默认请求参数：
```java
StreamingChatModel model = OpenAiOfficialResponsesStreamingChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .defaultRequestParameters(OpenAiOfficialResponsesChatRequestParameters.builder()
                .modelName("gpt-4o-mini")
                .previousResponseId("resp_abc123")
                .reasoningEffort("medium")
                .store(true)
                .build())
        .build();
```

### `OpenAiOfficialResponsesChatRequestParameters`

`OpenAiOfficialResponsesChatRequestParameters` 扩展 `DefaultChatRequestParameters`，包含 Responses API 特有的字段：
`previousResponseId`、`maxToolCalls`、`parallelToolCalls`、`topLogprobs`、`truncation`、`include`、
`serviceTier`、`safetyIdentifier`、`promptCacheKey`、`promptCacheRetention`、`promptCacheOptions`、
`reasoningEffort`、`reasoningSummary`、`textVerbosity`、`streamIncludeObfuscation`、`store`、`strictTools`、
`strictJsonSchema`。

这些参数可以在创建模型时配置为默认值（通过构建器上的 `defaultRequestParameters`），
也可以通过 `ChatRequest` 逐请求传递（逐请求参数会覆盖默认值）：
```java
ChatRequest chatRequest = ChatRequest.builder()
        .messages(UserMessage.from("Hello"))
        .parameters(OpenAiOfficialResponsesChatRequestParameters.builder()
                .modelName("gpt-4o-mini")
                .previousResponseId("resp_abc123")
                .store(true)
                .build())
        .build();
```

### 思考 / 推理
OpenAI 推理模型（例如 `gpt-5.4`、`gpt-5-mini`）支持
[推理摘要（reasoning summaries）](https://developers.openai.com/api/docs/guides/reasoning#reasoning-summaries)，
它会公开模型内部推理的摘要。

要启用推理摘要，在构建器上将 `reasoningSummary` 设置为 `Reasoning.Summary.AUTO`
（或通过 `OpenAiOfficialResponsesChatRequestParameters` 设置）。
你还可以使用 `reasoningEffort` 控制模型投入推理的精力程度。

```java
ChatModel model = OpenAiOfficialResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5-mini")
        .reasoningEffort(ReasoningEffort.LOW)
        .reasoningSummary(Reasoning.Summary.AUTO)
        .build();

ChatResponse response = model.chat("What is the capital of Germany?");
response.aiMessage().text();     // "The capital of Germany is Berlin."
response.aiMessage().thinking(); // reasoning summary text
```

当为 `OpenAiOfficialResponsesStreamingChatModel` 设置了 `reasoningSummary` 时，
`StreamingChatResponseHandler.onPartialThinking()` 回调将在推理摘要 token 被流式传输时被调用：

```java
StreamingChatModel model = OpenAiOfficialResponsesStreamingChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5-mini")
        .reasoningEffort(ReasoningEffort.LOW)
        .reasoningSummary(Reasoning.Summary.AUTO)
        .build();
```

`AiMessage.thinking()` 中的推理摘要仅供参考，无需在后续请求中发送回去——
OpenAI 会在轮次之间丢弃它。要实际跨轮次保留模型的推理状态（例如在工具调用之间），
请改用下方描述的加密推理（encrypted reasoning）。

#### 加密推理（在上下文中保留推理）

当 `store` 为 `false`（默认）或你的组织启用了零数据保留时，
模型的推理上下文会在轮次之间丢失。
要保留它，请通过 `include` 参数请求[加密推理内容](https://developers.openai.com/api/docs/guides/reasoning#keeping-reasoning-items-in-context)：

```java
ChatModel model = OpenAiOfficialResponsesChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-5-mini")
        .reasoningEffort(ReasoningEffort.MEDIUM)
        .include(List.of("reasoning.encrypted_content"))
        .build();
```

当 `include` 包含 `"reasoning.encrypted_content"` 时，响应的推理条目
将包含一个不透明的加密 blob。它会自动存储在
`AiMessage.attributes()` 中，键为 `"encrypted_reasoning"`。

当你在后续请求（例如工具调用之后）传回该 `AiMessage` 时，
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

对 `OpenAiOfficialResponsesStreamingChatModel` 的行为完全相同。

### `OpenAiOfficialResponsesChatResponseMetadata`

Responses API 的响应元数据在标准 `ChatResponseMetadata` 之外提供了额外字段：

```java
OpenAiOfficialResponsesChatResponseMetadata metadata =
        (OpenAiOfficialResponsesChatResponseMetadata) chatResponse.metadata();

metadata.id();               // Response ID (can be used as previousResponseId)
metadata.modelName();        // Model name used for the request
metadata.finishReason();     // Finish reason (STOP, LENGTH, TOOL_EXECUTION, CONTENT_FILTER, OTHER)
metadata.tokenUsage();       // Returns OpenAiOfficialTokenUsage with detailed token counts
metadata.createdAt();        // Timestamp when the response was created
metadata.completedAt();      // Timestamp when the response was completed
metadata.serviceTier();      // Service tier used for the request
```

## 批处理

`OpenAiOfficialBatchChatModel` 实现了核心的 `BatchChatModel` 接口，可通过 [OpenAI Batch API](https://platform.openai.com/docs/guides/batch) 异步处理大量聊天请求，价格为标准每 token 价格的 50%。

请求被写入 JSONL 文件，以 `batch` 用途通过 Files API 上传，并针对 `/v1/chat/completions` 端点运行。一个批次中的所有请求必须解析为同一个模型。结果保持提交顺序，因此第 i 个结果对应第 i 个请求，无论其成功还是失败。

```java
OpenAiOfficialBatchChatModel batchModel = OpenAiOfficialBatchChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();

BatchResponse<ChatResponse> submitted = batchModel.submit(new BatchRequest<>(List.of(
        ChatRequest.builder().messages(UserMessage.from("What is the capital of France?")).build(),
        ChatRequest.builder().messages(UserMessage.from("What is the capital of Germany?")).build())));

String batchId = submitted.batchId();

// Poll until the batch reaches a terminal state (SUCCEEDED, FAILED, CANCELLED, EXPIRED).
BatchResponse<ChatResponse> batch = batchModel.retrieve(batchId);
while (!batch.state().isTerminal()) {
    Thread.sleep(Duration.ofSeconds(30).toMillis());
    batch = batchModel.retrieve(batchId);
}

for (BatchItemResult<ChatResponse> result : batch.results()) {
    if (result.isSuccess()) {
        System.out.println(result.response().aiMessage().text());
    } else {
        System.out.println("Failed: " + result.error().message());
    }
}
```

正在运行的批次可以被取消，现有批次可以分页列出：
```java
batchModel.cancel(batchId);

BatchPage<ChatResponse> page = batchModel.list(new BatchPagination(20, null));
```

同样支持 Azure OpenAI，其中模型由其批处理部署名称标识；任何实现了 Files API 和 Batch API 的 OpenAI 兼容端点也受支持。

批处理特定的选项可以在构建器上设置：
```java
OpenAiOfficialBatchChatModel batchModel = OpenAiOfficialBatchChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .completionWindow("24h")                          // defaults to 24h
        .batchMetadata(Map.of("owner", "nightly-job"))    // attached to the batch itself
        .inputFileExpiresAfter(Duration.ofDays(14))
        .outputExpiresAfter(Duration.ofDays(7))
        .build();
```
