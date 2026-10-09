# 聊天模型与语言模型

!!! note
    本页面介绍底层 LLM API。
    高层级 LLM API 请参阅 [AI 服务](ai-services.md)。

!!! note
    所有受支持的 LLM 见[这里](../integrations/language-models/index.md)。

LLM 目前有两种 API 类型：
- `LanguageModel`。其 API 非常简单——接受 `String` 作为输入，返回 `String` 作为输出。
该 API 正逐渐过时，取而代之的是聊天 API（第二种 API 类型）。
- `ChatModel`。这些接受多个 `ChatMessage` 作为输入，并返回单个 `AiMessage` 作为输出。
`ChatMessage` 通常包含文本，但一些 LLM 还支持其他模态（例如图像、音频等）。
此类聊天模型的例子包括 OpenAI 的 `gpt-4o-mini` 和 Google 的 `gemini-1.5-pro`。

LangChain4j 将不再扩展对 `LanguageModel` 的支持，
因此在所有新功能中，我们将使用 `ChatModel` API。

`ChatModel` 是 LangChain4j 中与 LLM 交互的底层 API，提供最强大的功能和灵活性。
还有一个高层级 API（[AI 服务](ai-services.md)），我们将在讲完基础知识之后再介绍。

除了 `ChatModel` 和 `LanguageModel`，LangChain4j 还支持以下类型的模型：
- `EmbeddingModel` - 该模型可将文本转换为 `Embedding`。
- `ImageModel` - 该模型可以生成和编辑 `Image`。
- `ModerationModel` - 该模型可以检查文本是否包含有害内容。
- `ScoringModel` - 该模型可以针对查询对多段文本进行评分（或排序），
实质上就是判断每段文本与查询的相关程度。这对 [RAG](rag.md) 非常有用。
这些将在后面介绍。

现在，让我们更详细地看看 `ChatModel` API。

```java
public interface ChatModel {

    String chat(String userMessage);
    
    ...
}
```
如你所见，有一个简单的 `chat` 方法，接受 `String` 作为输入并返回 `String` 作为输出，与 `LanguageModel` 类似。
这只是一个便捷方法，让你可以快速地实验，而无需将 `String` 包装为 `UserMessage`。

以下是其他聊天 API 方法：
```java
    ...
    
    ChatResponse chat(ChatMessage... messages);

    ChatResponse chat(List<ChatMessage> messages);
        
    ...
```

这些版本的 `chat` 方法接受一个或多个 `ChatMessage` 作为输入。
`ChatMessage` 是表示聊天消息的基础接口。
下一节将详细介绍聊天消息。

如果你希望自定义请求（例如指定模型名称、温度、工具、JSON schema 等），
可以使用 `chat(ChatRequest)` 方法：
```java
    ...
    
    ChatResponse chat(ChatRequest chatRequest);
        
    ...
```

```java
ChatRequest chatRequest = ChatRequest.builder()
    .messages(...)
    .modelName(...)
    .temperature(...)
    .topP(...)
    .topK(...)
    .frequencyPenalty(...)
    .presencePenalty(...)
    .maxOutputTokens(...)
    .stopSequences(...)
    .toolSpecifications(...)
    .toolChoice(...)
    .responseFormat(...)
    .parameters(...) // you can also set common or provider-specific parameters all at once
    .build();

ChatResponse chatResponse = chatModel.chat(chatRequest);
```

### `ChatMessage` 的类型
目前有五种聊天消息类型，消息的每种"来源"对应一种：

