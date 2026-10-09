# Anthropic

- [Anthropic 文档](https://docs.anthropic.com/en/home)
- [Anthropic API 参考](https://docs.anthropic.com/en/api/overview)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-anthropic</artifactId>
    <version>1.22.0</version>
</dependency>
```

## AnthropicChatModel

```java
AnthropicChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName(CLAUDE_3_5_SONNET_20240620)
    .build();
String answer = model.chat("Say 'Hello World'");
System.out.println(answer);
```

### 自定义 AnthropicChatModel
```java
AnthropicChatModel model = AnthropicChatModel.builder()
    .httpClientBuilder(...)
    .baseUrl(...)
    .apiKey(...)
    .version(...)
    .beta(...)
    .modelName(...)
    .temperature(...)
    .topP(...)
    .topK(...)
    .maxTokens(...)
    .stopSequences(...)
    .toolSpecifications(...)
    .toolChoice(...)
    .toolChoiceName(...)
    .disableParallelToolUse(...)
    .serverTools(...)
    .returnServerToolResults(...)
    .toolMetadataKeysToSend(...)
    .cacheSystemMessages(...)
    .cacheTools(...)
    .cacheAutomatically(...)
    .cacheTtl(...)
    .returnCacheDiagnostics(...)
    .thinkingType(...)
    .thinkingBudgetTokens(...)
    .thinkingDisplay(...)
    .returnThinking(...)
    .sendThinking(...)
    .midConversationSystemMessages(...)
    .timeout(...)
    .maxRetries(...)
    .logRequests(...)
    .logResponses(...)
    .listeners(...)
    // You can also specify default chat request parameters using ChatRequestParameters or AnthropicChatRequestParameters
    .defaultRequestParameters(...)
    .userId(...)
    .customParameters(...)
    .build();
```
上面部分参数的说明见[此处](https://docs.anthropic.com/en/api/messages)。

### 按请求的参数

上面所示的 Anthropic 专属选项（`cacheSystemMessages`、`cacheTools`、`cacheAutomatically`、
`cacheTtl`、`returnCacheDiagnostics`、
`thinkingType`、`thinkingBudgetTokens`、`sendThinking`、`returnThinking`、`midConversationSystemMessages`、
`toolChoiceName`、`disableParallelToolUse` 和 `userId`），以及 `previousMessageId`（仅请求级，参见
[缓存诊断](#缓存诊断)），
也可以通过 `AnthropicChatRequestParameters` 按请求设置，覆盖在模型构建器上配置的值。这使得单个共享的
模型实例能在每次调用之间改变这些选项——例如，为长时间运行的智能体循环启用提示词缓存，而对廉价的
一次性补全则跳过，而无需构建第二个模型：

```java
AnthropicChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName(CLAUDE_3_5_SONNET_20240620)
    .build();

AnthropicChatRequestParameters parameters = AnthropicChatRequestParameters.builder()
    .cacheSystemMessages(true)
    .cacheTools(true)
    .build();

ChatRequest chatRequest = ChatRequest.builder()
    .messages(systemMessage, userMessage)
    .parameters(parameters)
    .build();

ChatResponse chatResponse = model.chat(chatRequest);
```

未在请求上设置的任何参数都会回退到在模型构建器上配置的值。

## AnthropicStreamingChatModel
```java
AnthropicStreamingChatModel model = AnthropicStreamingChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName(CLAUDE_3_5_SONNET_20240620)
    .build();

model.chat("Say 'Hello World'", new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        // this method is called when a new partial response is available. It can consist of one or more tokens.
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        // this method is called when the model has completed responding
    }

    @Override
    public void onError(Throwable error) {
        // this method is called when an error occurs
    }
});
```

### 自定义 AnthropicStreamingChatModel

与 `AnthropicChatModel` 相同，参见上文。

## 批处理 API

[消息批次 API](https://docs.anthropic.com/en/api/creating-message-batches)以标准每 token 价格的 50%
异步处理大量聊天请求。`AnthropicBatchChatModel` 实现了核心 `BatchChatModel` 接口（`submit`、`retrieve`、
`cancel`、`list`）。每个请求都使用 `AnthropicChatModel` 调用所使用的相同参数提交。

```java
AnthropicBatchChatModel model = AnthropicBatchChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName("claude-sonnet-4-5")
    .maxTokens(1024)
    .build();

// Submit a batch of requests
BatchResponse<ChatResponse> submitted = model.submit(new BatchRequest<>(List.of(
    ChatRequest.builder().messages(UserMessage.from("What is the capital of France?")).build(),
    ChatRequest.builder().messages(UserMessage.from("What is the capital of Germany?")).build())));

