# 模型路由

!!! note
    模型路由目前处于实验阶段，可能会在未来的版本中发生变化。

不同的请求需要不同的模型：问候或简短的事实类问题可以用小型、快速且低成本的模型来回答，而编写代码或
进行详细分析则需要更大的模型。借助模型路由，每个请求都会被发送到适合它的模型，而无需改动应用的其余部分。

`RoutingChatModel` 是一个 `ChatModel`，它会按照 `ChatModelRouter` 的决策，将每个请求发送到多个聊天模型（路由）中的
一个。由于它本身是一个 `ChatModel`，因此可以在所有使用聊天模型的地方使用：AI 服务、智能体、RAG 等。

```java
ChatModel chatModel = RoutingChatModel.builder()
        .route("simple", "Greetings, small talk and short factual questions", smallModel)
        .route("complex", "Writing or debugging code, multi-step reasoning, detailed analysis", largeModel)
        .router(new DecisionModelChatModelRouter(decisionModel))
        .defaultRoute("complex")
        .build();

Assistant assistant = AiServices.create(Assistant.class, chatModel);
```

`smallModel` 和 `largeModel` 可以是任意的 `ChatModel`，`decisionModel` 可以是任意的 `DecisionModel`，例如
`TypeSafeDecisionModel`（参见 [决策模型](decision-models.md)）。下文展示了无需模型的路由器。

对于流式，请使用 `RoutingStreamingChatModel` 配合 `StreamingChatModel`；它的工作方式相同。

## 路由器

`ChatModelRouter` 返回一个 `ChatModelRoutingResult`：对于某个路由使用 `ChatModelRoutingResult.route(name)`，
对于默认路由使用 `ChatModelRoutingResult.defaultRoute()`。
默认路由是必需的，这样无论何时都能有一个可以接收请求的模型，例如当调用模型的路由器不确定或失败时。

### 决策模型路由器

`DecisionModelChatModelRouter` 使用 [决策模型](decision-models.md) 来选择描述与请求最匹配的路由。它会发送
对话中的最后 3 条消息（`maxMessages`），以便理解“好的，继续吧”这样的简短跟进消息。只发送并计入用户消息和 AI 的
文本回复：系统消息、工具调用和工具结果会被排除。文本之外的内容（例如图像）会以标记（例如 `[attached image]`）表示，
这样描述中提到图像的路由就可以被选中。决策模型通常比聊天模型快得多、便宜得多，因此与聊天模型调用相比，
路由只会增加很少的延迟和成本。请为每个路由编写好的描述；没有描述的路由会用其名称作为描述。

当请求中没有用户消息时，以及当所选路由的概率低于 `minProbability` 时，它会选择默认路由，这在将决策模型
不确定的请求发送给更大的模型时很有用。`minProbability` 需要一个能报告概率的决策模型，否则调用会失败。
当决策模型失败时，会使用默认路由并记录一条警告；可设置 `fallbackStrategy(FAIL)` 让请求直接失败。

```java
ChatModelRouter router = DecisionModelChatModelRouter.builder()
        .decisionModel(decisionModel)
        .minProbability(0.7)
        .build();
```

面向多个不相关主题请求的路由可以有多个描述：

```java
ChatModel chatModel = RoutingChatModel.builder()
        .route("simple", "Greetings, small talk and short factual questions", smallModel)
        .route("complex", List.of("Writing or debugging code", "Legal contract analysis", "Tax planning"), largeModel)
        .router(new DecisionModelChatModelRouter(decisionModel))
        .defaultRoute("simple")
        .build();
```

此时决策模型会将每个描述视为一个独立的选项，路由的概率是其所有描述的概率之和。与列出所有主题的单一描述
相比，这能让决策更有把握，尤其在使用较小的决策模型时。当决策模型不确定时，它会把概率分摊到所有选项上，
因此描述更多的路由会分得更多：除非某个路由应当赢得模糊的情况，否则应保持各路由的描述数量均衡。

### 自定义路由器

路由器也可以只是一条简单的规则：

```java
ChatModel chatModel = RoutingChatModel.builder()
        .route("simple", smallModel)
        .route("complex", largeModel)
        .router(request -> ChatModelRoutingResult.route(
                request.chatRequest().messages().size() > 20 ? "complex" : "simple"))
        .defaultRoute("simple")
        .build();
```

路由器会接收到 `ChatRequest`、调用选项以及可以处理该请求的路由（`ChatModelRoute`：名称和描述）。
路由器也可以在创建路由聊天模型时通过实现 `validate(...)` 来检查路由。

### 异步调用

`chat(...)` 和使用 `StreamingChatResponseHandler` 的流式调用会在调用线程上调用 `route(...)`，该方法在选择路由
期间会阻塞：对于 `DecisionModelChatModelRouter`，会阻塞直到决策模型返回答案。请勿从事件循环线程（例如
Vert.x 或 Quarkus 响应式端点中）调用它们。
非阻塞方法 `chatAsync(...)` 以及向 `Publisher` 的流式调用（`StreamingChatModel.chat(ChatRequest)`）则改为调用
`routeAsync(...)`，从而保证路由永远不会阻塞。`routeAsync(...)` 默认没有实现，因此以 lambda 编写的路由器会使
这些调用抛出 `AsyncNotSupportedException` 而失败。
要在非阻塞调用中使用这类路由器，请实现 `routeAsync(...)`：

