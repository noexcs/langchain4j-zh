# ZhiPu AI

[ZhiPu AI](https://www.zhipuai.cn/) 是一个提供模型服务的平台，包括文本生成、文本嵌入、
图像生成等。更多详细信息请参阅 [ZhiPu AI 开放平台](https://open.bigmodel.cn/)。
LangChain4j 通过使用 [HTTP 端点](https://bigmodel.cn/dev/api/normal-model/glm-4) 与 ZhiPu AI 集成。我们正在
考虑将其从 HTTP 端点迁移到官方 SDK，感谢任何帮助！

## Maven 依赖

你可以在纯 Java 或 Spring Boot 应用程序中结合 LangChain4j 使用 ZhiPu AI。

### 纯 Java

!!! note
    自 `1.0.0-alpha1` 起，`langchain4j-zhipu-ai` 已迁移至 `langchain4j-community` 并重命名为
    `langchain4j-community-zhipu-ai`

`1.0.0-alpha1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-zhipu-ai</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及之后：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-zhipu-ai</artifactId>
    <version>${latest version here}</version>
</dependency>
```

或者，你可以使用 BOM 来一致地管理依赖：

```xml

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>dev.langchain4j</groupId>
            <artifactId>langchain4j-community-bom</artifactId>
            <version>${latest version here}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

## 可配置参数

### `ZhipuAiChatModel`

初始化 `ZhipuAiChatModel` 时，它可以配置以下参数：

| Property       | Description                                                                                                                                          | Default Value             |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------|
| baseUrl        | 要连接到的 URL。你可以使用 HTTP 或 websocket 连接到 DashScope                                                                                                                                  | https://open.bigmodel.cn/ |
| apiKey         | API 密钥                                                                                                                                                                                     |                           |
| model          | 要使用的模型。                                                                                                                                                                               | glm-4-flash               |
| topP           | 内核采样的概率阈值，控制模型生成文本的多样性。`top_p` 越高，生成的文本越多样，反之亦然。取值范围：(0, 1.0]。我们通常建议调整此项或 temperature，但不要同时调整两者。 |                           |
| maxRetries     | 请求的最大重试次数                                                                                                                                                                           | 3                         |
| temperature    | 采样温度，控制模型生成文本的多样性。温度越高，生成的文本越多样，反之亦然。取值范围：[0, 2)                                                                                          | 0.7                       |
| stops          | 通过 stop 参数，当文本即将包含指定字符串或 token_id 时，模型会自动停止生成文本。                                                                                                         |                           |
| maxToken       | 本次请求返回的最大 token 数。                                                                                                                                                                | 512                       |
| listeners      | 用于监听请求、响应和错误的监听器。                                                                                                                                                           |                           |
| callTimeout    | 请求的 OKHttp 超时配置                                                                                                                                                                       |                           |
| connectTimeout | 请求的 OKHttp 超时配置                                                                                                                                                                       |                           |
| writeTimeout   | 请求的 OKHttp 超时配置                                                                                                                                                                       |                           |
| readTimeout    | 请求的 OKHttp 超时配置                                                                                                                                                                       |                           |
| logRequests    | 是否记录请求日志                                                                                                                                                                             | false                     |
| logResponses   | 是否记录响应日志                                                                                                                                                                             | false                     |
| doSample       | 是否使用采样。设置为 `false` 时，模型将使用贪心解码                                                                                                                                          |                           |
| toolStream     | 是否启用部分工具流式传输。设置为 `true` 时，工具调用可以增量流式传输                                                                                                                       | false                     |

### `ZhipuAiChatRequestParameters`

`ZhipuAiChatRequestParameters` 可用于在发送聊天请求时配置额外参数：

| Property   | Description                                                                                             | Default Value |
|------------|---------------------------------------------------------------------------------------------------------|---------------|
| doSample   | 是否使用采样。设置为 `false` 时，模型将使用贪心解码                                                    |               |
| toolStream | 是否启用部分工具流式传输。设置为 `true` 时，工具调用可以增量流式传输                                    | false         |
| thinking   | 推理模式的配置。`type` 指定推理类型，`clearThinking` 控制在响应中是否显示内部思考过程                   |               |

### `ZhipuAiStreamingChatModel`

与 `ZhipuAiChatModel` 相同，除了 `maxRetries`。

## 示例

### 纯 Java

你可以使用以下代码初始化 `ZhipuAiChatModel`：

```java
ChatModel model = ZhipuAiChatModel.builder()
        .apiKey("You API key here")
        .callTimeout(Duration.ofSeconds(60))
        .connectTimeout(Duration.ofSeconds(60))
        .writeTimeout(Duration.ofSeconds(60))
        .readTimeout(Duration.ofSeconds(60))
        .build();
```

或者针对其他参数进行更多自定义：

```java
ChatModel model = ZhipuAiChatModel.builder()
        .apiKey("You API key here")
        .model("glm-4")
        .temperature(0.6)
        .maxToken(1024)
        .maxRetries(2)
        .callTimeout(Duration.ofSeconds(60))
        .connectTimeout(Duration.ofSeconds(60))
        .writeTimeout(Duration.ofSeconds(60))
        .readTimeout(Duration.ofSeconds(60))
        .build();
```

### 推理

你可以启用推理模式，以获取模型内部的思考过程：

```java
ChatModel model = ZhipuAiChatModel.builder()
        .apiKey("You API key here")
        .model(ChatCompletionModel.GLM_4_7)  // Use GLM-4-5 or upper model for reasoning support
        .build();

ChatResponse response = model.chat(
        ChatRequest.builder()
                .messages(UserMessage.from("What is the capital of Germany?"))
                .parameters(ZhipuAiChatRequestParameters.builder()
                        .thinking(Thinking.builder()
                                .type("reasoning")
                                .clearThinking(true)
                                .build())
                        .build())
                .build());

AiMessage aiMessage = response.aiMessage();
System.out.println("Answer: "+aiMessage.text());
System.out.println("Thinking: "+aiMessage.thinking());
```

### 部分工具调用（流式）

你可以使用 `toolStream` 增量流式传输部分工具调用：

```java
ZhipuAiStreamingChatModel model = ZhipuAiStreamingChatModel.builder()
        .apiKey("You API key here")
        .model(ChatCompletionModel.GLM_4_7)
        .build();

ToolSpecification calculator = ToolSpecification.builder()
        .name("calculator")
        .description("returns a sum of two numbers")
        .parameters(JsonObjectSchema.builder()
                .addIntegerProperty("first")
                .addIntegerProperty("second")
                .build())
        .build();

TestStreamingChatResponseHandler handler = new TestStreamingChatResponseHandler() {
    @Override
    public void onPartialToolCall(ToolExecutionRequest partialToolCall) {
        System.out.println("Partial tool call: " + partialToolCall.name() + " - " + partialToolCall.arguments());
    }
};

model.chat(
        ChatRequest.builder()
                .messages(UserMessage.from("2+2=?"))
                .parameters(ZhipuAiChatRequestParameters.builder()
                        .toolSpecifications(calculator)
                        .toolStream(true)
                        .build())
                .build(),
        handler);
```

### 更多示例

你可以在以下位置查看更多示例：

- [ZhipuAiChatModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-zhipu-ai/src/test/java/dev/langchain4j/community/model/zhipu/ZhipuAiChatModelIT.java)
- [ZhipuAiStreamingChatModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-zhipu-ai/src/test/java/dev/langchain4j/community/model/zhipu/ZhipuAiStreamingChatModelIT.java)
- [ZhipuAiChatModelReasoningIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-zhipu-ai/src/test/java/dev/langchain4j/community/model/zhipu/ZhipuAiChatModelReasoningIT.java)
- [ZhipuAiStreamingChatModelReasoningIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-zhipu-ai/src/test/java/dev/langchain4j/community/model/zhipu/ZhipuAiStreamingChatModelReasoningIT.java)
- [ZhipuAiStreamingPartialToolCallIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-zhipu-ai/src/test/java/dev/langchain4j/community/model/zhipu/ZhipuAiStreamingPartialToolCallIT.java)