String batchId = submitted.batchId();

// Poll until the batch reaches a terminal state (typically well under an hour)
BatchResponse<ChatResponse> batch = model.retrieve(batchId);
while (!batch.state().isTerminal()) {
    TimeUnit.SECONDS.sleep(30); // throws InterruptedException
    batch = model.retrieve(batchId);
}

// Read the per-request results, in submission order
for (BatchItemResult<ChatResponse> result : batch.results()) {
    if (result.isSuccess()) {
        System.out.println(result.response().aiMessage().text());
    } else {
        System.out.println("Failed: " + result.error().message());
    }
}
```

使用 `model.list(...)` 分页浏览最近的批次，使用 `model.cancel(batchId)` 取消仍在处理中的批次。你取消的
批次在 Anthropic 一侧同样以 `ended` 状态结束，并报告为 `BatchState.CANCELLED`；其中可能仍包含在取消
生效之前已完成的请求的结果。

诸如思考（thinking）或提示词缓存等 Anthropic 专属选项通过 `defaultRequestParameters(...)` 配置，
与 `AnthropicChatModel` 完全相同，并且可以按请求覆盖：

```java
AnthropicBatchChatModel model = AnthropicBatchChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName("claude-sonnet-4-5")
    .maxTokens(4096)
    .defaultRequestParameters(AnthropicChatRequestParameters.builder()
        .thinkingType("enabled")
        .thinkingBudgetTokens(2000)
        .cacheSystemMessages(true)
        .cacheTtl("1h") // batches can take longer than the default 5-minute cache TTL
        .build())
    .returnThinking(true) // store the returned thinking in AiMessage.thinking()
    .build();
```

## 工具

Anthropic 在流式和非流式模式下都支持[工具](../../tutorials/tools.md)。

关于工具的 Anthropic 文档可[在此](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview)找到。

## 工具选择

Anthropic 的[工具选择](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#forcing-tool-use)
功能可用于流式和非流式交互：

- `toolChoice(ToolChoice.REQUIRED)` 强制模型调用可用工具之一，而不是用文本回答。
- `toolChoiceName("get_weather")` 强制模型调用某个特定工具。它可以单独使用，当同时设置了
  `toolChoice(ToolChoice)` 时，指定名称的工具优先于它。

## 并行工具使用

默认情况下，Anthropic Claude 可能会使用多个工具来回答用户查询，但你可以通过设置 `disableParallelToolUse(true)`
来禁用[并行工具](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/implement-tool-use#parallel-tool-use)。

## 服务端工具

Anthropic 的[服务端工具](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview#server-tools)
通过 `serverTools` 参数支持，下面是使用[网页搜索工具](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)的示例：
```java
AnthropicServerTool webSearchTool = AnthropicServerTool.builder()
        .type("web_search_20250305")
        .name("web_search")
        .addAttribute("max_uses", 5)
        .addAttribute("allowed_domains", List.of("accuweather.com"))
        .build();

ChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName("claude-sonnet-4-5")
        .serverTools(webSearchTool)
        .logRequests(true)
        .logResponses(true)
        .build();

String answer = model.chat("What is the weather in Munich?");
```

通过 `serverTools` 指定的工具会包含在发往 Anthropic API 的每个请求中。

### 获取服务端工具结果

要访问来自服务端工具的原始结果（例如，网页搜索结果、代码执行输出、生成文件的 fileIds），请启用
`returnServerToolResults(true)`。结果将在 `AiMessage.attributes()` 中，位于键 `"server_tool_results"` 下：

```java
ChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName("claude-sonnet-4-5")
        .serverTools(webSearchTool)
        .returnServerToolResults(true)
        .build();

ChatResponse response = model.chat("What is the weather in Munich?");
AiMessage aiMessage = response.aiMessage();

List<AnthropicServerToolResult> results = aiMessage.attribute("server_tool_results", List.class);
for (AnthropicServerToolResult result : results) {
    System.out.println("Type: " + result.type());
    System.out.println("Tool Use ID: " + result.toolUseId());
    System.out.println("Content: " + result.content());
}
```

为避免在聊天记忆中存储可能较大的数据，此功能默认禁用。

## 技能

Anthropic 的[Agent Skills](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview)
让 Claude 通过在代码执行容器内运行预构建的技能，生成真正可下载的文件（`.xlsx`、`.pptx`、`.docx`、`.pdf`）。
通过带类型的 `skills` 参数启用它们：

```java
AnthropicChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName("claude-opus-4-8")
        .maxTokens(4096)
        .beta("code-execution-2025-08-25,skills-2025-10-02,files-api-2025-04-14")
        .skills(AnthropicSkill.XLSX, AnthropicSkill.PPTX)
        .returnServerToolResults(true)
        .build();

