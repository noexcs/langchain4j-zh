# 响应流式传输

!!! note
    本页描述的是使用底层 LLM API 的响应流式传输。
    高级 LLM API 请参阅 [AI 服务](ai-services.md#流式)。

LLM 逐个 token 生成文本，因此许多 LLM 提供商提供了一种逐 token 流式传输响应
的方法，而不是等待整个文本生成完毕。
这显著改善了用户体验，因为用户无需等待未知的时间
即可几乎立即开始阅读响应。

对于 `ChatModel` 和 `LanguageModel` 接口，有对应的
`StreamingChatModel` 和 `StreamingLanguageModel` 接口。
它们具有类似的 API，但可以流式传输响应。
它们接受 `StreamingChatResponseHandler` 接口的一个实现作为参数。

```java
public interface StreamingChatResponseHandler {

    default void onPartialResponse(String partialResponse) {}
    default void onPartialResponse(PartialResponse partialResponse, PartialResponseContext context) {}

    default void onPartialThinking(PartialThinking partialThinking) {}
    default void onPartialThinking(PartialThinking partialThinking, PartialThinkingContext context) {}

    default void onPartialToolCall(PartialToolCall partialToolCall) {}
    default void onPartialToolCall(PartialToolCall partialToolCall, PartialToolCallContext context) {}

    default void onCompleteToolCall(CompleteToolCall completeToolCall) {}

    default void onUnmappedRawEvent(Object rawEvent) {}

    void onCompleteResponse(ChatResponse completeResponse);

    void onError(Throwable error);
}
```

通过实现 `StreamingChatResponseHandler`，你可以为以下事件定义动作：
- 当生成下一个部分文本响应时：调用 `onPartialResponse(String)`
或 `onPartialResponse(PartialResponse, PartialResponseContext)`（你可以实现其中任何一个方法）。
根据 LLM 提供商的不同，部分响应文本可能由一个或多个 token 组成。
例如，一旦 token 可用，你就可以直接将其发送到 UI。
- 当生成下一个部分思考/推理文本时：调用 `onPartialThinking(PartialThinking)`
或 `onPartialThinking(PartialThinking, PartialThinkingContext)`（你可以实现其中任何一个方法）。
根据 LLM 提供商的不同，部分思考文本可能由一个或多个 token 组成。
- 当生成下一个[部分工具调用](tools.md#使用-streamingchatmodel)时：调用 `onPartialToolCall(PartialToolCall)`
或 `onPartialToolCall(PartialToolCall, PartialToolCallContext)`（你可以实现其中任何一个方法）。
- 当 LLM 完成单个工具调用的流式传输时：调用 `onCompleteToolCall(CompleteToolCall)`。
- 当提供商发出尚未通过上述类型化回调之一暴露的原始流式事件时：
调用 `onUnmappedRawEvent(Object)`。参见下面的 [未映射的原始事件](#未映射的原始事件)。
- 当 LLM 完成生成时：调用 `onCompleteResponse(ChatResponse)`。
`ChatResponse` 对象包含完整的响应（`AiMessage`）以及 `ChatResponseMetadata`。
- 当发生错误时：调用 `onError(Throwable error)`。

下面是如何使用 `StreamingChatModel` 实现流式传输的示例：
```java
StreamingChatModel model = OpenAiStreamingChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName(GPT_4_O_MINI)
    .build();

String userMessage = "Tell me a joke";

model.chat(userMessage, new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.println("onPartialResponse: " + partialResponse);
    }

    @Override
    public void onPartialThinking(PartialThinking partialThinking) {
        System.out.println("onPartialThinking: " + partialThinking);
    }

    @Override
    public void onPartialToolCall(PartialToolCall partialToolCall) {
        System.out.println("onPartialToolCall: " + partialToolCall);
    }

    @Override
    public void onCompleteToolCall(CompleteToolCall completeToolCall) {
        System.out.println("onCompleteToolCall: " + completeToolCall);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        System.out.println("onCompleteResponse: " + completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

一种更紧凑的流式传输响应方式是使用 `LambdaStreamingResponseHandler` 类。
这个工具类提供了静态方法，使用 lambda 表达式创建 `StreamingChatResponseHandler`。
使用 lambda 流式传输响应的方式非常简单。
你只需调用 `onPartialResponse()` 静态方法，并传入一个定义如何处理部分响应的 lambda 表达式：

```java
import static dev.langchain4j.model.LambdaStreamingResponseHandler.onPartialResponse;

model.chat("Tell me a joke", onPartialResponse(System.out::print));
```

`onPartialResponseAndError()` 方法允许你同时为
`onPartialResponse()` 和 `onError()` 事件定义动作：

```java
import static dev.langchain4j.model.LambdaStreamingResponseHandler.onPartialResponseAndError;

model.chat("Tell me a joke", onPartialResponseAndError(System.out::print, Throwable::printStackTrace));
```

## 响应式 API

!!! note
    实验性功能。该 API 带有 `@Experimental` 注解，可能会在未来的版本中变更。

除了上述基于处理器的 API 之外，`StreamingChatModel` 还可以以
事件 `Flow.Publisher` 的形式将相同的响应交给你，而不会阻塞调用线程：

```java
Flow.Publisher<ChatModelStreamingEvent> publisher = model.chat(chatRequest);
```

流会在事件到达时发出 `PartialThinking`、`PartialResponse`、`PartialToolCall` 和 `CompleteToolCall` 事件，
其间穿插任何 `RawStreamingEvent`（参见下面的 [未映射的原始事件](#未映射的原始事件)），然后是
一个携带组装好的 `ChatResponse` 的终端 `CompleteResponse`。一个便捷的
重载方法只发出文本：

```java
Flow.Publisher<String> textOnly = model.chat("Tell me a joke");
```

该 publisher 是**冷（cold）**的：在你订阅之前什么都不会发生，并且每次订阅都会发送一个新请求。
取消订阅会尽力中止进行中的 HTTP 调用。

随着时间推移可能会添加新的事件类型，因此请优雅地处理无法识别的事件，而不是编写没有 default 分支的穷举
类型 switch。

!!! note
    事件在模型自己的线程上交付——对于 HTTP 模型，就是读取响应的传输 I/O 工作线程。
    不要在 `onNext` 中阻塞或执行繁重的工作：它会停滞流，并在并发下降低
    每个进行中调用的吞吐量。将此类工作卸载到你自己的执行器。

    LLM 响应无法有意义地被限流，因此实现会急切地消费它，并通过
    有界缓冲区转发事件，而不是把你的 demand 传播给模型。请大方地请求
    （例如 `Long.MAX_VALUE`）；请求更少的订阅者可能会耗尽缓冲区并以错误终止。

AI 服务级别的等效功能——它还会暴露工具执行和 RAG 内容——请参阅
[非阻塞与响应式](non-blocking.md)。

## 未映射的原始事件

!!! note
    这是一个面向高级使用场景的实验性功能。该 API 可能会在未来变更。

大多数应用只需要上面描述的类型化回调。然而，一些 LLM 提供商会发出
LangChain4j 尚未映射到专门回调的附加流式事件——例如，
OpenAI 服务器端工具（如 `web_search`）的生命周期事件
（`response.web_search_call.in_progress`、`response.web_search_call.searching`、
`response.web_search_call.completed`）。

`onUnmappedRawEvent(Object rawEvent)` 回调让你可以访问此类事件。它
**仅**在事件**没有**已经通过类型化回调
（`onPartialResponse`、`onPartialThinking`、`onPartialToolCall`、`onCompleteToolCall`、`onCompleteResponse`）暴露时才会被调用。
换句话说，部分响应、思考和工具调用**不会**作为未映射的原始事件重复，
因此你可以同时消费两者而不会重复。

`rawEvent` 的具体类型取决于提供商的实现：

| 提供商 | 原始事件类型 |
|----------|----------------|
| OpenAI、Anthropic、Google AI Gemini、Mistral、Ollama | `dev.langchain4j.http.client.sse.ServerSentEvent` |
| OpenAI（官方）- Responses API | `com.openai.models.responses.ResponseStreamEvent` |
| OpenAI（官方）- Chat Completions API | `com.openai.models.chat.completions.ChatCompletionChunk` |
| Amazon Bedrock | `software.amazon.awssdk.services.bedrockruntime.model.ConverseStreamOutput` |
| Google GenAI | `com.google.genai.types.GenerateContentResponse` |

由于事件类型是提供商特定的，你通常使用 `instanceof` 检查并强制类型转换：
```java
model.chat(userMessage, new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.println("onPartialResponse: " + partialResponse);
    }

    @Override
    public void onUnmappedRawEvent(Object rawEvent) {
        if (rawEvent instanceof ServerSentEvent sse) {
            System.out.println("Raw SSE event: " + sse.event() + " -> " + sse.data());
        }
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        System.out.println("onCompleteResponse: " + completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

使用 [AI 服务](ai-services.md#流式) 时，相同的事件可通过
`TokenStream.onUnmappedRawEvent(Consumer<Object>)` 回调获得。

## 流式取消

如果你希望取消流式传输，可以从以下方法之一进行：
- `onPartialResponse(PartialResponse, PartialResponseContext)`
- `onPartialThinking(PartialThinking, PartialThinkingContext)`
- `onPartialToolCall(PartialToolCall, PartialToolCallContext)`

上下文对象包含 `StreamingHandle`，可用于取消流式传输：
```java
model.chat(userMessage, new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(PartialResponse partialResponse, PartialResponseContext context) {
        process(partialResponse);
        if (shouldCancel()) {
            context.streamingHandle().cancel();
        }
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        System.out.println("onCompleteResponse: " + completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

当调用 `StreamingHandle.cancel()` 时，LangChain4j 将关闭连接并停止流式传输。
一旦调用了 `StreamingHandle.cancel()`，`StreamingChatResponseHandler` 将不会收到任何进一步的回调。
