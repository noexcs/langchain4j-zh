# Cohere

!!! note
   这是社区 `Cohere` 聊天模型集成的文档。
   它基于 [Cohere 的 V2 Chat API](https://docs.cohere.com/reference/chat) 实现。

## Maven 依赖

`1.0.0-alpha1` 及更高版本：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-cohere</artifactId>
    <version>${latest version here}</version>
</dependency>
```

或者，你可以使用 BOM 来统一管理依赖：

```xml
<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-community-bom</artifactId>
        <version>${latest version here}</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencyManagement>
```

## 聊天模型支持

你可以使用以下代码实例化 `CohereChatModel`：

```java
ChatModel model = CohereChatModel.builder()
        .apiKey(System.getenv("CO_API_KEY"))
        .modelName("command-r7b-12-2024")
        .logRequests(true)
        .logResponses(true)
        .build();
```

对于流式响应，使用 `CohereStreamingChatModel`：

```java
StreamingChatModel streamingModel = CohereStreamingChatModel.builder()
        .apiKey(System.getenv("CO_API_KEY"))
        .modelName("command-r7b-12-2024")
        .logRequests(true)
        .logResponses(true)
        .build();
```

## 可配置参数

`CohereChatModel` 和 `CohereStreamingChatModel` 接受以下参数：

| 属性 | 描述 | 默认值 |
|----------------------------|-------------------------------------------------------------------------------------------------|----------------------------|
| `baseUrl` | 连接 Cohere API 的 URL。 | https://api.cohere.com/v2/ |
| `apiKey` | API 密钥。 | |
| `modelName` | 要使用的模型，例如 `command-r7b-12-2024` 或 `command-r-plus`。 | |
| `timeout` | 请求的 HTTP 客户端超时。 | |
| `maxRetries` | 每个请求的最大重试次数。仅在 `CohereChatModel` 上可用。 | 3 |
| `temperature` | 采样温度。 | |
| `topP` | 核采样（Nucleus sampling）阈值。 | |
| `topK` | 将每一步的采样限制在可能性最高的 `topK` 个 token 中。 | |
| `frequencyPenalty` | 根据 token 出现频率给出的惩罚。 | |
| `presencePenalty` | 对至少出现过一次的 token 的惩罚。 | |
| `maxTokens` | 此请求返回的最大 token 数。 | |
| `stopSequences` | 使模型停止继续生成文本的序列。 | |
| `toolSpecifications` | 模型可调用的工具（函数）定义。 | |
| `toolChoice` | 控制模型如何选择工具的 `ToolChoice`。可能的值：`AUTO`、`REQUIRED`。 | |
| `responseFormat` | 响应格式，例如 `TEXT` 或 `JSON`。 | |
| `thinkingType` | 启用或禁用具有推理能力模型的扩展思考（extended thinking）的 `CohereThinkingType`。 | |
| `thinkingTokenBudget` | 模型可花费在内部思考上的最大 token 数。 | |
| `safetyMode` | 插入到提示词中的 `CohereSafetyMode`。可能的值：`CONTEXTUAL`、`STRICT`、`OFF`。 | |
| `priority` | Cohere API 负载较高时的请求优先级。 | |
| `seed` | 如果设置，模型将以确定性方式采样 token。 | |
| `logprobs` | 是否在响应中包含 token 的对数概率。 | |
| `strictTools` | 是否强制严格遵循工具定义。 | |
| `defaultRequestParameters` | 应用于每个请求的默认 `ChatRequestParameters`。 | |
| `listeners` | 监听请求、响应和错误的监听器。 | |
| `logRequests` | 是否记录请求。 | `false` |
| `logResponses` | 是否记录响应。 | `false` |

## 响应元数据

你可以访问 Cohere 特有的响应元数据：

```java
ChatResponse response = model.chat(UserMessage.from("Hello"));
CohereChatResponseMetadata metadata = (CohereChatResponseMetadata) response.metadata();

List<CohereLogprobs> logprobs = metadata.logprobs();
CohereBilledUnits billedUnits = metadata.billedUnits();
Integer cachedTokens = metadata.cachedTokens();
```

| 属性 | 描述 |
|----------------|-------------------------------------------------------------------------------------------------|
| `logprobs` | 生成 token 的对数概率。启用 `logprobs` 时返回。 |
| `billedUnits` | 请求的计费明细（输入 token、输出 token、搜索单元、分类）。 |
| `cachedTokens` | 从 Cohere 提示词缓存中提供的 token 数量。 |

## 示例

- [CohereChatModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-cohere/src/test/java/dev/langchain4j/community/model/cohere/common/CohereChatModelIT.java)
- [CohereStreamingChatModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-cohere/src/test/java/dev/langchain4j/community/model/cohere/common/CohereStreamingChatModelIT.java)