ChatResponse response = model.chat("Create an Excel spreadsheet with the numbers 1 to 5 in column A");
```

启用技能会自动：

- 在请求中添加 `container.skills` 块，
- 添加所需的 `code_execution` 服务端工具（除非已通过 `serverTools(...)` 配置了一个）。

你必须自己通过 `beta(...)` 选择加入所需的 beta 特性，如上所示。这些是 beta 请求头，其值会随时间变化，
因此不会替你自动注入——请查阅[Agent Skills 文档](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/overview)
了解当前的集合。

将其与 `returnServerToolResults(true)` 结合使用，可在 `AiMessage.attributes()` 的 `"server_tool_results"`
键下展示生成的文件 ID（参见上文[获取服务端工具结果](#获取服务端工具结果)）；这些文件可通过
Anthropic 的 Files API 在 24 小时内下载。

技能受 Claude Sonnet 4 / 4.5、Opus 4 及更高版本支持。每个请求最多可启用 8 个技能。
相同的 `skills(...)` 参数在 `AnthropicStreamingChatModel` 上也可用。

## 工具搜索工具

Anthropic 的[工具搜索工具](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool)
通过 `serverTools`、工具 `metadata` 和 `toolMetadataKeysToSend` 参数支持。

下面是使用高层 AI 服务和 `@Tool` API 的示例：

```java
AnthropicServerTool toolSearchTool = AnthropicServerTool.builder()
        .type("tool_search_tool_regex_20251119")
        .name("tool_search_tool_regex")
        .build();

class Tools {

    @Tool(metadata = "{\"defer_loading\": true}")
    String getWeather(String location) {
        return "sunny";
    }

    @Tool
    String getTime(String location) {
        return "12:34:56";
    }
}

ChatModel chatModel = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName(CLAUDE_SONNET_4_5_20250929)
        .beta("advanced-tool-use-2025-11-20")
        .serverTools(toolSearchTool)
        .toolMetadataKeysToSend("defer_loading") // need to specify it explicitly
        .logRequests(true)
        .logResponses(true)
        .build();

interface Assistant {

    @SystemMessage("Use tool search if needed")
    String chat(String userMessage);
}

Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(new Tools())
        .build();

assistant.chat("What is the weather in Munich?");
```

下面是使用底层 `ChatModel` 和 `ToolSpecification` API 的示例：
```java
AnthropicServerTool toolSearchTool = AnthropicServerTool.builder()
        .type("tool_search_tool_regex_20251119")
        .name("tool_search_tool_regex")
        .build();

Map<String, Object> toolMetadata = Map.of("defer_loading", true);

ToolSpecification weatherTool = ToolSpecification.builder()
        .name("get_weather")
        .parameters(JsonObjectSchema.builder()
                .addStringProperty("location")
                .required("location")
                .build())
        .metadata(toolMetadata)
        .build();

ToolSpecification timeTool = ToolSpecification.builder()
        .name("get_time")
        .parameters(JsonObjectSchema.builder()
                .addStringProperty("location")
                .required("location")
                .build())
        .build();

ChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName(CLAUDE_SONNET_4_5_20250929)
        .beta("advanced-tool-use-2025-11-20")
        .serverTools(toolSearchTool)
        .toolMetadataKeysToSend(toolMetadata.keySet()) // need to specify it explicitly
        .logRequests(true)
        .logResponses(true)
        .build();

ChatRequest chatRequest = ChatRequest.builder()
        .messages(UserMessage.from("What is the weather in Munich? Use tool search if needed."))
        .toolSpecifications(weatherTool, timeTool)
        .build();

ChatResponse chatResponse = model.chat(chatRequest);
```

### 编程式工具调用

Anthropic 的[编程式工具调用](https://www.anthropic.com/engineering/advanced-tool-use)
通过 `serverTools`、工具 `metadata` 和 `toolMetadataKeysToSend` 参数支持。

下面是使用高层 AI 服务和 `@Tool` API 的示例：

```java
AnthropicServerTool codeExecutionTool = AnthropicServerTool.builder()
        .type("code_execution_20250825")
        .name("code_execution")
        .build();

class Tools {

