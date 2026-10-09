# 模型上下文协议（MCP）

!!! note
    MCP 客户端可以通过 `executeToolAsync(...)` 在不阻塞线程的情况下执行工具，
    它被异步和响应式 AI 服务模式使用。
    参见[非阻塞与响应式](non-blocking.md)。

LangChain4j 支持模型上下文协议（MCP），用于与能够提供并执行工具的
MCP 兼容服务器进行通信。关于该协议的一般信息
可以在 [MCP 网站](https://modelcontextprotocol.io/) 上找到。

!!! note
    想在 Java 中构建 MCP **stdio 服务器**？
    服务器实现位于 LangChain4j Community。参见[构建 Java MCP stdio 服务器](mcp-stdio-server.md)。

该协议规定了两种传输类型，两者均受支持：

- [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#streamable-http)：
  客户端发送 HTTP 请求，服务器要么以常规响应进行回复，要么在需要随时间发送
  多个响应时打开一个 SSE 流。
- [stdio](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports#stdio)：客户端
  可以将 MCP 服务器作为本地子进程运行，
  并通过标准输入/输出与其直接通信。

在规范之上，LangChain4j 实现了 `WebSocket` 传输。该传输尚未标准化，目前
客户端侧的实现方式与
[Quarkus MCP Server 扩展](https://docs.quarkiverse.io/quarkus-mcp-server/dev) 实现的 WebSocket 传输兼容。对于暴露 WebSocket 但
使用其他框架构建的 MCP 服务器，不保证兼容性。

此外，LangChain4j 还支持一种 Docker stdio 传输，它可以利用以容器
镜像形式分发的 stdio MCP 服务器。

要让你的聊天模型或 AI 服务运行由 MCP 服务器提供的工具，
你需要创建一个 MCP 工具提供器实例。

## 创建 MCP 工具提供器

### MCP 传输

首先，你需要一个 MCP 传输实例。

对于 stdio，下面的示例展示了如何从 NPM 包以子进程方式启动服务器：

```java
McpTransport transport = StdioMcpTransport.builder()
    .command(List.of("/usr/bin/npm", "exec", "@modelcontextprotocol/server-everything@0.6.2"))
    .logEvents(true) // only if you want to see the traffic in the log
    .build();
```

如果服务器需要在特定项目目录中运行，请在 stdio 传输构建器上配置
`.workingDirectory(Path.of("/path/to/project"))`。
该目录同时适用于服务器子进程的启动和重启。如果
省略，子进程将继承当前进程的工作目录。

对于 Streamable HTTP 传输，你需要提供服务器 `POST` 端点的 URL：

```java
McpTransport transport = StreamableHttpMcpTransport.builder()
        .url("http://localhost:3001/mcp")
        .logRequests(true) // if you want to see the traffic in the log
        .logResponses(true)
        .build();
```

**_注意：_**（仅限遗留（旧版）协议）Streamable HTTP 传输可以选择性开启一个辅助的
[基于 GET 的 SSE 流](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#listening-for-messages-from-the-server)，
用于接收服务器发起的通知和请求。在构建器上启用 `.subsidiaryChannel(true)` 即可开启。
在现代协议（2026-07-28）中，通知改为通过 `subscriptions/listen` 接收。
默认情况下它是禁用的。如果服务器不支持它，传输会记录一条警告日志，并在没有该流的情况下继续。
如果流在建立之后中断，传输会自动重连（遵循服务器的 `retry` 值，默认为 5 秒）。

对于 WebSocket 传输：
```java
McpTransport transport = WebSocketMcpTransport.builder()
        .url("ws://localhost:3001/mcp/ws")
        .logResponses(true)
        .logRequests(true)
        .build();
```

对于 Docker stdio 传输，你需要先在 pom.xml 中添加一个模块：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-mcp-docker</artifactId>
</dependency>
```

然后你需要创建一个 Docker 传输：

```java
McpTransport transport = DockerMcpTransport.builder()
    .image("mcp/time")
    .dockerHost("unix:///var/run/docker.sock")
    .logEvents(true) // if you want to see the traffic in the log
    .build();
```

### MCP 客户端

要从传输创建 MCP 客户端：

```java
McpClient mcpClient = DefaultMcpClient.builder()
    .key("MyMCPClient")
    .transport(transport)
    .build();
```

注意，客户端键（key）是可选的，但建议设置它，尤其是
当存在多个 MCP 客户端且需要在它们之间加以区分时。

### 协议版本

MCP 客户端同时支持遗留（旧版）协议（2025-11-25）和现代的
无状态协议（2026-07-28）。默认情况下，客户端会自动检测服务器的
协议版本，当服务器支持 2026-07-28 时优先选择该版本：

```java
// Auto-detect (default behavior)
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .build();

// Force modern protocol
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .protocolVersion("2026-07-28")
    .build();

// Force legacy protocol
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .protocolVersion("2025-11-25")
    .build();
```

检测在客户端启动时会额外消耗一次往返：它会发送一个 `server/discover`
请求，如果应答是一个错误，或者在 `protocolDetectionTimeout` 之内
没有到达，则把服务器当作遗留（旧版）服务器处理。该超时的默认值为 `initializationTimeout`
（30 秒），因为以子进程方式启动的服务器需要一段时间完成启动才能
应答任何请求，过早放弃会让现代服务器看起来像遗留（旧版）服务器。
由静默（而非错误）导致的回退会被记录为警告日志，因为这种情况
下服务器有可能是被误判的。

```java
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .protocolDetectionTimeout(Duration.ofSeconds(5)) // servers you know answer quickly
    .build();
```

显式设置 `protocolVersion` 会完全跳过检测。当你已经知道
服务器使用哪个协议版本时，这样做是值得的；如果某个
服务器对收到它不认识的方法反应异常，这也是解决之道：一些较旧的 MCP 服务器
实现在收到未知请求时会直接终止，而不是返回错误应答。

### MCP 工具提供器

最后，你从客户端创建一个 MCP 工具提供器：

```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .build();
```

注意，一个 MCP 工具提供器可以同时使用多个客户端。
如果你利用了这一点，你还可以指定当从某个特定服务器
检索工具失败时工具提供器的行为——这通过
`builder.failIfOneServerFails(boolean)` 方法完成。默认值为 `false`，
意味着工具提供器将忽略来自某个服务器的错误，
并继续处理其他服务器。如果你将它设置为 `true`，来自任何
服务器的失败都会导致工具提供器抛出异常。

此外，MCP 服务器通常可能提供数十个工具，而给定的 AI 服务
可能只需要其中少数几个，这既是为了防止使用不想要的工具，也是为了
降低发生幻觉的可能性。`McpToolProvider` 允许你按名称过滤
这些工具，如下所示：

```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .filterToolNames("get_issue", "get_issue_comments", "list_issues")
    .build();
```

这样一来，配置了这个 `ToolProvider` 的 AI 服务就只能使用
上述提到的 3 个工具，允许它读取现有的 issue，但阻止它
创建新的 issue。更一般地，`ToolProvider` 允许你通过
`BiPredicate<McpClient, ToolSpecification>` 来过滤工具。当多个 MCP 客户端暴露了同名
因而相互冲突的工具时，这也很有用。
例如，下面的 `ToolProvider` 从两个 MCP 客户端
获取工具，但由于它们都有一个名为 `echoInteger` 的工具，它只取来自
键为 `numeric-mcp` 的 MCP 客户端的那个：

```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClient1, mcpClient2)
    .filter((mcpClient, tool) ->
            !tool.name().startsWith("echoInteger") || 
            mcpClient.key().equals("numeric-mcp"))
    .build();
```

注意，在同一个 `McpToolProvider` 构建器上多次调用 `filter` 方法
会产生所有这些过滤器之间的合取（AND）关系。

为了允许应用程序在运行时连接或断开与 MCP 服务器的连接，
也可以向现有的 `McpToolProvider` 实例动态添加和移除客户端及过滤器。

要将工具提供器绑定到 AI 服务，只需使用 AI 服务构建器的 `toolProvider` 方法：

```java
Bot bot = AiServices.builder(Bot.class)
    .chatModel(model)
    .toolProvider(toolProvider)
    .build();
```

或者，你也可以使用 `Map<ToolSpecification, ToolExecutor>` 来提供工具。

```java
Map<ToolSpecification, ToolExecutor> tools = mcpClient.listTools().stream().collect(Collectors.toMap(
        tool -> tool, 
        tool -> new McpToolExecutor(mcpClient)
));
```

要将工具绑定到 AI 服务，只需使用 AI 服务构建器的 `tools` 方法：

```java
Bot bot = AiServices.builder(Bot.class)
    .chatModel(model)
    .tools(tools)
    .build();
```

有关 LangChain4j 中工具支持的更多信息，可以在[此处](tools.md)找到。

### MCP 工具名称映射

如果你使用多个 MCP 服务器，它们暴露了名称冲突的工具（或者你只是想
调整一个不恰当的名字），那么应用一个工具名称映射函数可能很有用。
这可以在创建 `McpToolProvider` 时通过指定 `BiFunction<McpClient, ToolSpecification, String>` 来完成。

例如：
```java
McpToolProvider toolProvider = McpToolProvider.builder()
        .mcpClients(mcpClient1, mcpClient2)
        .toolNameMapper((client, toolSpec) -> {
            // Prefix all tool names with the name of the MCP client and an underscore
            return client.key() + "_" + toolSpec.name();
        })
        .build();
```

此后，工具提供器返回的 `ToolSpecification` 对象将包含映射后的（逻辑）名称，
但生成的 `ToolExecutor` 对象会被固定为在调用工具时向服务器传递原始的（物理）名称。

### MCP 工具规范映射

与上文的 MCP 工具映射类似，你还可以映射完整的 `ToolSpecification`：
```java
McpToolProvider toolProvider = McpToolProvider.builder()
        .mcpClients(mcpClient)
        .toolSpecificationMapper((client, toolSpec) -> {
            // Prefix all tool names with "myprefix_" and convert the description to uppercase
            return toolSpec.toBuilder()
                .name("myprefix_" + toolSpec.name())
                .description(toolSpec.description().toUpperCase())
                .build();
        })
        .build();
```

### MCP 工具元数据

MCP 协议允许服务器为每个工具提供额外的元数据，形式可以是注解，
也可以是工具定义中的 `_meta` 字段。
LangChain4j 通过 `ToolSpecification.metadata()` 方法内部存储的 map 暴露所有这些元数据。
注解使用可以在 `dev.langchain4j.mcp.client.McpToolMetadataKeys` 类中
作为常量找到的键存储在 map 中。
`_meta` 字段的内容按其原始键存储，JSON 值会被序列化
为嵌套 map。

直接存在于 MCP 工具定义中的 `title` 字段，会通过元数据 map 中的
`McpToolMetadataKeys.TITLE` 键暴露，以便与从注解中获取的 title
相区分——后者通过 `McpToolMetadataKeys.ANNOTATION_TITLE` 键暴露。

如果工具带有图标，它们会通过元数据 map 中的 `McpToolMetadataKeys.ICONS` 键暴露。

### MCP 工具结果元数据

除了实际结果之外，MCP 服务器还可以在工具调用的响应上附加一个 `_meta` 对象。
这对于你的应用程序需要而 LLM 不需要的数据很有用，例如工具
所创建记录的标识符，或你的 UI 应当渲染的 widget。

`_meta` 对象的各个条目通过 `ToolExecutionResult.attributes()` 暴露，使用其
原始键，JSON 值会被转换为嵌套 map。它们永远不会被发送给 LLM。
被 MCP 规范保留的键（如 `io.modelcontextprotocol/serverInfo`）
会被跳过，因为它们描述的是协议交互而非工具结果。

当直接在客户端上调用工具时，这些属性始终可用：

```java
ToolExecutionResult result = mcpClient.executeTool(toolExecutionRequest);
Object widget = result.attributes().get("example.org/widget");
```

当工具由 AI 服务调用时，这些属性默认会被丢弃，
因为它们的大小和内容由 MCP 服务器控制。
要保留它们，请在工具提供器上启用 `returnToolResultAttributes`：

```java
McpToolProvider toolProvider = McpToolProvider.builder()
    .mcpClients(mcpClient)
    .returnToolResultAttributes(true)
    .build();
```

然后，你可以从结果的 tool executions 中读取它们：

```java
interface Assistant {

    Result<String> chat(String userMessage);
}

Result<String> result = assistant.chat("What is the weather in Munich?");
for (ToolExecution toolExecution : result.toolExecutions()) {
    Object widget = toolExecution.attributes().get("example.org/widget");
}
```

这些属性还会被传播到 `ToolExecutionResultMessage`，
因此它们会随消息一起存储在聊天记忆中。
当聊天记忆被持久化时，请记住这一点，有关更多细节，参见
[工具结果属性](tools.md#工具结果属性)。

如果工具返回应用级错误（工具结果中为 `"isError": true`），该调用将以
`McpApplicationErrorException` 结束，它是 `ToolExecutionException` 的子类，且失败响应的 `_meta`
不可用。它仍会被传递给 `McpClientListener.afterExecuteTool()`，后者会收到完整的
原始响应。

应用级错误是 MCP 服务器告诉*模型*某个工具没有执行成功的方式，因此其文本是
写给 LLM 的。`McpApplicationErrorException` 因此实现了 `ToolErrorVisibleToLlm`：借助一个
会尊重它的工具执行错误处理器（如 `ToolExecutionErrorHandler.failInvocationUnlessVisibleToLlm()`），
服务器的文本会被发送给 LLM，LLM 可以据此作出反应。使用该处理器时，协议错误——意味着
调用本身出了问题——会导致 AI 服务调用失败；没有任何
文本的应用级错误也是如此，它就是一个普通的 `ToolExecutionException`。
参见[错误处理](tools.md#错误处理)。

### 通过 HTTP 头传递的工具参数

在使用 Streamable HTTP 的 2026-07-28 协议下，服务器可以要求将选定的工具
参数在请求体之外，以 HTTP 头的形式发送，这样代理和
网关就可以在不解析请求体的情况下对调用进行路由或授权。服务器会在工具的输入 schema 中
用 `x-mcp-header` 来标记这样的参数：

```json
{
  "name": "query_database",
  "inputSchema": {
    "type": "object",
    "properties": {
      "tenant": { "type": "string", "x-mcp-header": "X-Tenant-Id" },
      "sql": { "type": "string" }
    }
  }
}
```

当工具被调用时，客户端会同时在请求体和一个 `Mcp-Param-X-Tenant-Id` HTTP 头中发送 `tenant` 的值。
这是自动完成的，无需任何
配置。不适合放入头的值（例如包含非 ASCII
字符的值）会按照协议要求进行 Base64 编码。

只有 `string`、`integer` 和 `boolean` 类型的参数可以这样标记，头的名称必须是
有效的 HTTP token，且同一个头名称不能被声明两次。如果某个工具的定义
违反了这些规则，它会被排除在 `listTools()` 之外，并记录一条警告日志，因为客户端
无法判断这样的调用本应如何到达服务器。

头的名称是从工具定义中读取的，因此客户端需要先知道工具列表
才能发送这些头。如果你在一个从未列出过工具的客户端上调用 `executeTool()`，
这些头会被省略，并记录一条警告日志；请先调用 `listTools()`。工具提供器会
自行处理这一点。

## 提供 `_meta` 字段

MCP 协议允许客户端向发送到服务器的每个
请求和通知的 `params` 附加一个 `_meta` 对象。这可以用于传递
OpenTelemetry 链路追踪上下文、自定义的应用程序元数据，或服务器可能需要的
其他任何带外信息。

要提供 `_meta` 字段，请在客户端构建器上注册一个 `McpMetaSupplier`。
该供应器会在每次请求或通知之前被调用，返回的
map 会被放入 `params._meta`。与 HTTP 头不同，它在所有
传输（stdio、HTTP、WebSocket）上都能工作。

```java
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .metaSupplier(context -> Map.of(
        "traceparent", "00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01",
        "custom-key", "custom-value"))
    .build();
```

该供应器会接收一个 `McpCallContext`（可为 null），其中包含
正在发送的消息，以及（在适用时）触发它的
AI 服务调用的 `InvocationContext`。这使得供应器能够根据正在执行的操作
来动态调整元数据。

## 日志

MCP 协议还定义了服务器向客户端发送日志消息的
方式。默认情况下，客户端的行为是转换这些日志
消息，并使用 SLF4J 日志记录器将它们记录下来。如果你想改变这一
行为，有一个名为
`dev.langchain4j.mcp.client.logging.McpLogMessageHandler` 的接口，可作为
收到日志消息时的回调。如果你自己实现了
`McpLogMessageHandler`，请将它传递给 MCP 客户端构建器：

```java
McpClient mcpClient = new DefaultMcpClient.Builder()
    .transport(transport)
    .logHandler(new MyLogMessageHandler())
    .build();
```

## MCP 监听器

MCP 客户端支持监听器，可以监听客户端
生命周期内发生的事件。
`dev.langchain4j.mcp.client.McpClientListener` 接口是
监听器实现的基础。可以在单个客户端上注册多个监听器；
它们都会在每次工具调用、提示词渲染和资源访问之前与之后被调用。
调用监听器时会注入相应的
`McpCallContext`。该对象
包含正在发送给服务器的实际 MCP 消息，以及在适用时包含
一个 `InvocationContext` 实例（仅当这次调用
是作为 AI 服务调用的一部分发生时）。

监听器可以逐个添加，也可以批量添加：

```java
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .addListener(new MyFirstListener())
    .addListener(new MySecondListener())
    .addListeners(List.of(new MyThirdListener(), new MyFourthListener()))
    .build();
```

## 资源

与资源配合工作有两种方式。要么应用程序调用 MCP 客户端的
资源相关方法，以编程方式访问资源；要么可以选择通过合成工具（一个工具用于获取资源列表，
另一个用于获取资源内容）将资源自动暴露给 LLM 调用，从而使聊天模型能够自行查阅资源。

### 以编程方式访问资源

要获取服务器上 [MCP 资源](https://modelcontextprotocol.io/docs/concepts/resources) 的列表，
使用 `client.listResources()`；对于资源模板，则使用 `client.listResourceTemplates()`。
这将返回一个 `McpResource` 对象列表（对于资源模板则为 `McpResourceTemplate` 列表）。它们
包含资源的元数据，其中最重要的是 URI。

要获取资源的实际内容，使用 `client.readResource(uri)`，传入资源的 URI。
这会返回一个 `McpReadResourceResult`，其中包含一个 `McpResourceContents` 对象列表（单个 URI 上可能存在多个资源内容，例如
当 URI 表示一个目录时）。每个 `McpResourceContents` 对象要么表示一个
二进制 blob（`McpBlobResourceContents`），要么表示文本（`McpTextResourceContents`）。

### 通过合成工具自动暴露资源

如果你在构建 `McpToolProvider` 时通过构建器设置了一个 `McpResourcesAsToolsPresenter` 实例，
MCP 工具提供器会自动在其 `provideTools` 方法的结果中添加两个合成工具，
与背后 MCP 服务器支持的"常规"工具一起提供。一个工具用于获取
资源列表，另一个用于获取特定资源。LangChain4j 提供了
一个名为 `DefaultMcpResourcesAsToolsPresenter` 的默认实现，它会添加这两个工具：

**_注意：_** 本节其余部分描述的是 `DefaultMcpResourcesAsToolsPresenter`。你可以插入自己的
行为不同的实现。

- `list_resources`：列出背后 MCP 服务器暴露的所有资源。该工具不接受参数。
- `get_resource`：读取资源的内容。该工具接受两个参数，二者共同标识一个资源：
MCP 服务器名称和 URI。

`list_resources` 的输出是一个形如以下的 JSON 数组：

```json
[ {
  "mcpServer" : "alice",
  "uri" : "file:///info",
  "uriTemplate" : null,
  "name" : "basicInfo",
  "description" : "Basic information about Alice",
  "mimeType" : "text/plain"
}, {
  "mcpServer" : "bob",
  "uri" : "file:///info",
  "uriTemplate" : null,
  "name" : "basicInfo",
  "description" : "Basic information about Bob",
  "mimeType" : "text/plain"
} ]
```

此数组中的每个文档代表一个资源。每个资源由 `uri` 和 `mcpServer` 的组合标识，
其中 `mcpServer` 是在创建时分配给 MCP 客户端的 `key` 值（参见 `DefaultMcpClient.Builder#key`）。
当聊天模型调用 `list_resources` 工具时，
它会收到这个资源列表，然后可以决定调用 `read_resource`。`list_resources`
和 `get_resource` 工具的默认描述在大多数情况下已经足以向 LLM 解释如何使用它们。但是，如果你需要
自定义这些工具及其参数的描述，可以使用
`DefaultMcpResourcesAsToolsPresenter.Builder` 的方法对其进行覆盖。

### 资源订阅

MCP 协议支持[资源订阅](https://modelcontextprotocol.io/specification/2025-11-25/server/resources#subscriptions)，
允许客户端在服务器上的资源发生变化时收到通知。

#### 遗留（旧版）协议（2025-11-25）

要订阅特定资源的更新，使用 `client.subscribeToResource(uri)`。
当服务器更新资源时，它会发送一个 `notifications/resources/updated` 通知。
要处理这些通知，通过 `onResourceUpdated` 构建器方法注册一个回调：

```java
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .onResourceUpdated((client, uri) -> {
        // re-read the updated resource
        McpReadResourceResult result = client.readResource(uri);
        // process the updated contents...
    })
    .build();

// subscribe to a resource
mcpClient.subscribeToResource("file:///status");

// later, unsubscribe
mcpClient.unsubscribeFromResource("file:///status");
```

#### 现代协议（2026-07-28）

在现代协议下，使用 `subscribeToResources`，它接受
多个 URI 并返回一个订阅 ID：

```java
long subId = mcpClient.subscribeToResources(List.of("file:///status", "file:///config"));
// later, unsubscribe using the subscription ID
mcpClient.unsubscribeFromResources(subId);
```

服务器必须先确认一个订阅，之后才能在其上发送任何内容，因此
`subscribeToResources` 会阻塞，直到该确认到达。如果服务器拒绝
该订阅、拒绝了所请求的 URI，或保持沉默，该调用会抛出异常，而不是
返回一个永远不会传递任何内容的订阅 ID。使用 `resourcesTimeout` 来
控制客户端等待确认的时长：

```java
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .resourcesTimeout(Duration.ofSeconds(10))  // default: 60 seconds
    .build();
```

由于该调用会阻塞，请不要在 `onResourceUpdated` 回调内部调用它：
这些回调运行在从服务器读取消息的线程上，而那正是
需要传递确认的同一个线程。

对于列表变更通知（工具列表、提示词列表、资源列表的变更），
客户端默认会自动订阅。你可以通过
构建器标志来控制这一点：

```java
McpClient mcpClient = DefaultMcpClient.builder()
    .transport(transport)
    .subscribeToToolListChanges(true)      // default: true
    .subscribeToPromptListChanges(true)    // default: true
    .subscribeToResourceListChanges(true)  // default: true
    .build();
```

## 提示词

要获取服务器上的 [MCP 提示词](https://modelcontextprotocol.io/docs/concepts/prompts) 列表，
使用 `client.listPrompts()`。该方法返回一个 `McpPrompt` 列表。`McpPrompt`
包含提示词名称和参数的信息。

要渲染提示词的实际内容，使用 `client.getPrompt(name, arguments)`。渲染后的提示词可以包含一条到多条
消息，这些消息由 `McpPromptMessage` 对象表示。每个 `McpPromptMessage` 包含消息的角色（`user`、`assistant`……）
以及消息的实际内容。目前支持的消息内容
类型有：`McpTextContent`、`McpImageContent` 和 `McpEmbeddedResource`。

你可以使用 `McpPromptMessage.toChatMessage()` 将其转换为 LangChain4j 核心 API 中
通用的 `dev.langchain4j.data.message.ChatMessage`。不过，这在所有情况下都可能做不到。例如，如果提示词消息的 `role`
是 `assistant` 且包含除文本以外的内容，它会抛出
异常。无论角色如何，将包含二进制 blob 内容的消息
转换为 `ChatMessage` 都是不受支持的。

## 通过 Docker 使用 GitHub MCP 服务器

现在，让我们看看如何使用模型上下文协议（MCP）以标准化的方式将 AI 模型与外部工具连接起来。
下面的示例将通过 LangChain4j MCP 客户端与 GitHub 交互，从一个公共 GitHub 仓库获取并总结最新的提交。
为此，无需重新发明轮子，我们可以使用 [MCP GitHub 仓库](https://github.com/modelcontextprotocol) 中现有的 [GitHub MCP 服务器实现](https://github.com/github/github-mcp-server)。

我们的想法是构建一个 Java 应用程序，它连接到在本地 Docker 中运行的 GitHub MCP 服务器，以获取并总结最新的提交。
该示例使用 MCP 的 stdio 传输机制在我们的 Java 应用程序与 GitHub MCP 服务器之间进行通信。

## 在 Docker 中打包和运行 GitHub MCP 服务器

要与 GitHub 交互，我们首先需要在 Docker 中设置好 GitHub MCP 服务器。
GitHub MCP 服务器提供了一个标准化的接口，通过模型上下文协议与 GitHub 交互。
它支持文件操作、仓库管理和搜索功能。

要为我们的 GitHub MCP 服务器构建 Docker 镜像，你需要从 [MCP servers GitHub 仓库](https://github.com/modelcontextprotocol/servers/tree/main/src/github) 获取代码，可以通过克隆仓库或下载代码。
然后，进入根目录并执行以下 Docker 命令：

```bash
docker build -t mcp/github -f src/github/Dockerfile .
```
`Dockerfile` 会设置必要的环境并安装 GitHub MCP 服务器实现。
构建完成后，镜像将在本地以 `mcp/github` 的名称可用。

```bash
docker image ls

REPOSITORY   TAG         IMAGE ID        SIZE
mcp/github   latest      b141704170b1    173MB
```

## 开发工具提供器

让我们创建一个名为 `McpGithubToolsExample` 的 Java 类，使用 LangChain4j 连接到我们的 GitHub MCP 服务器。该类将：

* 在 Docker 容器中启动 GitHub MCP 服务器（`docker` 命令位于 `/usr/local/bin/docker`）
* 使用 stdio 传输建立连接
* 使用 LLM 总结 LangChain4j GitHub 仓库的最后 3 个提交

> **注意**：在下面的代码中，我们通过环境变量 `GITHUB_PERSONAL_ACCESS_TOKEN` 传递 GitHub token。但对于公共仓库上一些不需要认证的操作来说，这是可选的。

以下是实现：

```java
public static void main(String[] args) throws Exception {

    ChatModel model = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .logRequests(true)
        .logResponses(true)
        .build();

    McpTransport transport = new StdioMcpTransport.Builder()
        .command(List.of("/usr/local/bin/docker", "run", "-e", "GITHUB_PERSONAL_ACCESS_TOKEN", "-i", "mcp/github"))
        .logEvents(true)
        .build();

    McpClient mcpClient = new DefaultMcpClient.Builder()
        .transport(transport)
        .build();

    ToolProvider toolProvider = McpToolProvider.builder()
        .mcpClients(List.of(mcpClient))
        .build();

    Bot bot = AiServices.builder(Bot.class)
        .chatModel(model)
        .toolProvider(toolProvider)
        .build();

    try {
        String response = bot.chat("Summarize the last 3 commits of the LangChain4j GitHub repository");
        System.out.println("RESPONSE: " + response);
    } finally {
        mcpClient.close();
    }
}
```

!!! note
    并非所有 LLM 对工具的支持程度都一样好。
    理解、选择和正确使用工具的能力在很大程度上取决于具体的模型及其能力。
    有些模型可能完全不支持工具，而有些模型可能需要精心设计的提示词工程
    或额外的系统指令。

> **注意**：本示例使用 Docker，因此会执行位于 `/usr/local/bin/docker` 的 Docker 命令（请根据你的操作系统更改路径）。如果你想改用 Podman，请相应地更改命令。

## 运行代码

要运行该示例，请确保 Docker 在你的系统上已启动并正在运行。
此外，请将你的 OpenAI API 密钥设置在环境变量 `OPENAI_API_KEY` 中。

然后运行 Java 应用程序。你应当收到一个响应，总结 LangChain4j GitHub 仓库的最后 3 个提交，例如：

```
Here are the summaries of the last three commits in the LangChain4j GitHub repository:

1. **Commit [36951f9](https://github.com/langchain4j/langchain4j/commit/36951f9649c1beacd8b9fc2d910a2e23223e0d93)** (Date: 2025-02-05)
   - **Author:** Dmytro Liubarskyi
   - **Message:** Updated to `upload-pages-artifact@v3`.
   - **Details:** This commit updates the GitHub Action used for uploading pages artifacts to version 3.

2. **Commit [6fcd19f](https://github.com/langchain4j/langchain4j/commit/6fcd19f50c8393729a0878d6125b0bb1967ac055)** (Date: 2025-02-05)
   - **Author:** Dmytro Liubarskyi
   - **Message:** Updated to `checkout@v4`, `deploy-pages@v4`, and `upload-pages-artifact@v4`.
   - **Details:** This commit updates multiple GitHub Actions to their version 4.

3. **Commit [2e74049](https://github.com/langchain4j/langchain4j/commit/2e740495d2aa0f16ef1c05cfcc76f91aef6f6599)** (Date: 2025-02-05)
   - **Author:** Dmytro Liubarskyi
   - **Message:** Updated to `setup-node@v4` and `configure-pages@v4`.
   - **Details:** This commit updates the `setup-node` and `configure-pages` GitHub Actions to version 4.

All commits were made by the same author, Dmytro Liubarskyi, on the same day, focusing on updating various GitHub Actions to newer versions.
```

## 在无 AI 服务的情况下使用 MCP

前面的示例展示了如何将 MCP 与高级 AI 服务 API 配合使用。但是，也可以通过低级 API 使用 MCP。
你可以手动使用所构建的 `DefaultMcpClient` 实例对服务器执行命令。一些示例：

```java
// obtain a list of tools from the server
List<ToolSpecification> toolSpecifications = mcpClient.listTools();

// build and execute a ChatRequest that has access to the MCP tools
ChatRequest chatRequest = ChatRequest.builder()
        .messages(UserMessage.from("What will the weather be like in London tomorrow?"))
        .toolSpecifications(toolSpecifications)
        .build();
ChatResponse response = chatModel.chat(chatRequest);
AiMessage aiMessage = response.aiMessage();

// if the LLM requested to invoke a tool, forward it to the MCP server
if(aiMessage.hasToolExecutionRequests()) {
    for (ToolExecutionRequest req : aiMessage.toolExecutionRequests()) {
        String resultString = mcpClient.executeTool(req);
        // prepare the result for adding it to the memory for the next ChatRequest...
        ToolExecutionResultMessage resultMessage = ToolExecutionResultMessage.from(req.id(), req.name(), resultString);
    }
}
```

如果你想直接使用 MCP 客户端以编程方式执行工具（在对话之外），
你需要手动构建一个 `ToolExecutionRequest` 实例：

```java
// to execute a tool named "tool1" with argument "a=b"
ToolExecutionRequest request = ToolExecutionRequest.builder()
                .name("tool1")
                .arguments("{\"a\": \"b\"}")
                .build();
String toolResult = mcpClient.executeTool(request);
```

## 关于工具缓存的说明

`DefaultMcpClient` 维护着一个 MCP 工具的内部缓存。一旦获取过，
除非服务器发送通知表明列表已更新，否则不会再次向 MCP 服务器请求
工具列表。你可以通过调用 `DefaultMcpClient.evictToolListCache()` 手动清除这个缓存。
如果你希望完全禁用缓存，请按以下方式配置客户端：

```java
McpClient mcpClient = new DefaultMcpClient.Builder()
    .key("MyMCPClient")
    .transport(transport)
    .cacheToolList(false)
    .build();
```

## MCP 注册表客户端

LangChain4j 还提供了一个独立的客户端实现，可以与
[MCP 注册表](https://registry.modelcontextprotocol.io/docs#/) 通信。目前，只
实现了只读操作（你可以搜索 MCP 服务器，但不支持管理和添加服务器
——请使用
[官方工具](https://github.com/modelcontextprotocol/registry/blob/main/docs/guides/publishing/publish-server.md) 来完成这些操作）。

**_警告：_** 发现 MCP 服务器并使用它们（尤其是在本地运行）可能会带来严重的安全风险。在
运行你在公共注册表中找到的任何 MCP 服务器之前，请确保你能够信任它。

注册表客户端
位于 `dev.langchain4j.mcp.registryclient` 包中，可以像这样初始化：

```java
McpRegistryClient client = DefaultMcpRegistryClient.builder()
        .baseUrl("URL-OF-THE-REGISTRY")
        .build();
```

如果没有提供基础 URL，则默认使用官方注册表（https://registry.modelcontextprotocol.io）。
然后，要搜索 MCP 服务器，使用 `registry.listServers(McpServerListRequest)` 方法。`McpServerListRequest`
对象可以使用 `McpServerListRequest.Builder` 类来构建。LangChain4j 中的 Java API
与官方 [MCP 注册表参考](https://registry.modelcontextprotocol.io/docs) 中描述的 MCP 注册表 REST API 紧密对应。