- `UserMessage`：这是来自用户的消息。
  用户可以是你的应用的最终用户（人类），也可以是你的应用本身。
  它可以包含：
    - `contents()`：消息的内容。根据 LLM 支持的模态，
      它可能只包含单个文本（`(String)`），
      或 [其他模态](chat-and-language-models.md#多模态)。
    - `name()`：用户的名称。并非所有模型提供商都支持。
    - `attributes()`：附加属性：这些属性不会发送给模型，
      但会存储在 [`ChatMemory`](chat-memory.md) 中。
- `AiMessage`：这是由 AI 生成、作为对所发送消息的回复的消息。
  它可以包含：
    - `text()`：文本内容
    - `thinking()`：思考/推理内容
    - `toolExecutionRequests()`：执行工具的请求。我们将在
      [另一节](tools.md)中探讨工具。
    - `attributes()`：附加属性，通常是提供商专属的
- `ToolExecutionResultMessage`：这是 `ToolExecutionRequest` 的结果。
- `SystemMessage`：这是来自系统的消息。
通常，作为开发者，你应定义此消息的内容。
你通常会在这里写明 LLM 在这次对话中的角色、它应如何表现、以什么风格作答等指令。
LLM 经过训练，对 `SystemMessage` 的关注度高于其他类型的消息，
所以务必小心，最好不要让最终用户自由地定义或向 `SystemMessage` 中注入输入。
它通常位于对话的开头。
它可以包含：
    - `text()`：消息文本。
    - `attributes()`：附加属性：这些属性不会发送给模型，
      但会存储在 [`ChatMemory`](chat-memory.md) 中。
- `CustomMessage`：这是一种可以包含任意属性的自定义消息。该消息类型只能由
`ChatModel` 实现中支持它的实现使用（目前仅 Ollama）。

现在我们已经了解了 `ChatMessage` 的所有类型，让我们看看如何把它们组合到对话中。

在最简单的场景中，我们可以向 `chat` 方法提供一个 `UserMessage` 实例。
这与接受 `String` 作为输入的 `chat` 方法的第一个版本类似。
这里的主要区别是，它现在返回的不是 `String`，而是 `ChatResponse`。
除了 `AiMessage` 之外，`ChatResponse` 还包含 `ChatResponseMetadata`。
`ChatResponseMetadata` 包含 `TokenUsage`，其中包含关于输入中包含多少 token
（你提供给 generate 方法的所有 `ChatMessage`）、输出生成了多少 token（在 `AiMessage` 中）
以及总数（输入 + 输出）的统计信息。
你将需要这些信息来计算某次对 LLM 的调用成本是多少。
然后，`ChatResponseMetadata` 还包含 `FinishReason`，
它是一个枚举，表示生成停止的各种原因。
通常，如果 LLM 自行决定停止生成，它会是 `FinishReason.STOP`。

根据内容不同，创建 `UserMessage` 有多种方式。
最简单的方式是 `new UserMessage("Hi")` 或 `UserMessage.from("Hi")`。

### 多个 `ChatMessage`
现在，为什么你需要提供多个 `ChatMessage` 作为输入，而不是只有一个？
这是因为 LLM 天生是无状态的，也就是说它们不维护对话的状态。
因此，如果你想支持多轮对话，就需要自行管理对话的状态。

假设你想构建一个聊天机器人。想象用户与聊天机器人（AI）之间的一段简单多轮对话：
- 用户：你好，我叫 Klaus
- AI：你好 Klaus，有什么可以帮你？
- 用户：我叫什么名字？
- AI：Klaus

与 `ChatModel` 的交互将是这样的：
```java
UserMessage firstUserMessage = UserMessage.from("Hello, my name is Klaus");
AiMessage firstAiMessage = model.chat(firstUserMessage).aiMessage(); // Hi Klaus, how can I help you?
UserMessage secondUserMessage = UserMessage.from("What is my name?");
AiMessage secondAiMessage = model.chat(firstUserMessage, firstAiMessage, secondUserMessage).aiMessage(); // Klaus
```
如你所见，在 `chat` 方法的第二次调用中，我们提供的不仅是一个单独的 `secondUserMessage`，
还有对话中之前的消息。

手动维护和管理这些消息会很繁琐。
因此，`ChatMemory` 这一概念应运而生，我们将在[下一节](chat-memory.md)中对其进行探讨。

### 多模态

`UserMessage` 不仅可以包含文本，还可以包含其他类型的内容。
`UserMessage` 包含一个 `List<Content> contents`。
`Content` 是一个接口，具有以下实现：
- `TextContent`
- `ImageContent`
- `AudioContent`
- `VideoContent`
- `PdfFileContent`

你可以在[这里](../integrations/language-models/index.md)的对比表格中查看哪些 LLM 提供商支持哪些模态。

下面是一个向 LLM 同时发送文本和图像的例子：
```java
UserMessage userMessage = UserMessage.from(
    TextContent.from("Describe the following image"),
    ImageContent.from("https://example.com/cat.jpg")
);
ChatResponse response = model.chat(userMessage);
```

#### 文本内容
`TextContent` 是 `Content` 最简单的形式，表示纯文本，包装单个 `String`。
`UserMessage.from(TextContent.from("Hello!"))` 等价于 `UserMessage.from("Hello!")`。

可以在 `UserMessage` 中提供一个或多个 `TextContent`：
```java
UserMessage userMessage = UserMessage.from(
    TextContent.from("Hello!"),
    TextContent.from("How are you?")
);
```

#### 图像内容
根据 LLM 提供商的不同，`ImageContent` 可以从 **远程** 图像的 URL 创建（见上面的例子），
也可以从 Base64 编码的二进制数据创建：
```java
byte[] imageBytes = readBytes("/home/me/cat.jpg");
String base64Data = Base64.getEncoder().encodeToString(imageBytes);
ImageContent imageContent = ImageContent.from(base64Data, "image/jpg");
UserMessage userMessage = UserMessage.from(imageContent);
```

还可以指定 `DetailLevel` 枚举（有 `LOW`/`HIGH`/`AUTO` 选项）来控制模型处理图像的方式。
更多详情见[这里](https://platform.openai.com/docs/guides/vision#low-or-high-fidelity-image-understanding)。

#### 音频内容
`AudioContent` 与 `ImageContent` 类似，但表示音频内容。

#### 视频内容
`VideoContent` 与 `ImageContent` 类似，但表示视频内容。

#### PDF 文件内容
`PdfFileContent` 与 `ImageContent` 类似，但表示 PDF 文件的二进制内容。

### 非阻塞调用

!!! note
    实验性功能。该 API 标注了 `@Experimental`，可能在未来的版本中发生变化。

`ChatModel` 也可以在不阻塞调用线程的情况下作答：

```java
CompletableFuture<ChatResponse> future = model.chatAsync(chatRequest);
```

与 `chat(...)` 一样，它也有相同的便捷重载，例如
`CompletableFuture<String> chatAsync(String userMessage)`。

取消 future 会释放调用方，并尽力中止正在进行的 HTTP 调用。
future 在模型的传输线程上完成，因此未显式指定执行器而附加的后续操作
会在线程上运行——请保持非阻塞，或使用 `thenApplyAsync(fn, executor)`。

未实现非阻塞路径的提供商会以返回的 future 所携带的 `AsyncNotSupportedException` 显式失败，
而不是悄悄地阻塞一个线程。

要了解全貌（包括流式和 AI 服务），请参阅 [Non-blocking and Reactive](non-blocking.md)。

### Kotlin 扩展

!!! warning
    **Kotlin 用户的破坏性变更。** `ChatModel` 现在声明了一个 Java 成员
    `chatAsync(ChatRequest): CompletableFuture<ChatResponse>`。在 Kotlin 中，同签名的成员优先于
    扩展，因此一个裸的单参数调用——之前解析为 `suspend` 扩展（返回
    `ChatResponse`）——现在解析为成员（返回 `CompletableFuture<ChatResponse>`）：

    ```kotlin
    // Before - resolved to the suspend extension, returned ChatResponse:
    val response: ChatResponse = model.chatAsync(request)

    // After - the bare single-arg call resolves to the Java member (a CompletableFuture):
    val future: CompletableFuture<ChatResponse> = model.chatAsync(request)

    // Migration - await the future...
    val response: ChatResponse = model.chatAsync(request).await()
    // ...or supply a coroutineContext, which still selects the suspend extension:
    val response: ChatResponse = model.chatAsync(request, Dispatchers.IO)
    ```

`ChatModel` 的 [Kotlin 扩展](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-kotlin/src/main/kotlin/dev/langchain4j/kotlin/model/chat/ChatModelExtensions.kt) 提供了异步方法，用于处理与语言模型的聊天交互，利用了 Kotlin 的 [协程](https://kotlinlang.org/docs/coroutines-guide.html) 能力。`chatAsync` 方法允许非阻塞地处理 `ChatRequest` 或 `ChatRequest.Builder` 配置，返回包含模型回复的 `ChatResponse`。类似地，`generateAsync` 负责从聊天消息异步生成响应。这些扩展简化了在 Kotlin 应用中高效构建聊天请求和处理对话。注意，这些方法被标记为实验性的，未来可能会演进。

**`ChatModel.chatAsync(request: ChatRequest)`**：专为 Kotlin 协程设计，此*异步*扩展函数使用 `Dispatchers.IO` 将同步的 `chat` 方法包装在协程作用域内。这实现了非阻塞操作，对于保持应用响应性至关重要。它特意命名为 `chatAsync`，以避免与现有的同步 `chat` 冲突。其函数签名是：`suspend fun ChatModel.chatAsync(request: ChatRequest): ChatResponse`。关键字 `suspend` 将其指定为协程函数。

**`ChatModel.chat(block: ChatRequestBuilder.() -> Unit)`**：此 `chat` 变体通过使用 Kotlin 的类型安全构建器 DSL，提供了更简洁的方式。它在内部使用 `chatAsync` 进行异步执行的同时，简化了 `ChatRequest` 对象的构建。这个版本通过协程同时提供了简洁性和非阻塞行为。