    static final String TOOL_METADATA = "{\"allowed_callers\": [\"code_execution_20250825\"]}";
    static final String TOOL_DESCRIPTION = """
            Returns daily minimum and maximum temperatures recorded
            for a specified city for a specified number of previous days.
            Response format: [{"min":0.0,"max":10.0},{"min":0.0,"max":20.0},{"min":0.0,"max":30.0}]
            """;

    record TemperatureRange(double min, double max) {}

    @Tool(value = TOOL_DESCRIPTION, metadata = TOOL_METADATA)
    List<TemperatureRange> getDailyTemperatures(String city, int days) {
        if ("Munich".equals(city) && days == 5) {
            return List.of(
                    new TemperatureRange(0.0, 1.0),
                    new TemperatureRange(0.0, 2.0),
                    new TemperatureRange(0.0, 3.0),
                    new TemperatureRange(0.0, 4.0),
                    new TemperatureRange(0.0, 5.0)
            );
        }

        throw new IllegalArgumentException("Unknown city: " + city + " or days: " + days);
    }

    @Tool(value = "Calculates the average of the specified list of numbers", metadata = TOOL_METADATA)
    Double average(List<Double> numbers) {
        return numbers.stream()
                .mapToDouble(Double::doubleValue)
                .average()
                .orElseThrow();
    }
}

ChatModel chatModel = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName(CLAUDE_SONNET_4_5_20250929)
        .beta("advanced-tool-use-2025-11-20")
        .serverTools(codeExecutionTool)
        .toolMetadataKeysToSend("allowed_callers") // need to specify it explicitly
        .logRequests(true)
        .logResponses(true)
        .build();

interface Assistant {

    String chat(String userMessage);
}

Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(new Tools())
        .build();

assistant.chat("What was the average max temperature in Munich in the last 5 days?");
```

查看[工具搜索工具](anthropic.md#工具搜索工具)部分，
了解在底层 `ToolSpecification` API 中指定工具 `metadata` 的示例。

### 工具使用示例

Anthropic 的[工具使用示例](https://www.anthropic.com/engineering/advanced-tool-use)
通过工具 `metadata` 和 `toolMetadataKeysToSend` 参数支持。

下面是使用高层 AI 服务和 `@Tool` API 的示例：

```java
enum Unit {
    CELSIUS, FAHRENHEIT
}

class Tools {

    // NOTE: if javac "-parameters" option is not enabled, you need to change "location" to "arg0"
    // and "unit" to "arg1" inside the TOOL_METADATA to make it work.
    public static final String TOOL_METADATA = """
            {
                "input_examples": [
                    {
                        "location": "San Francisco, CA",
                        "unit": "FAHRENHEIT"
                    },
                    {
                        "location": "Tokyo, Japan",
                        "unit": "CELSIUS"
                    },
                    {
                        "location": "New York, NY"
                    }
                ]
            }
            """;

    @Tool(metadata = TOOL_METADATA)
    String getWeather(String location, @P(description = "temperature unit", required = false) Unit unit) {
        return "sunny";
    }
}

ChatModel chatModel = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName(CLAUDE_SONNET_4_5_20250929)
        .beta("advanced-tool-use-2025-11-20")
        .toolMetadataKeysToSend("input_examples") // need to specify it explicitly
        .logRequests(true)
        .logResponses(true)
        .build();

interface Assistant {

    String chat(String userMessage);
}

Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(new Tools())
        .build();

