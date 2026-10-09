# 非阻塞与响应式

!!! note
    异步和响应式支持目前处于实验阶段。本页中的异步和响应式 API 均标注了 `@Experimental`；API 和行为在未来的版本中仍可能变更。同步 API 和 `TokenStream` API 不受影响。

默认情况下，调用 AI 服务会阻塞调用线程直到整个交互完成：LLM 调用、工具执行、聊天记忆访问和护栏都在方法返回之前发生。这种方式简单，对大多数应用来说效果很好。

如果你构建在响应式技术栈之上（Quarkus/Mutiny、Vert.x、Spring WebFlux），或者需要用一个线程驱动许多并发交互，LangChain4j 可以在不阻塞的情况下运行同样的交互。你只需在 AI 服务方法上声明不同的**返回类型**——接口的其他一切都不变。

## 四种模式

| 返回类型 | 性质 |
|---|---|
| `String`、POJO、`Result<T>`、… | 同步，阻塞调用线程 |
| `TokenStream` | 通过回调流式传输 |
| `CompletableFuture<T>`、`CompletionStage<T>` | 单次响应，非阻塞 |
| `Flow.Publisher<AiServiceStreamingEvent>`、`Flow.Publisher<String>` | 事件流，非阻塞 |

```java
interface Assistant {

    // synchronous
    String chat(String message);

    // one response, without blocking the caller
    CompletableFuture<String> chatAsync(String message);

    // the answer, streamed token by token
    Flow.Publisher<String> chatStreaming(String message);

    // everything that happens during the interaction, as events
    Flow.Publisher<AiServiceStreamingEvent> chatEvents(String message);
}
```

## 非阻塞获取单次响应

```java
CompletableFuture<String> future = assistant.chatAsync("Tell me a joke");

future.thenAccept(System.out::println);
```

取消该 future（`future.cancel(true)`）会释放调用方，停止后续的 LLM 轮次，并尽力中止正在进行的 HTTP 调用。

!!! note
    该 future 在模型自己的线程上完成——对 HTTP 模型而言，就是读取响应的传输层 I/O 工作线程。因此，未显式指定执行器的续接（`thenApply`、`thenAccept`、…）都会在该线程上运行，其中的阻塞操作会降低所有在途调用的吞吐量。请保持续接非阻塞，或者传入你自己的 `Executor`：`future.thenApplyAsync(fn, executor)`。

## 流式输出答案

返回 `Flow.Publisher<String>` 的方法会分块流式输出答案文本：

```java
Flow.Publisher<String> publisher = assistant.chatStreaming("Tell me a joke");
```

该 publisher 是**冷的**：在你订阅之前什么都不会发生，而且每次订阅都会启动一个新的交互。

## 流式输出全部事件

`Flow.Publisher<AiServiceStreamingEvent>` 会呈现整个交互过程，而不仅仅是答案文本——与基于回调的 `TokenStream` 提供的信息相同：

| 事件 | 含义 |
|---|---|
| `PartialResponseEvent` | 答案的一个片段 |
| `PartialThinkingEvent` | 模型推理的一个片段 |
| `PartialToolCallEvent`、`CompleteToolCallEvent` | 工具调用正在组装，随后完成 |
| `BeforeToolExecutionEvent`、`AfterToolExecutionEvent` | 即将运行的工具，以及其执行结果 |
| `IntermediateResponseEvent` | 结束某一轮工具调用的响应 |
| `RetrievedContentsEvent` | 由 RAG 检索到的内容 |
| `ToolCompensatedEvent` | 交互被取消或失败后，已完成的工具被补偿 |
| `RawEvent` | LangChain4j 未映射的提供商特定事件 |
| `FinalResponseEvent` | 最终答案 |

```java
assistant.chatEvents("What is the weather in Munich?").subscribe(new Flow.Subscriber<>() {

    @Override
    public void onSubscribe(Flow.Subscription subscription) {
        subscription.request(Long.MAX_VALUE);
    }

    @Override
    public void onNext(AiServiceStreamingEvent event) {
        // the event types are nested in AiServiceStreamingEvent:
        // import dev.langchain4j.service.AiServiceStreamingEvent.PartialResponseEvent;
        if (event instanceof PartialResponseEvent partial) {
            System.out.print(partial.partialResponse().text());
        }
    }

    @Override
    public void onError(Throwable error) { }

    @Override
    public void onComplete() { }
});
```