```java
ChatModelRouter router = new ChatModelRouter() {

    @Override
    public ChatModelRoutingResult route(ChatModelRoutingRequest request) {
        return ChatModelRoutingResult.route(
                request.chatRequest().messages().size() > 20 ? "complex" : "simple");
    }

    @Override
    public CompletableFuture<ChatModelRoutingResult> routeAsync(ChatModelRoutingRequest request) {
        return CompletableFuture.completedFuture(route(request)); // route(...) does not block
    }
};
```

会阻塞的路由器（例如在数据库中查询用户的路由器），可以改为使用
`CompletableFuture.supplyAsync(() -> route(request), executor)` 在自己选择的 executor 上运行 `route(...)`，或者更好的
方式是使用非阻塞客户端。`DecisionModelChatModelRouter` 通过 `DecisionModel.decideAsync(...)` 实现了 `routeAsync(...)`。

## 请求如何被路由

- 选中的模型会像被直接调用一样处理请求：它的默认参数和监听器都会生效。
- 请求可能会去往不同提供商的模型，因此只应设置通用的请求参数
  （`ChatRequestParameters`），不要设置特定于提供商的参数。
- 所选路由的名称会被添加到该调用的监听器属性中
  （位于 `RoutingChatModel.ROUTE_ATTRIBUTE` 下），以便所选模型的监听器可以上报它，并且会被保存在返回的 `AiMessage` 的属性中。
- 工具调用循环的各个轮次会保持在同一模型上：以工具结果结尾的请求会直接去往请求这些工具时保存在 `AiMessage`
  中的路由，而不再询问路由器。只要持久化的聊天记忆保留消息的属性（默认序列化会保留），这对持久化聊天记忆同样有效。
- `supportedCapabilities()` 返回至少有一个路由支持的能力。需要某个能力的请求
  （例如 JSON schema 响应格式）只会路由到声明了该能力的路由：
  路由器只能看到这些路由，并且如果默认路由没有声明该能力，则使用第一个声明了它的路由。
  如果没有任何路由声明该能力，则所有路由仍然是候选，所选模型会自行接受或拒绝该请求，就像被直接调用时一样。
- 如果路由器返回一个未知路由，请求会以 `IllegalStateException` 失败。
- 所选模型会在完成路由的线程上被调用：即调用线程，或者在非阻塞调用中完成 `routeAsync(...)` 的线程
  （例如决策模型响应所在的线程）。
- 当路由聊天模型嵌套使用时，保存在 `AiMessage` 中的名称是外层路由聊天模型的名称。
  在工具调用循环中，内层路由聊天模型找不到自己的路由，于是再次询问其路由器，路由器可能选中另一个模型。
  如果内层路由与外层路由同名，内层路由聊天模型会使用其同名路由。请为嵌套路由聊天模型的路由使用互不相同的名称。

## 需要注意的事项

- 所有路由共享对话：新的用户消息之后，一条路由产生的消息可能会被另一条路由接收。不同提供商的路由
  必须能够读取彼此的消息。当存在特定于提供商的内容时可能会失败，例如以另一种提供商不接受的格式返回
  带签名或工具调用 id 的思考内容。在同一提供商的模型之间路由可以避免这种情况。
- `DecisionModelChatModelRouter` 看到的是消息的文本，而不是图像或其他附件的内容：它只知道有附件被附上。
- 在带 RAG 的 AI 服务中，`DecisionModelChatModelRouter` 看到的是加入了检索内容的用户消息，与聊天模型看到的一样：
  检索到的文档会参与决策，而长内容可能超出决策模型的输入限制，此时会使用默认路由并记录一条警告。
- 提示词缓存是按模型划分的：在路由之间切换的对话无法利用上一个模型的缓存，在长对话中，这可能超过路由带来的节省。
- 路由聊天模型自身没有默认请求参数，`provider()` 返回 `OTHER`：从聊天模型读取默认请求参数的代码
  （例如用于调整 `toolChoice`）看到的是空参数，而不是路由的参数。所选模型的默认参数仍然适用于每个请求。
- 当路由聊天模型与其路由都是同类型的 bean 时，请确保 AI 服务使用的是路由聊天模型，例如在 Spring Boot 中使用
  `@AiService(wiringMode = EXPLICIT, chatModel = "routingChatModel")`。
- 监听器配置在路由模型上，而不是路由聊天模型上：所选模型的监听器会观察每次调用，并且路由名称可用在其属性中
  （`RoutingChatModel.ROUTE_ATTRIBUTE`），例外是 `StreamingChatModel.chat(ChatRequest)` 返回的 `Publisher`，它不接受选项：
  此时路由名称只在响应的属性中。
- 路由在请求发送之前选择模型；它不会将失败的请求在另一个模型上重试。