assistant.chat("What is the weather in Munich in Fahrenheit?");
```

查看[工具搜索工具](anthropic.md#工具搜索工具)部分，
了解在底层 `ToolSpecification` API 中指定工具 `metadata` 的示例。

## 缓存

Anthropic 可以缓存提示词的开头部分（工具、系统消息以及较早的消息），使得下一个以相同内容开头的请求
从缓存中读取它，而不是重新处理。从缓存读取比重新处理相同 token 便宜且快得多，而写入缓存的成本
略高于普通输入 token。因此，当相同的提示词前缀被发送多次时缓存才有价值，多轮对话、调用工具的
AI 服务以及智能体都属于这种情况。

缓存默认禁用。使用下述选项按提示词的部分启用。Anthropic 会精确匹配缓存内容，
顺序为 工具 → 系统消息 → 消息，因此请求之间发生变化的任何内容（例如，系统消息中的当前时间或不同的
工具集合）都会阻止其后所有内容的缓存命中。短于[模型特定最小值](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
（介于 512 到 4,096 个 token 之间）的提示词不会被缓存。

该使用哪些选项：

- 当系统消息和工具在请求之间保持不变时，启用 `cacheSystemMessages` 和 `cacheTools`
  （参见[下文](#缓存系统消息和工具)）。无论何种用法，包括没有聊天记忆的独立调用，它们都能发挥作用。
- 当对话历史被保留且从一个请求到下一个请求不断增长时，此外启用 `cacheAutomatically`
  （参见[自动缓存](#自动缓存)），例如，当 AI 服务或智能体在循环中调用工具时。当对话开头在每次请求
  都变化时不要启用它，例如，当聊天记忆在每一轮都驱逐旧消息（完整的 `MessageWindowChatMemory` 或
  `TokenWindowChatMemory`）时，或没有聊天记忆的独立调用：那时它的成本比节省的更多。

Anthropic 每个请求最多允许 4 个缓存断点。`cacheSystemMessages`、`cacheTools` 和
`cacheAutomatically` 各使用一个，每个标记了 `cache_control` 属性的消息也使用一个。
断点超出的请求会被 Anthropic 拒绝。

缓存内容由 Anthropic 保存[缓存 TTL](#缓存-ttl) 的时长，并且不会与其他组织共享。
详见[提示词缓存文档](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)。

`AnthropicChatModel` 和 `AnthropicStreamingChatModel` 在响应中返回 `AnthropicTokenUsage`，
其中包含 `cacheCreationInputTokens`（写入缓存的 token）和 `cacheReadInputTokens`（从缓存读取的 token）。

关于缓存的更多信息可[在此](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)找到。

### 缓存系统消息和工具

`cacheSystemMessages` 为最后一个系统消息标记 `cache_control`，`cacheTools` 为最后一个工具标记。
由于工具在系统消息之前，系统消息断点会同时缓存这两者。工具断点还会在系统消息在请求之间变化时
保持工具处于缓存状态。

这些断点在每次请求中都处于相同位置，因此只要系统消息和工具保持不变，它们就能发挥作用，
包括没有聊天记忆的独立调用：

```java
ChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName("claude-opus-5-5")
    .cacheSystemMessages(true)
    .cacheTools(true)
    .build();
```

### 自动缓存

启用 `cacheAutomatically` 后，Anthropic 会将缓存断点放在每个请求的最后一个块上，
并随着对话增长向前移动，使得每个请求都从缓存中读取其之前发送的所有内容。
无需手动标记任何消息以便缓存，这也使其适用于[AI 服务](../../tutorials/ai-services.md)和[智能体](../../tutorials/agents.md)，
在这些场景中消息由 LangChain4j 创建。

它只有在每次请求都以上一请求发送的所有内容开头时才划算（参见[该使用哪些选项](#缓存)）。
否则，每个请求都为整个提示词支付缓存写入价格，而没有任何内容被读回，这比完全不缓存成本更高。
使用时，同时启用 `cacheSystemMessages` 和 `cacheTools`，以便即使在对话开头变化时，
系统消息和工具也保持缓存。

在下面的示例中，一次 `assistant.chat(...)` 调用内的每次工具调用都会添加到对话中，
因此同一工具循环中的后续请求会从缓存中读取较早的内容：

```java
ChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName("claude-opus-5-5")
    .cacheSystemMessages(true)
    .cacheTools(true)
    .cacheAutomatically(true)
    .build();

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .tools(new MyTools())
    .build();
```

自动缓存作为请求的顶级 `cache_control` 字段发送。不支持此字段的 Anthropic 兼容网关和代理
可能会拒绝请求或忽略该字段。在这种情况下，改为缓存系统消息、工具和[单个消息](#缓存单个消息)。

### 缓存单个消息

可以分别通过将 `cache_control` 属性设置为 `ephemeral` 来标记 `UserMessage`、`AiMessage`
和 `ToolExecutionResultMessage` 以便缓存。缓存控制标记会自动应用于消息的最后一个内容块
（对于 `ToolExecutionResultMessage`，即 `tool_result` 块本身）。

`UserMessage` 暴露了一个可变属性映射：

```java
UserMessage userMessage = UserMessage.from("Hello cached world");
userMessage.attributes().put("cache_control", "ephemeral");
```

`AiMessage` 和 `ToolExecutionResultMessage` 携带不可变属性映射，因此通过 `toBuilder()` 设置。
要缓存每一轮都在增长的对话（例如，智能体工具执行循环），[自动缓存](#自动缓存)更简单，
因为无需标记任何消息。当你需要控制缓存断点的位置时，标记单个消息是有用的。

```java
AiMessage aiMessage = someAiMessage.toBuilder()
        .attributes(Map.of("cache_control", "ephemeral"))
        .build();