随着时间推移可能会新增事件类型，因此要优雅地处理未识别的事件——不要编写没有 default 分支的穷举类型 switch。

!!! note
    不要在 `onNext` 中阻塞。事件在其产生线程上交付：token 级事件在模型的传输 I/O 工作线程上，工具执行事件在完成该工具调用的线程上。请将每个事件的重型工作转移到你自己的 `Executor`。事件通过有界缓冲区中继，因此落后太多的订阅者会抛出 `IllegalStateException` 终止，而不是无限制地缓冲；缓冲区大小默认为 16384 个事件，可通过 `AiServices.builder(...).streamingBufferSize(int)` 配置。

## 第三方响应式类型

AI 服务方法返回的是 JDK 类型——`CompletableFuture` 和 `Flow.Publisher`——因此该 API 不会把你绑定到任何特定的响应式编程库。

Reactor 类型通过 `langchain4j-reactor` 模块支持——单次响应模式使用 `Mono<T>`，响应式模式使用 `Flux<AiServiceStreamingEvent>`。添加依赖即可；适配器会通过 `ServiceLoader` 自行注册。

```java
interface Assistant {

    Mono<String> answer(String userMessage);

    Flux<AiServiceStreamingEvent> events(String userMessage);
}
```

!!! note
    Mutiny 的 `Uni`/`Multi` 目前尚不支持。接缝已经就位——通过 `ServiceLoader` 发现的 `CompletableFutureAdapter` 和 `PublisherAdapter` SPI——但尚未为它们提供适配器，因此声明这样的返回类型目前会失败。请使用 `CompletableFuture` 或 `Flow.Publisher`，并在调用点自行适配。

