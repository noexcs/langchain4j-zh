# Amazon Bedrock

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-bedrock</artifactId>
    <version>1.22.0</version>
</dependency>
```

## AWS 凭据
要使用 Amazon Bedrock 模型，你需要配置 AWS 凭据。
其中一种选项是设置 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY` 环境变量。更多信息见[这里](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)。或者，在本地设置 `AWS_BEARER_TOKEN_BEDROCK` 环境变量以进行 API 密钥认证。有关 API 密钥的更多细节，请参阅[文档](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)。

## BedrockChatModel
!!! note
    当前实现不支持护栏。

支持的模型及其功能见[这里](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-supported-models-features.html)。

模型 ID 见[这里](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)。

### 配置
```java
ChatModel model = BedrockChatModel.builder()
        .client(BedrockRuntimeClient)
        .region(...)
        .modelId("us.amazon.nova-lite-v1:0")
        .returnThinking(...)
        .sendThinking(...)
        .timeout(...)
        .maxRetries(...)
        .logRequests(...)
        .logResponses(...)
        .listeners(...)
        .defaultRequestParameters(BedrockChatRequestParameters.builder()
                .modelName(...)
                .temperature(...)
                .topP(...)
                .maxOutputTokens(...)
                .stopSequences(...)
                .toolSpecifications(...)
                .toolChoice(...)
                .additionalModelRequestFields(...)
                .additionalModelRequestField(...)
                .enableReasoning(...)
                .promptCaching(...)
                .requestMetadata(Map.of("team", "platform"))
                .build())
        .build();
```

### 示例