ToolExecutionResultMessage toolExecutionResultMessage = someToolExecutionResultMessage.toBuilder()
        .attributes(Map.of("cache_control", "ephemeral"))
        .build();
```

### 缓存 TTL

缓存内容默认保留 5 分钟，每次缓存命中都会刷新该时间。如果共享相同提示词前缀的请求通常
间隔超过 5 分钟（例如，用户在 20 分钟后回复，或[批处理](#批处理-api)），可以将缓存保留 1 小时：

```java
ChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName("claude-opus-5-5")
    .cacheAutomatically(true)
    .cacheTtl("1h") // "5m" by default
    .build();
```

这两个值也可用作常量 `AnthropicChatRequestParameters.CACHE_TTL_5M` 和
`AnthropicChatRequestParameters.CACHE_TTL_1H`。

TTL 适用于所有缓存内容：系统消息、工具、自动缓存的消息以及标记了 `cache_control` 属性的消息。
除非其中至少一项被缓存，否则它不生效。写入 1 小时缓存的成本是基础输入 token 价格的 2 倍，
而 5 分钟缓存是 1.25 倍，因此只有当缓存内容在一小时内至少被读取几次时才有价值。

### 缓存诊断

Anthropic 的（beta）[缓存诊断](https://docs.anthropic.com/en/docs/build-with-claude/cache-diagnostics)
功能会报告提示词缓存命中*为什么*失败（模型、系统提示词、工具或消息历史发生了变化），
而不仅仅是显示 `cacheReadInputTokens` 降为零。

它需要 `cache-diagnosis-2026-04-07` beta 请求头，并通过 `returnCacheDiagnostics` 启用。
在对话的第一轮将 `previousMessageId` 传为 `null` 以选择加入，在之后的每一轮传上一轮响应的 `id`：

```java
AnthropicChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .beta("cache-diagnosis-2026-04-07")
        .returnCacheDiagnostics(true)
        .build();

ChatResponse response1 = model.chat(ChatRequest.builder()
        .messages(UserMessage.from("Summarize section 1."))
        .build());
String previousMessageId = ((AnthropicChatResponseMetadata) response1.metadata()).id();

ChatResponse response2 = model.chat(ChatRequest.builder()
        .messages(UserMessage.from("Summarize section 1."), UserMessage.from("Now summarize section 2."))
        .parameters(AnthropicChatRequestParameters.builder()
                // returnCacheDiagnostics is already enabled on the model above, so on subsequent turns
                // you only need to supply the previousMessageId (it changes every turn).
                .previousMessageId(previousMessageId)
                .build())
        .build());

AnthropicCacheDiagnostics diagnostics = ((AnthropicChatResponseMetadata) response2.metadata()).cacheDiagnostics();
if (diagnostics != null && diagnostics.cacheMissReasonType() != null) {
    // e.g. "model_changed", "system_changed", "tools_changed", "messages_changed",
    // "previous_message_not_found" or "unavailable"
    System.out.println(diagnostics.cacheMissReasonType());
}
```

当未请求诊断或未找到差异时，`cacheDiagnostics()` 为 `null`。

## 思考

`AnthropicChatModel` 和 `AnthropicStreamingChatModel` 均支持
[扩展思考](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)
和[自适应思考](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)功能。

它由以下参数控制：
- `thinkingType` 和 `thinkingBudgetTokens`：启用思考，更多详情见[此处](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)。
- `thinkingDisplay`：控制 API 是否在思考签名旁边返回可读的思考文本。有效值为
  `"summarized"`（思考块包含推理的可读摘要）和 `"omitted"`（思考块包含空的思考文本，只返回加密签名）。
  未设置时，API 会选择取决于模型的默认值：较新的 Claude 模型默认为 `"omitted"`，较旧的模型默认为
  `"summarized"`，参见[Anthropic 文档](https://platform.claude.com/docs/en/build-with-claude/thinking)。
  当需要思考文本本身时（例如，为了展示给最终用户），将其设置为 `"summarized"`。两种情况下模型
  思考和计费方式都相同；只有思考文本的可见性不同。
- `returnThinking`：控制是否（如有）将思考内容返回在 `AiMessage.thinking()` 中，以及在使用
  `AnthropicStreamingChatModel` 时是否调用 `StreamingChatResponseHandler.onPartialThinking()` 和
  `TokenStream.onPartialThinking()` 回调。默认禁用。启用后，思考签名也会存储在
  `AiMessage.attributes()` 中并返回。请注意，当 API 不返回思考文本时，`AiMessage.thinking()`
  保持为空，参见上面的 `thinkingDisplay`。
- `sendThinking`：控制是否在后续请求中将存储在 `AiMessage` 中的思考和签名发送给 LLM。默认启用。

要配置 `effort` 参数，在构建模型时设置 `customParameters`：
```java
ChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName("claude-sonnet-5")
        .customParameters(Map.of("output_config", Map.of("effort", "max")))
        ...
        .build();