`Flux<String>` 由同一模块中较旧的基于 `TokenStream` 的适配器提供——参见 [AI 服务](ai-services.md#flux)。它早于本功能存在，不属于此处描述的非阻塞路径，并且支持所有提供商。

## 必须非阻塞的环节

非阻塞必须在每一层成立：任何位置的阻塞步骤都会使整个调用重新变回阻塞。每一层在其现有的阻塞方法旁边都有一个异步对应方法：

| 层 | 阻塞 | 非阻塞对应方法 |
|---|---|---|
| 聊天模型 | `chat(ChatRequest)` | `chatAsync(ChatRequest)`，以及 `StreamingChatModel` 上返回 `Publisher` 的 `chat(ChatRequest)` |
| 嵌入模型 | `embed(...)` | `embedAsync(...)` |
| 评分模型 | `scoreAll(...)` | `scoreAsync(...)` |
| 聊天记忆 | `add`、`messages`、`set` | `addAsync`、`messagesAsync`、`setAsync` |
| 聊天记忆存储 | `getMessages`、`updateMessages`、`deleteMessages` | `getMessagesAsync`、`updateMessagesAsync`、`deleteMessagesAsync` |
| 护栏 | `validate(...)` | `validateAsync(...)` |
| 工具 | `ToolExecutor.execute(...)` | `ToolExecutor.executeAsync(...)` |
| RAG | `RetrievalAugmentor.augment(...)`、检索器、路由器、聚合器、查询转换器 | `augmentAsync(...)`、`retrieveAsync(...)`、`routeAsync(...)`、`aggregateAsync(...)`、`transformAsync(...)` |
| 向量存储 | `search(...)` | `searchAsync(...)` |
| 网页搜索 | `search(...)` | `searchAsync(...)` |
| MCP | `McpClient.executeTool(...)` | `executeToolAsync(...)` |
| 护栏执行 | `ChatExecutor.execute(...)` | `ChatExecutor.executeAsync(...)` |
| HTTP 客户端 | `execute(...)` | `executeAsync(...)`、`stream(...)` |

未实现对应方法的组件会**大声失败**，而不是静默阻塞：返回的 future 或 publisher 会以 `AsyncNotSupportedException` 失败，其中指明了组件和缺失的方法。`AsyncNotSupportedException` 是一种 `UnsupportedFeatureException`，因此一个 catch 子句即可覆盖两种“不支持”，并且它永远不会被重试。

## 无法避免的阻塞代码

工具是最常见的情况：调用数据库或阻塞式 HTTP API 的工具无法改为非阻塞。这类工具会被转移执行，以免阻塞模型自己的线程。

!!! note
    在 Java 21 及更高版本上，转移执行器会创建虚拟线程，因此阻塞工具使的是一个*虚拟*线程进入等待，该线程会从其载体线程卸载，而不是占用它。LangChain4j 的目标是 Java 17，在 Java 17-20 上，同一个执行器是**无界的平台线程池**——负载下的资源画像完全不同。如果这对你很重要，请提供你自己的有界 `Executor`（见下文）。

这适用于用 `@Tool` 注解的方法。未重写 `executeAsync` 的手写 `ToolExecutor` 会像其他任何未选择加入的组件一样，以 `AsyncNotSupportedException` 大声失败。

在异步和响应式模式下，工具默认**并发**运行。若要一次只运行一个工具，请传入单线程执行器：

```java
AiServices.builder(Assistant.class)
        .chatModel(model)
        .tools(new MyTools())
        .executeToolsConcurrently(Executors.newSingleThreadExecutor())
        .build();
```

对于 RAG，未实现 `retrieveAsync` 的检索器默认会失败，而不是静默阻塞。改为通过 `DefaultRetrievalAugmentor` 或 `EmbeddingStoreContentRetriever` 上的 `offloadBlocking(true)` 选择加入转移执行。

## 与同步模式不同的默认值

异步和响应式模式并不只是把同样的交互放到另一个线程上——有几个默认值是有意不同的。如果你在迁移现有方法，以下这些就是需要检查的地方。

| | 同步 / `TokenStream` | `CompletableFuture` / `Flow.Publisher` |
|---|---|---|
| 多个工具调用 | **顺序**执行 | **并发**执行 |
| 工具**执行**错误 | 发回给 LLM | **使调用失败**，除非该异常实现了 `ToolErrorVisibleToLlm` |
| 工具**参数解析**错误 | **使调用失败** | 发回给 LLM |
| `@Moderate` | 支持 | 在创建 AI 服务时即被拒绝 |

### 工具错误

这两个工具错误的默认值是有意反转的。把*执行*失败发回给 LLM 会把你工具里的 bug 隐藏起来，并诱导模型绕着它编造答案，因此异步模式改为使调用失败，除非异常本身指明了可以告诉 LLM 的内容（参见 [`ToolErrorVisibleToLlm`](tools.md#逐异常决定-llm-看到什么)）。另一方面，畸形的*参数*字符串是模型自己产生的，被告知后通常能自行修正，因此将其发回，而不是使调用失败。

两者都保持可配置，且显式配置的处理程序会被所有模式使用：

```java
AiServices.builder(Assistant.class)
        .chatModel(model)
        .tools(new MyTools())
        .toolExecutionErrorHandler(myExecutionErrorHandler)
        .toolArgumentsErrorHandler(myArgumentsErrorHandler)
        .build();
```

这些处理程序能做什么，参见 [错误处理](tools.md#错误处理)。

### 工具并发

因为在这些模式下工具总是在 `Executor` 上运行，一个 LLM 响应中的多个工具调用会同时执行。如果你的工具并发运行不安全，请传入单线程执行器：`executeToolsConcurrently(Executors.newSingleThreadExecutor())`。

### 事件顺序

在响应式路径上，工具一旦其 `CompleteToolCallEvent` 发出就开始运行，因此会与本轮的其余部分重叠。因此，某轮的 `BeforeToolExecutionEvent` / `AfterToolExecutionEvent` 可能**先于**该轮的 `IntermediateResponseEvent` 到达。请把 `IntermediateResponseEvent` 当作每轮的标记，而不是一个屏障（即该轮的所有工具事件都先于它到达）。基于回调的 `TokenStream` 总是先报告中间响应。

## 控制执行器并传播上下文

LangChain4j 在所有把工作移出调用方线程的地方——并发工具调用、转移执行的检索、重试退避——都从一个可插拔接缝获取执行器，即 `ExecutorProvider` SPI：

```java
public interface ExecutorProvider {

    Executor executor();

    default CapturedContext captureContext() {
        return CapturedContext.NONE;
    }
}
```

通过 `ServiceLoader` 注册一个，或者在测试和非 DI 应用中以编程方式注册：

```java
ExecutorProvider.set(() -> myExecutor);
```

如果没有注册，LangChain4j 在 Java 21 及更高版本上使用每任务一个虚拟线程的执行器，在 Java 17-20 上使用无界平台线程池。

!!! note
    一次调用会跨越多个线程，因此环境 `ThreadLocal` 状态——MDC 日志上下文、链路追踪 span、安全上下文——**不会**像完全同步模式那样自动传播。要让它们跟随工作，请实现 `captureContext()`。LangChain4j 每次调用会调用它一次，在调用 AI 服务方法的线程上，并让该调用转移到执行器上的所有任务（工具、阻塞的 RAG 阶段、内容审核）都在捕获的上下文中运行。用 `ExecutorProvider.set(() -> myExecutor)` 注册的 lambda 无法做到这一点，因此请改为注册一个类，例如结合 Micrometer 上下文传播：

    ```java
    import dev.langchain4j.spi.CapturedContext;
    import dev.langchain4j.spi.ExecutorProvider;
    import io.micrometer.context.ContextSnapshotFactory;
    import java.util.concurrent.Executor;

    public class ContextPropagatingExecutorProvider implements ExecutorProvider {

        private static final ContextSnapshotFactory CONTEXT_SNAPSHOT_FACTORY = ContextSnapshotFactory.builder().build();

        @Override
        public Executor executor() {
            return null; // keeps the built-in default
        }

        @Override
        public CapturedContext captureContext() {
            return CONTEXT_SNAPSHOT_FACTORY.captureAll()::wrap;
        }
    }
    ```

    ```java
    ExecutorProvider.set(new ContextPropagatingExecutorProvider());
    ```

    对于 OpenTelemetry，`captureContext()` 为 `return Context.current()::wrap;`。对于 MicroProfile Context Propagation：

    ```java
    private static final ThreadContext THREAD_CONTEXT = ThreadContext.builder().build();

    @Override
    public CapturedContext captureContext() {
        Executor callerContext = THREAD_CONTEXT.currentContextExecutor();
        return task -> () -> callerContext.execute(task);
    }
    ```

    `captureContext()` 在每次调用时都会被调用，因此必须开销很小。它返回的 `CapturedContext` 可能包装多个同时运行的任务，每个包装的任务在完成时必须恢复其运行线程之前的上下文：任务运行在池化线程上，遗留下来的上下文会泄漏到无关的任务中。上面的示例遵循了这些规则。

    一些需要注意的事项：

    - 仅使用上下文传播执行器（一个 `ManagedExecutor`、一个用 `TaskDecorator` 包装的执行器、`Context.taskWrapping(executor)`、…）是不够的：它捕获的是*提交*任务的线程的上下文，而大部分被转移的工作是在模型回答之后、从交付答案的线程提交的。它可以与 `captureContext()` 结合使用：这样任务就会在捕获的上下文中运行。
    - LangChain4j 不转移的工作——护栏、聊天记忆、监听器、流式回调——在当前线程上运行，不会获得捕获的上下文。
    - AI 服务调用之外转移的工作也不会获得：重试退避、模型集成自行启动的线程（例如用于读取流式响应）、以及 `langchain4j-agentic` 中的并行和异步智能体。如果你需要那里的上下文，请结合 `captureContext()` 与上下文传播执行器。
    - 对于返回 `Flow.Publisher`、`Mono` 或 `Flux` 的方法，上下文在方法被调用时捕获，而不是在结果被订阅时捕获。
    - 捕获的上下文会保持到调用结束，因此被转移的工作可能在发起调用的请求完成后才带着它运行（例如带着一个此后已结束会话的安全上下文）。
    - 只有 `ExecutorProvider` 会捕获上下文。运行在传给 AI 服务的执行器（通过 `executeToolsConcurrently(executor)`）上的工具，仍然运行在该执行器自己捕获的上下文中。
    - 这适用于用 `AiServices` 创建的 AI 服务。自行构建 AI 服务实现的框架自行决定如何传播上下文。

    `InvocationContext` 不受影响——它作为参数显式传递，绝不通过 thread-local 传递。

## 模型监听器不得阻塞

`ChatModelListener` 和 `EmbeddingModelListener` 回调在模型自己的线程上同步调用，且从不被转移。对异步和响应式 API 而言，这意味着是传输层的 I/O 工作线程。在那里执行阻塞 I/O 的监听器会卡住该工作线程，并降低所有在途调用的吞吐量——请在回调内部把这类工作转移到你自己的执行器上。参见 [可观测性](observability.md)。

## 提供商支持

!!! warning
    **非阻塞模式仅支持已实现该功能的提供商。** 对任何其他提供商声明 `CompletableFuture` 或 `Flow.Publisher` 返回类型都能编译通过，但随后会在运行时以指明组件和缺失方法的 `AsyncNotSupportedException` 失败。不存在向阻塞调用的静默回退——这正是设计意图，但也意味着你能使用的返回类型取决于你的提供商。

支持是逐提供商选择加入的，目前正在逐步推出。目前的情况：

| 提供商 | `CompletableFuture`（`chatAsync`） | `Flow.Publisher`（响应式 `chat`） |
|---|---|---|
| OpenAI — Chat Completions | ✅ | ✅ |
| OpenAI — Responses | ✅ | ✅ |
| Anthropic | ✅ | ✅ |
| Bedrock | ✅ | ✅ |
| 其他所有提供商 | ❌ | ❌ |

除聊天模型外：OpenAI 实现了异步嵌入（`embedAsync`），Cohere 实现了异步评分（`scoreAsync`），Tavily 实现了异步网页搜索（`searchAsync`）。

未选择加入的提供商在同步和 `TokenStream` API 上不受影响——它们完全按原来的方式继续工作。

### 调用链中的其他所有组件同理

支持该模式的聊天模型是必要条件，但并非充分条件：交互中任何位置的单个阻塞组件都会以同样的方式使调用失败。具体来说，这意味着：

| 组件 | 必须实现的方法 | 捆绑的实现 |
|---|---|---|
| 聊天记忆 | `addAsync` / `messagesAsync` / `setAsync` | `MessageWindowChatMemory` 和 `InMemoryChatMemoryStore` 已支持 |
| 护栏 | `validateAsync` | 无——你编写的护栏必须重写它，即使它不做任何 I/O |
| 内容检索器、查询路由器、聚合器 | `retrieveAsync`、`routeAsync`、`aggregateAsync` | 改为通过 `offloadBlocking(true)` 选择加入转移执行 |
| 向量存储 | `searchAsync` | 同上，通过检索器的 `offloadBlocking(true)` |
| 自定义 `ToolExecutor` | `executeAsync` | 用 `@Tool` 注解的方法会为你自动转移执行 |
| 聊天模型路由器（[`RoutingChatModel`](model-routing.md)） | `routeAsync` | `DecisionModelChatModelRouter` 支持（如果其决策模型支持 `decideAsync`） |

不做阻塞工作的护栏一行即可满足契约：

```java
@Override
public CompletableFuture<InputGuardrailResult> validateAsync(InputGuardrailRequest request) {
    return CompletableFuture.completedFuture(validate(request));
}
```

### Spring Boot

`Flux<String>` 对**所有**提供商保持可用，包括 ❌ 行的那些：它由 `langchain4j-reactor` 中基于 `TokenStream` 的适配器提供，而不是由本页描述的非阻塞路径提供。

`Mono<T>` 和 `Flux<AiServiceStreamingEvent>` 来自 `langchain4j-reactor` 模块，与 JDK 类型一样带有相同的提供商约束——参见上文[第三方响应式类型](#第三方响应式类型)。

要让环境上下文跟随异步调用，请让 LangChain4j 转移到应用自己的执行器上，而不是其默认执行器：

```properties
langchain4j.executor.use-spring-task-executor=true
```

这样 LangChain4j 就会在应用的任务执行器上运行被转移的工作，其线程池遵循 `spring.task.execution.*`。该设置默认关闭，因为它是进程级的，而不是限定在单个应用上下文内。

从 Spring Boot starters 的 1.23.0-beta33 版本开始，调用方的上下文也会被捕获（参见[上文](#控制执行器并传播上下文)），因此链路追踪 span、MDC 和安全上下文会跟随 LangChain4j 转移的工作：

- 如果应用定义了 `TaskDecorator` bean（例如 `ContextPropagatingTaskDecorator`），它们决定捕获什么，与应用于自身任务执行器时相同；
- 否则，如果 classpath 上有 Micrometer 上下文传播，则使用它。