- [BedrockChatModelExample](https://github.com/langchain4j/langchain4j-examples/blob/main/bedrock-examples/src/main/java/converse/BedrockChatModelExample.java)

## BedrockStreamingChatModel

!!! note
    当前实现不支持护栏。

支持的模型及其功能见[这里](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference-supported-models-features.html)。

模型 ID 见[这里](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html)。

### 配置
```java
StreamingChatModel model = BedrockStreamingChatModel.builder()
        .client(BedrockRuntimeAsyncClient)
        .region(...)
        .modelId("us.amazon.nova-lite-v1:0")
        .returnThinking(...)
        .sendThinking(...)
        .timeout(...)
        .logRequests(...)
        .logResponses(...)
        .listeners(...)
        .defaultRequestParameters(BedrockChatRequestParameters.builder()
                .modelName(...)
                .temperature(...)
                .topP(...)
                .maxOutputTokens(...)
                .stopSequences(...)
                .toolSpecifications(...)
                .toolChoice(...)
                .additionalModelRequestFields(...)
                .additionalModelRequestField(...)
                .enableReasoning(...)
                .promptCaching(...)
                .requestMetadata(Map.of("team", "platform"))
                .build())
        .build();
```

### 示例

- [BedrockStreamingChatModelExample](https://github.com/langchain4j/langchain4j-examples/blob/main/bedrock-examples/src/main/java/converse/BedrockStreamingChatModelExample.java)


## BedrockBatchChatModel

`BedrockBatchChatModel` 在 Bedrock [批量推理 API](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference.html) 之上实现了核心的 `BatchChatModel` 接口。该接口可异步处理大量聊天请求，对于支持的模型，其价格低于按需推理。关于批量处理在 LangChain4j 中的工作原理，请参阅上文关于批量推理 API 的说明。

请求会作为 JSONL 文件写入 S3，然后提交一个模型调用作业，结果再从 S3 输出位置读回。这需要一个与作业位于同一区域的 S3 存储桶，以及一个 Bedrock 用于读取输入和写入输出的 [服务角色](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-iam-sr.html)。输入和输出文件之后不会被删除，因此会一直保留在存储桶中，直到你将其移除。

!!! note
    Bedrock 批量推理不支持工具调用、结构化输出或提示词缓存，因此指定了工具、JSON 响应格式或缓存点的请求会以 `UnsupportedFeatureException` 被拒绝，指定了某个服务层级或 `BedrockBatchChatModel` 上未配置的模型的请求同样会被拒绝。只有部分模型支持批量推理，请参阅[支持的模型](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-supported.html)。Bedrock 还将每个作业的记录数下限和上限作为 [服务配额](https://docs.aws.amazon.com/bedrock/latest/userguide/quotas.html) 强制执行，并拒绝超出此范围的作业。

### 依赖
`BedrockBatchChatModel` 使用 AWS SDK 的 Amazon Bedrock 和 Amazon S3 客户端，而 `langchain4j-bedrock` 将它们声明为可选依赖。要使用它，请将它们添加到你的项目中：

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>bedrock</artifactId>
</dependency>
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3</artifactId>
</dependency>
```

### 配置
```java
BedrockBatchChatModel model = BedrockBatchChatModel.builder()
        .region(...)
        .modelId("us.anthropic.claude-haiku-4-5-20251001-v1:0")
        .roleArn("arn:aws:iam::123456789012:role/my-bedrock-batch-role")
        .outputS3Uri("s3://my-bucket/batch-output")
        .inputS3Uri(...)             // optional, defaults to outputS3Uri
        .defaultRequestParameters(...)
        .jobTimeout(Duration.ofHours(24))     // between 24 and 168 hours
        .returnThinking(...)
        .sendThinking(...)
        .timeout(...)
        .customHeaders(...)
        .maxRetries(...)
        .logRequests(...)
        .logResponses(...)
        .build();
```

除非向构建器传入 `S3Client` 和 `BedrockClient`，否则模型会自行创建，`close()` 会关闭它所创建的客户端。

### 用法
```java
// Submit a batch of chat requests, at least as many as the minimum number of records per job
List<ChatRequest> requests = ...;
BatchResponse<ChatResponse> submitted = model.submit(new BatchRequest<>(requests));

String batchId = submitted.batchId();

// Poll until the job reaches a terminal state (SUCCEEDED, FAILED, CANCELLED, EXPIRED).
BatchResponse<ChatResponse> batch = model.retrieve(batchId);
while (!batch.state().isTerminal()) {
    Thread.sleep(Duration.ofMinutes(1).toMillis());
    batch = model.retrieve(batchId);
}

for (BatchItemResult<ChatResponse> result : batch.results()) {
    if (result.isSuccess()) {
        System.out.println(result.response().aiMessage().text());
    } else {
        System.out.println("Failed: " + result.error().message());
    }
}
```

结果按提交请求的顺序返回。Bedrock 报告为部分完成的作业其状态为 `SUCCEEDED`，因此请检查每个结果。`model.cancel(batchId)` 会停止一个作业，其已处理的记录的结果仍会返回（并计费）。`model.list(...)` 列出该区域中的每个批量推理作业，包括未通过 LangChain4j 提交的作业。


## 附加模型请求字段

`BedrockChatRequestParameters` 中的字段 `additionalModelRequestFields` 是 `Map<String, Object>`。
如[这里](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_Converse.html#bedrock-runtime_Converse-request-additionalModelRequestFields)所述，
它允许你为某个特定模型添加通用 `InferenceConfiguration` 未涵盖的推理参数。


## 请求元数据

使用 `BedrockChatRequestParameters` 上的 `requestMetadata` 为 Converse 和 ConverseStream 请求添加键值对。
该元数据可用于过滤 Amazon Bedrock 模型调用日志。它可以作为模型的默认请求参数的一部分进行配置，
也可以针对单个请求提供。

```java
BedrockChatRequestParameters parameters = BedrockChatRequestParameters.builder()
        .requestMetadata(Map.of("team", "platform"))
        .build();
```

不要在请求元数据中包含个人身份信息、凭据或其他敏感数据。
更多信息请参阅[按请求的元数据标记](https://docs.aws.amazon.com/bedrock/latest/userguide/cost-mgmt-request-metadata.html)。


## 思考 / 推理

要启用 Claude 思考过程，请调用 `BedrockChatRequestParameters` 上的 `enableReasoning`，并在构建模型时通过
`defaultRequestParameters` 设置：
```java
BedrockChatRequestParameters parameters = BedrockChatRequestParameters.builder()
        .enableReasoning(1024) // token budget
        .build();

ChatModel model = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-sonnet-4-20250514-v1:0")
        .defaultRequestParameters(parameters)
        .returnThinking(true)
        .sendThinking(true)
        .build();
```

以下参数也控制思考行为：
- `returnThinking`：控制是否在 `AiMessage.thinking()` 中返回 thinking（如果可用），以及使用 `BedrockStreamingChatModel` 时是否调用 `StreamingChatResponseHandler.onPartialThinking()` 和 `TokenStream.onPartialThinking()` 回调。
默认禁用。如果启用，thinking 签名也会被存储在 `AiMessage.attributes()` 中并返回。
- `sendThinking`：控制是否在后续请求中将存储在 `AiMessage` 中的 thinking 和签名发送给 LLM。
默认启用。

## 提示词缓存

AWS Bedrock 支持提示词缓存，以在使用相似提示词进行重复 API 调用时提升性能并降低成本。此功能可将缓存内容的延迟降低最多 85%，成本降低最多 90%。

### 工作原理

提示词缓存允许你标记对话中的特定位置进行缓存。当你使用相同的缓存内容进行后续 API 调用时，Bedrock 可以复用已缓存的部分，显著减少处理时间和成本。缓存的 TTL（Time To Live）为 5 分钟，每次缓存命中时都会重置。

### 支持的模型

以下模型支持提示词缓存：
- Claude Opus 4.5
- Claude Opus 4.1
- Claude Opus 4
- Claude Sonnet 4.5
- Claude Haiku 4.5
- Claude Sonnet 4
- Claude 3.7 Sonnet
- Claude 3.5 Sonnet
- Claude 3.5 Haiku
- Amazon Nova 模型

### 配置

要启用提示词缓存，请在 `BedrockChatRequestParameters` 中使用 `promptCaching()` 方法：

```java
import dev.langchain4j.model.bedrock.BedrockChatRequestParameters;
import dev.langchain4j.model.bedrock.BedrockCachePointPlacement;

BedrockChatRequestParameters params = BedrockChatRequestParameters.builder()
        .promptCaching(BedrockCachePointPlacement.AFTER_SYSTEM)
        .temperature(0.7)
        .maxOutputTokens(500)
        .build();

ChatModel model = BedrockChatModel.builder()
        .modelId("us.amazon.nova-micro-v1:0")
        .region(Region.US_EAST_1)
        .defaultRequestParameters(params)
        .build();
```

### 缓存点位置选项

`BedrockCachePointPlacement` 枚举提供了三个选项，用于决定在对话中的哪个位置放置缓存点：

- **`AFTER_SYSTEM`**：将缓存点放置在系统消息之后。当你有一个希望在多个对话中复用的一致系统提示词时，这是理想选择。
- **`AFTER_USER_MESSAGE`**：将缓存点放置在用户消息之后。当你有一个保持不变的标准化用户提示词或上下文时非常有用。
- **`AFTER_TOOLS`**：将缓存点放置在工具定义之后。当你有一组想要缓存的一致工具时，这非常有益。

### 示例

#### 使用系统消息缓存的基本用法

```java
// Configure prompt caching to cache after system message
BedrockChatRequestParameters params = BedrockChatRequestParameters.builder()
        .promptCaching(BedrockCachePointPlacement.AFTER_SYSTEM)
        .build();

ChatModel model = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-sonnet-4-6")
        .defaultRequestParameters(params)
        .build();

// First request - establishes the cache
ChatRequest request1 = ChatRequest.builder()
        .messages(Arrays.asList(
                SystemMessage.from("You are a helpful coding assistant with expertise in Java."),
                UserMessage.from("What is dependency injection?")
        ))
        .build();

ChatResponse response1 = model.chat(request1);

// Second request - benefits from cached system message
ChatRequest request2 = ChatRequest.builder()
        .messages(Arrays.asList(
                SystemMessage.from("You are a helpful coding assistant with expertise in Java."),
                UserMessage.from("What is the singleton pattern?")
        ))
        .build();

ChatResponse response2 = model.chat(request2); // Faster response due to caching
```

#### 与其他功能结合使用

提示词缓存可以与其他 Bedrock 功能（如推理）结合使用：

```java
BedrockChatRequestParameters params = BedrockChatRequestParameters.builder()
        .promptCaching(BedrockCachePointPlacement.AFTER_SYSTEM)
        .enableReasoning(1000)  // Enable reasoning with 1000 token budget
        .temperature(0.3)
        .maxOutputTokens(2000)
        .build();

ChatModel model = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-sonnet-4-6")
        .defaultRequestParameters(params)
        .build();
```

### 最佳实践

1. **缓存稳定内容**：对不经常变化的内容使用缓存，例如系统提示词、工具定义或常见上下文。
2. **选择合适的放置位置**：
   - 当你的系统提示词在各对话中保持一致时，使用 `AFTER_SYSTEM`
   - 当你有一套稳定的工具定义时，使用 `AFTER_TOOLS`
   - 对于用户上下文重复出现的场景，使用 `AFTER_USER_MESSAGE`
3. **监控缓存命中**：5 分钟 TTL 在每次缓存命中时重置，因此使用相同缓存内容的频繁请求会保持缓存有效。
4. **成本优化**：缓存对于被重复使用的长系统提示词或工具定义尤其有益。

### 其他资源

- [AWS Bedrock 提示词缓存文档](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html)