```

下面是如何配置思考的示例：
```java
ChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName("claude-sonnet-4-5-20250929")
        .thinkingType("enabled")
        .thinkingBudgetTokens(1024)
        .maxTokens(1024 + 100)
        .returnThinking(true)
        .sendThinking(true)
        .build();
```

较新的 Claude 模型除非 `thinkingDisplay` 要求，否则不返回思考文本，因此未设置时
`AiMessage.thinking()` 为空：
```java
ChatModel model = AnthropicChatModel.builder()
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .modelName("claude-sonnet-5")
        .thinkingType("adaptive")
        .thinkingDisplay("summarized")
        .maxTokens(16000)
        .returnThinking(true)
        .sendThinking(true)
        .build();
```

## 对话中途的系统消息

默认情况下，无论 `SystemMessage` 出现在消息列表的哪个位置，每个 `SystemMessage` 都会被合并到
顶级 `system` 提示词中。这与 Anthropic 一直以来的工作方式一致，且未改变。

Claude Opus 4.8 额外支持[对话中途的系统消息](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)：
出现在对话开始*之后*的 `SystemMessage` 可以内联作为 `messages` 数组中的 `system` 条目发送，
从而从对话中的该点起生效（例如，在会话中途更改助手的指令）。
使用 `midConversationSystemMessages(true)` 启用此功能：

```java
AnthropicChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName("claude-opus-4-8")
    .midConversationSystemMessages(true)
    .build();

ChatResponse response = model.chat(ChatRequest.builder()
    .messages(
        SystemMessage.from("You are a helpful assistant."), // leading -> top-level "system" prompt
        UserMessage.from("Hello"),
        AiMessage.from("Hi! How can I help?"),
        SystemMessage.from("From now on, answer only in French."), // mid-conversation -> inline
        UserMessage.from("What is the capital of Spain?"))
    .build());
```

启用后，**开头的** `SystemMessage`（在第一条用户/助手消息之前的那些）仍然填充顶级 `system`
提示词；只有出现在对话开始之后的才会内联发送。这不仅仅是一种约定——Anthropic 有此要求：
`system` 消息不能是 `messages` 数组的第一个条目，而且基础系统提示词无论如何都应属于稳定的、
可缓存的前缀。禁用此选项时（默认），行为不变，所有 `SystemMessage` 都进入顶级 `system` 提示词。

也可以通过 `AnthropicChatRequestParameters` 按请求设置（参见[按请求的参数](#按请求的参数)）。

!!! note
    Anthropic 限制了对话中途系统消息可以放置的位置：它必须紧跟在一个 `user` 轮次之后（包括携带工具
    结果的 `user` 轮次），必须位于一个 `assistant` 轮次之前或结束数组，并且不能位于 `tool_use` 块与其
    `tool_result` 之间。也不允许连续出现 `system` 消息。请注意，禁用该选项时，langchain4j 会将多个
    `SystemMessage` 合并到顶级 `system` 字段；启用该选项时，两个相邻的对话中途 `SystemMessage` 会作为
    连续的内联 `system` 条目发送并被拒绝。langchain4j 不会重新排序或合并内联消息——它会按你提供的
    位置发送——因此不受支持的模型或无效的位置会导致 Anthropic API 返回 `400`。

## PDF 支持

Anthropic Claude 支持处理 PDF 文档。你可以通过 URL 或 base64 编码的数据发送 PDF。

### 通过 URL 发送 PDF
```java
UserMessage message = UserMessage.from(
    PdfFileContent.from(URI.create("https://example.com/document.pdf")),
    TextContent.from("What are the key findings in this document?")
);

ChatResponse response = model.chat(message);
```

### 通过 Base64 发送 PDF
```java
String base64Data = Base64.getEncoder().encodeToString(Files.readAllBytes(Path.of("document.pdf")));

UserMessage message = UserMessage.from(
    PdfFileContent.from(base64Data, "application/pdf"),
    TextContent.from("Summarize this document.")
);

ChatResponse response = model.chat(message);
```

关于 PDF 支持的更多信息可[在此](https://docs.anthropic.com/en/docs/build-with-claude/pdf-support)找到。

## 设置自定义聊天请求参数

在构建 `AnthropicChatModel` 和 `AnthropicStreamingChatModel` 时，你可以在 HTTP 请求的 JSON 主体中
为聊天请求配置自定义参数。下面是如何启用[上下文编辑](https://docs.claude.com/en/docs/build-with-claude/context-editing)的示例：
```java
record Edit(String type) {}
record ContextManagement(List<Edit> edits) { }
Map<String, Object> customParameters = Map.of("context_management", new ContextManagement(List.of(new Edit("clear_tool_uses_20250919"))));

ChatModel model = AnthropicChatModel.builder()
    .apiKey(System.getenv("ANTHROPIC_API_KEY"))
    .modelName(CLAUDE_SONNET_4_5_20250929)
    .beta("context-management-2025-06-27")
    .customParameters(customParameters)
    .logRequests(true)
    .logResponses(true)
    .build();

String answer = model.chat("Hi");
```

这将产生一个具有以下主体的 HTTP 请求：
```json
{
    "model" : "claude-sonnet-4-5-20250929",
    "messages" : [ {
        "role" : "user",
        "content" : [ {
            "type" : "text",
            "text" : "Hi"
        } ]
    } ],
    "context_management" : {
        "edits" : [ {
            "type" : "clear_tool_uses_20250919"
        } ]
    }
}
```

或者，自定义参数也可以指定为嵌套映射的结构：
```java
Map<String, Object> customParameters = Map.of(
        "context_management",
        Map.of("edits", List.of(Map.of("type", "clear_tool_uses_20250919")))
);
```

## 访问原始 HTTP 响应和服务器发送事件（SSE）

使用 `AnthropicChatModel` 时，你可以访问原始 HTTP 响应：
```java
SuccessfulHttpResponse rawHttpResponse = ((AnthropicChatResponseMetadata) chatResponse.metadata()).rawHttpResponse();
System.out.println(rawHttpResponse.body());
System.out.println(rawHttpResponse.headers());
System.out.println(rawHttpResponse.statusCode());
```

使用 `AnthropicStreamingChatModel` 时，你可以访问原始 HTTP 响应（参见上文）和原始服务器发送事件（SSE）：
```java
List<ServerSentEvent> rawServerSentEvents = ((AnthropicChatResponseMetadata) chatResponse.metadata()).rawServerSentEvents();
System.out.println(rawServerSentEvents.get(0).data());
System.out.println(rawServerSentEvents.get(0).event());
```

## AnthropicTokenCountEstimator

```java
TokenCountEstimator tokenCountEstimator = AnthropicTokenCountEstimator.builder()
        .modelName(CLAUDE_3_OPUS_20240229)
        .apiKey(System.getenv("ANTHROPIC_API_KEY"))
        .logRequests(true)
        .logResponses(true)
        .build();

List<ChatMessage> messages = List.of(...);

int tokenCount = tokenCountEstimator.estimateTokenCountInMessages(messages);
```

## Quarkus

更多详情见[此处](https://docs.quarkiverse.io/quarkus-langchain4j/dev/anthropic.html)。

## Spring Boot

导入 Anthropic 的 Spring Boot starter：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-anthropic-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

!!! note
    此 starter 要求 **Spring Boot 4**。在 **Spring Boot 3** 上，请改用
    `langchain4j-anthropic-spring-boot-starter`。详情请参见
    [Spring Boot 集成](../../tutorials/spring-boot-integration.md#支持的版本)。

配置 `AnthropicChatModel` Bean：
```
langchain4j.anthropic.chat-model.api-key = ${ANTHROPIC_API_KEY}
```

配置 `AnthropicStreamingChatModel` Bean：
```
langchain4j.anthropic.streaming-chat-model.api-key = ${ANTHROPIC_API_KEY}
```

## 示例

- [AnthropicChatModelTest](https://github.com/langchain4j/langchain4j-examples/blob/main/anthropic-examples/src/main/java/AnthropicChatModelTest.java)
- [AnthropicStreamingChatModelTest](https://github.com/langchain4j/langchain4j-examples/blob/main/anthropic-examples/src/main/java/AnthropicStreamingChatModelTest.java)
- [AnthropicToolsTest](https://github.com/langchain4j/langchain4j-examples/blob/main/anthropic-examples/src/main/java/AnthropicToolsTest.java)
- [AnthropicPdfExample](https://github.com/langchain4j/langchain4j-examples/blob/main/anthropic-examples/src/main/java/AnthropicPdfExample.java)
