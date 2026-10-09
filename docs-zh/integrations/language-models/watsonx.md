# watsonx.ai

- [watsonx.ai API Reference](https://cloud.ibm.com/apidocs/watsonx-ai#chat-completions)
- [watsonx.ai Java SDK](https://github.com/IBM/watsonx-ai-java-sdk)
- [watsonx.ai Java SDK documentation](https://ibm.github.io/watsonx-ai-java-sdk/)

本集成构建于 **IBM watsonx.ai Java SDK** 之上。下面描述的每个模型都封装了其一个服务。当你需要了解与 LangChain4j 无关的行为细节——token 缓存、重试、HTTP 客户端调优——时，请参照 [SDK 文档](https://ibm.github.io/watsonx-ai-java-sdk/)。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-watsonx</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 身份验证

Watsonx.ai 通过 `Authenticator` 接口支持身份验证。

这允许你根据部署方式使用不同的身份验证机制：

- **IBMCloudAuthenticator** – 使用 API 密钥对 **IBM Cloud** 进行身份验证。这是最简单的方式，当你提供 `apiKey(...)` 构建器方法时使用它。
- **CP4DAuthenticator** – 对 **Cloud Pak for Data** 部署进行身份验证。
- **自定义身份验证器** – 可以使用 `Authenticator` 接口的任何实现。

`WatsonxChatModel`、`WatsonxStreamingChatModel` 以及其他服务的构建器既可以接受 `.apiKey(...)` 快捷方式，也可以通过 `.authenticator(...)` 接受一个完整的 `Authenticator` 实例。

token 的缓存和续期是透明处理的。token 会在第一次请求时获取并缓存，并在过期前刷新，因此你无需管理其生命周期。将同一个 `Authenticator` 实例传递给多个模型可以让它们共享一个已缓存的 token。有关身份验证器的完整列表及其参数，请参阅 [SDK 身份验证指南](https://ibm.github.io/watsonx-ai-java-sdk/authentication)。

### 示例
```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.watsonx.WatsonxChatModel;
import com.ibm.watsonx.ai.core.auth.cp4d.CP4DAuthenticator;
import com.ibm.watsonx.ai.core.auth.cp4d.AuthMode;
import com.ibm.watsonx.ai.CloudRegion;

WatsonxChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key") // Simple IBM Cloud authentication
    .projectId("your-project-id")
    .modelName("ibm/granite-4-h-small")
    .build();

WatsonxChatModel.builder()
    .baseUrl("https://my-instance-url")
    .authenticator( // For Cloud Pak for Data deployments
        CP4DAuthenticator.builder()
            .baseUrl("https://my-instance-url")
            .username("username")
            .apiKey("api-key")
            .authMode(AuthMode.LEGACY)
            .build()
    )
    .projectId("my-project-id")
    .modelName("ibm/granite-4-h-small")
    .build();
```

### 自定义 HttpClient 和 SSL 配置

#### 使用自定义 HttpClient

所有服务和身份验证器都支持通过构建器模式使用自定义 `HttpClient` 实例。这在 Cloud Pak for Data 环境中尤其有用，你可能需要在那里配置自定义的 TLS/SSL 设置、代理配置或其他 HTTP 客户端属性。

```java
HttpClient httpClient = HttpClient.newBuilder()
    .sslContext(createCustomSSLContext())
    .executor(ExecutorProvider.ioExecutor())
    .build();

EmbeddingModel embeddingModel = WatsonxEmbeddingModel.builder()
    .baseUrl("https://my-instance-url")
    .modelName("ibm/granite-embedding-278m-multilingual")
    .projectId("project-id")
    .httpClient(httpClient) // Custom HttpClient
    .authenticator(
        CP4DAuthenticator.builder()
            .baseUrl("https://my-instance-url")
            .username("username")
            .apiKey("api-key")
            .httpClient(httpClient) // Custom HttpClient
            .build()
    )
    .build();
```

> **注意：** 在 Cloud Pak for Data 中使用自定义 `HttpClient` 时，请务必在构建器和身份验证器构建器上都进行设置，以确保所有请求具有一致的 HTTP 行为。

> 🔗 [HTTP 客户端的 SDK 指南](https://ibm.github.io/watsonx-ai-java-sdk/advanced/http-client)，包括如何从私有信任库构建 `SSLContext`。

#### 禁用 SSL 验证

如果你只需要禁用 SSL 证书验证，可以使用 `verifySsl(false)` 选项，而不是提供自定义的 `HttpClient`：

```java
EmbeddingModel embeddingModel = WatsonxEmbeddingModel.builder()
    .baseUrl("https://my-instance-url")
    .modelName("ibm/granite-embedding-278m-multilingual")
    .projectId("project-id")
    .verifySsl(false) // Disable SSL verification
    .authenticator(
        CP4DAuthenticator.builder()
            .baseUrl("https://my-instance-url")
            .username("username")
            .apiKey("api-key")
            .verifySsl(false) // Disable SSL verification
            .build()
    )
    .build();
```

### 如何创建 IBM Cloud API 密钥

你可以点击 **Create +**，在 [https://cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) 创建 API 密钥。

### 如何查找你的项目 ID

1. 访问 [https://dataplatform.cloud.ibm.com/projects/?context=wx](https://dataplatform.cloud.ibm.com/projects/?context=wx)
2. 打开你的项目
3. 前往 **Manage** 标签页
4. 从 **Details** 部分复制 **Project ID**

## WatsonxChatModel

`WatsonxChatModel` 类允许你创建一个完全封装在 LangChain4j 内部的 `ChatModel` 接口实例。
创建实例时，你必须指定以下必需参数：

- `baseUrl(...)` – IBM Cloud 端点 URL（可为 `String`、`URI` 或 `CloudRegion`）
- `apiKey(...)` – IBM Cloud IAM API 密钥
- `projectId(...)` – IBM Cloud 项目 ID（或使用 `spaceId(...)`）
- `modelName(...)` – 用于推理的基础模型 ID

> 你可以使用 `.apiKey(...)` 进行身份验证，也可以通过 `.authenticator(...)` 使用完整的 `Authenticator` 实例。

> 要调用你按需部署的模型，请改用 [`WatsonxDeploymentChatModel`](#已部署的模型按需部署)。

### 示例

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.watsonx.WatsonxChatModel;
import com.ibm.watsonx.ai.CloudRegion;

ChatModel chatModel = WatsonxChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-4-h-small")
    .temperature(0.7)
    .maxOutputTokens(0)
    .build();

String answer = chatModel.chat("Hello from watsonx.ai");
System.out.println(answer);
```

> 🔗 [查看可用模型](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html?context=wx#ibm-provided)

## WatsonxStreamingChatModel

`WatsonxStreamingChatModel` 为 IBM watsonx.ai 在 LangChain4j 中提供流式支持。当你希望在 token 生成的同时处理它们时，它会很有用，非常适合聊天 UI 或长文本生成等实时应用。

流式模式使用与非流式的 [`WatsonxChatModel`](#watsonxchatmodel) 相同的配置结构和参数。主要区别在于，响应通过一个处理器接口增量地传递。

> 要调用你按需部署的模型，请改用 [`WatsonxDeploymentStreamingChatModel`](#已部署的模型按需部署)。

### 示例

```java
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.StreamingChatResponseHandler;
import dev.langchain4j.model.chat.ChatResponse;
import dev.langchain4j.model.watsonx.WatsonxStreamingChatModel;
import com.ibm.watsonx.ai.CloudRegion;

StreamingChatModel model = WatsonxStreamingChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-4-h-small")
    .maxOutputTokens(0)
    .build();

model.chat("What is the capital of Italy?", new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.println("Partial: " + partialResponse);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        System.out.println("Complete: " + completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

> 🔗 [查看可用模型](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models.html?context=wx#ibm-provided)

## 已部署的模型（按需部署）

IBM watsonx.ai 允许你将基础模型按需部署在专用硬件上，供你的组织独占使用。这些已部署的模型通过其 `deploymentId` 寻址，由一个与基础模型目录不同的 watsonx.ai 端点提供服务，因此 LangChain4j 通过自己的一对类来暴露它们：`WatsonxDeploymentChatModel` 和 `WatsonxDeploymentStreamingChatModel`。

创建实例时，你必须指定：

- `baseUrl(...)` – IBM Cloud 端点 URL（可为 `String`、`URI` 或 `CloudRegion`）
- `apiKey(...)` – IBM Cloud IAM API 密钥
- `deploymentId(...)` – 按需部署的模型的部署 ID

一个部署已经指向某个项目或空间内的特定模型，因此这些构建器既不提供 `modelName(...)`，也不提供 `projectId(...)`/`spaceId(...)`。其他所有生成参数（`temperature`、`maxOutputTokens`、`thinking`、工具、`responseFormat` 等）的工作方式与 `WatsonxChatModel` 上完全相同。

> **注意：** `deploymentId` 是一个在模型构建时固定的连接级设置——它选择部署端点，因此不能通过 `WatsonxChatRequestParameters` 按请求覆盖。

### WatsonxDeploymentChatModel

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.watsonx.WatsonxDeploymentChatModel;
import com.ibm.watsonx.ai.CloudRegion;

ChatModel chatModel = WatsonxDeploymentChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .deploymentId("your-deployment-id")
    .temperature(0.7)
    .maxOutputTokens(0)
    .build();

String answer = chatModel.chat("Hello from watsonx.ai");
System.out.println(answer);
```

### WatsonxDeploymentStreamingChatModel

```java
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.StreamingChatResponseHandler;
import dev.langchain4j.model.chat.ChatResponse;
import dev.langchain4j.model.watsonx.WatsonxDeploymentStreamingChatModel;
import com.ibm.watsonx.ai.CloudRegion;

StreamingChatModel model = WatsonxDeploymentStreamingChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .deploymentId("your-deployment-id")
    .maxOutputTokens(0)
    .build();

model.chat("What is the capital of Italy?", new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.println("Partial: " + partialResponse);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        System.out.println("Complete: " + completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

> 🔗 [了解更多关于按需部署模型的内容](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/deploy-on-demand-overview.html?context=wx&audience=wdp)

## 模型网关

IBM watsonx.ai 的 **Model Gateway（模型网关）** 暴露了一个 OpenAI 兼容的聊天端点，它可以将请求路由到由多个提供商（例如 OpenAI、Anthropic 或你注册的第三方提供商）托管的模型，背后只有一个 watsonx.ai 入口。LangChain4j 通过 `WatsonxGatewayChatModel` 和 `WatsonxGatewayStreamingChatModel` 与之集成。

> **注意：** 网关在使用前必须由管理员进行配置——你传入的每个 `modelName` 必须是已在网关中注册的 id。

### WatsonxGatewayChatModel

创建实例时，指定：

- `baseUrl(...)` – IBM Cloud 端点 URL（可为 `String`、`URI` 或 `CloudRegion`）
- `apiKey(...)` – IBM Cloud IAM API 密钥（或经由 `.authenticator(...)` 的完整 `Authenticator`）
- `modelName(...)` – 在网关中注册的 OpenAI 风格模型 id

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.watsonx.WatsonxGatewayChatModel;
import com.ibm.watsonx.ai.CloudRegion;

ChatModel chatModel = WatsonxGatewayChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("gpt-4o")
    .temperature(0.7)
    .build();

String answer = chatModel.chat("Hello from the watsonx.ai Model Gateway");
System.out.println(answer);
```

### WatsonxGatewayStreamingChatModel

`WatsonxGatewayStreamingChatModel` 为网关提供流式支持。它使用与 `WatsonxGatewayChatModel` 相同的配置。
响应通过处理器增量传递。

```java
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.chat.StreamingChatResponseHandler;
import dev.langchain4j.model.chat.ChatResponse;
import dev.langchain4j.model.watsonx.WatsonxGatewayStreamingChatModel;
import com.ibm.watsonx.ai.CloudRegion;

StreamingChatModel model = WatsonxGatewayStreamingChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("gpt-4o")
    .build();

model.chat("What is the capital of Italy?", new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.println("Partial: " + partialResponse);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        System.out.println("Complete: " + completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

### 仅网关支持的参数

每个 watsonx.ai 聊天服务都有自己独立的 `ChatRequestParameters` 实现，只暴露该服务接受的参数，
其他一概不暴露：

| 类 | 使用者 |
|---|---|
| `WatsonxChatRequestParameters` | `WatsonxChatModel`、`WatsonxStreamingChatModel`、`WatsonxDeploymentChatModel`、`WatsonxDeploymentStreamingChatModel` |
| `WatsonxGatewayChatRequestParameters` | `WatsonxGatewayChatModel`、`WatsonxGatewayStreamingChatModel` |

这两个类是 `ChatRequestParameters` 相互独立的实现。每个类都精确声明了其服务
支持的内容，因此任何一类都不知道另一类的参数。将一个服务的参数传递给另一个服务——
无论是通过构建器上的 `defaultRequestParameters(...)`，还是通过单个 `ChatRequest` 的参数——
因此只能贡献 `DefaultChatRequestParameters` 所覆盖的部分（`modelName`、`temperature`、`topP`、
`maxOutputTokens` 等），而它们携带的所有 watsonx.ai 特有参数都会被忽略。请使用与你正在调用的
模型相匹配的类。

除通用的聊天参数外，`WatsonxGatewayChatRequestParameters` 还暴露了网关特有的参数：

| 参数 | 描述 |
|---|---|
| `serviceTier(...)` | 服务层级，为 `AUTO`、`DEFAULT`、`FLEX` 或 `PRIORITY` 之一。 |
| `reasoningEffort(...)` | 推理模型的推理努力程度，为 `LOW`、`MEDIUM` 或 `HIGH` 之一。 |
| `router(...)` / `cache(...)` | 路由器配置，包括提示词 `Cache`。 |
| `modalities(...)` | 输出模态（例如 `["text"]`）。 |
| `store(...)` | 提供商是否应持久化请求/响应。 |
| `parallelToolCalls(...)` | 启用/禁用并行工具调用。 |
| `user(...)` | 转发给提供商的最终用户标识符。 |
| `metadata(...)` | 转发给提供商的自由格式元数据映射。 |
| `logitBias(...)`、`logprobs(...)`、`topLogprobs(...)`、`seed(...)` | OpenAI 兼容的采样控制。 |

```java
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.request.ChatRequest;
import dev.langchain4j.model.watsonx.WatsonxGatewayChatRequestParameters;
import com.ibm.watsonx.ai.gateway.chat.ModelGatewayParameters.ReasoningEffort;
import com.ibm.watsonx.ai.gateway.chat.ModelGatewayParameters.ServiceTier;

ChatRequest request = ChatRequest.builder()
    .messages(UserMessage.from("Solve this step by step."))
    .parameters(
        WatsonxGatewayChatRequestParameters.builder()
            .serviceTier(ServiceTier.FLEX)
            .reasoningEffort(ReasoningEffort.HIGH)
            .build()
    ).build();

String answer = chatModel.chat(request).aiMessage().text();
```

### 响应元数据

每个 watsonx.ai 聊天响应都携带一个 `WatsonxChatResponseMetadata`。它的三个字段仅由
Model Gateway 填充，对于其他服务则保持为 `null`：

```java
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.watsonx.WatsonxChatResponseMetadata;

ChatResponse response = chatModel.chat(request);
var metadata = (WatsonxChatResponseMetadata) response.metadata();

metadata.serviceTier();       // service tier that served the request (gateway only)
metadata.systemFingerprint(); // provider system fingerprint (gateway only)
metadata.cached();            // whether the response was served from cache (gateway only)
```

## 内联审核

`WatsonxChatModel` 和 `WatsonxStreamingChatModel` 可以在答案生成的同时，对聊天请求的输入和输出进行筛查，而无需向审核服务发起任何额外调用。筛查通过 `moderations(...)` 构建器方法启用。

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.watsonx.WatsonxChatModel;
import com.ibm.watsonx.ai.CloudRegion;
import com.ibm.watsonx.ai.chat.ChatModeration;

ChatModel chatModel = WatsonxChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-4-h-small")
    .moderations(
        ChatModeration.builder()
            .pii(pii -> pii.input(true).output(true))
            .hap(hap -> hap.output(0.8f))
            .graniteGuardian(guardian -> guardian.input(0.85f))
            .build()
    )
    .build();
```

有三种检测器可用。`pii` 和 `hap` 可以启用在输入上、输出上或两者上，而 `graniteGuardian` 只筛查输入。

| 检测器 | 用途 | 启用方式 |
|---|---|---|
| `pii` | 检测个人数据，例如电话号码、电子邮件和信用卡。 | `.pii(pii -> pii.input(true).output(true))` |
| `hap` | 检测置信度超过阈值的仇恨言论和侮辱性语言。 | `.hap(hap -> hap.input(0.8f).output(0.9f))` |
| `graniteGuardian` | 有害内容通用分类器。 | `.graniteGuardian(guardian -> guardian.input(0.85f))` |

`inputRanges(...)` 将输入的筛查范围缩小到给定的范围，其中起始位置包含在内，结束位置不包含。

```java
import com.ibm.watsonx.ai.chat.ChatModeration.InputRanges;

ChatModeration.builder()
    .pii(pii -> pii.input(true))
    .inputRanges(List.of(InputRanges.of(0, 50), InputRanges.of(100, 150)))
    .build();
```

### 读取匹配结果

匹配结果在响应的 `WatsonxChatResponseMetadata` 上报告。

```java
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.watsonx.WatsonxChatResponseMetadata;

ChatResponse response = chatModel.chat(request);
var metadata = (WatsonxChatResponseMetadata) response.metadata();

metadata.moderations(); // matches keyed by detector name, "pii", "hap" or "granite_guardian"
metadata.detections();  // Granite Guardian detections keyed by position, "input" or "output"
```

当审核被禁用且没有任何检测器匹配时，这两个映射都为 `null`。每个匹配都会说明它来自输入还是输出、检测器给出的分数、已识别的实体类型，以及问题词在文本中的位置。对于 `WatsonxStreamingChatModel`，每个分块的匹配会被合并，并报告在传递给 `onCompleteResponse(...)` 的响应的元数据上。

| 字段 | 类型 | 描述 |
|---|---|---|
| `score()` | `float` | 匹配的置信度。 |
| `input()` | `boolean` | 匹配来自输入时为 `true`，来自输出时为 `false`。 |
| `position()` | `Position` | 匹配在文本中的起始（包含）和结束（不包含）偏移量。 |
| `entity()` | `String` | 已识别实体的类型，例如 `PhoneNumber`。 |
| `word()` | `String` | 匹配到的文本。 |

该服务报告输出的匹配，但从不重写答案，因此文本的脱敏交由调用方完成，调用方可以使用每个匹配的偏移量。每个检测器也接受 `mask(true)`，要求服务移除已检测实体的值，同时聊天服务的答案仍按原样返回。

```java
import com.ibm.watsonx.ai.chat.TextChatResponse.ModerationResult;

static String mask(String text, ModerationResult result) {
    var position = result.position();
    return text.substring(0, position.start())
        + "*".repeat(position.end() - position.start())
        + text.substring(position.end());
}
```

### 输入被检测器拦截

与某个检测器匹配的输入会阻止生成。LangChain4j 将其报告为一个 `ContentFilteredException`，其 cause 是 SDK 抛出的 `ModerationException`，因此触发拦截的每个检测器的匹配仍然可以访问到。

```java
import com.ibm.watsonx.ai.chat.exception.ModerationException;
import dev.langchain4j.exception.ContentFilteredException;

try {
    chatModel.chat(request);
} catch (ContentFilteredException e) {
    var cause = (ModerationException) e.getCause();
    System.out.println(cause.moderations());
}
```

对于 `WatsonxStreamingChatModel`，同一个异常会被传递到 `onError(...)`。

### 对单个请求进行内容审核

`WatsonxChatRequestParameters` 携带相同的设置，其优先级高于在构建器上配置的设置。

```java
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.request.ChatRequest;
import dev.langchain4j.model.watsonx.WatsonxChatRequestParameters;

ChatRequest request = ChatRequest.builder()
    .messages(UserMessage.from("Contact me at john@example.com."))
    .parameters(
        WatsonxChatRequestParameters.builder()
            .moderations(ChatModeration.builder().pii(pii -> pii.output(true)).build())
            .build()
    ).build();
```

> **注：** 内联审核仅适用于基础模型。`WatsonxDeploymentChatModel` 和 `WatsonxDeploymentStreamingChatModel` 会以 `UnsupportedFeatureException` 拒绝它，而 Model Gateway 也不支持它。要在聊天流程之外筛查文本，请使用 [WatsonxModerationModel](#watsonxmoderationmodel)。

> 🔗 [SDK 内容审核](https://ibm.github.io/watsonx-ai-java-sdk/services/chat-service#content-moderation)，查看每个检测器的完整选项列表。

## 工具集成

所有 watsonx.ai 聊天模型——`WatsonxChatModel`、`WatsonxStreamingChatModel`、`WatsonxDeploymentChatModel`、`WatsonxDeploymentStreamingChatModel`、`WatsonxGatewayChatModel` 和 `WatsonxGatewayStreamingChatModel`——都支持 **LangChain4j 工具（Tools）**，允许模型调用带有 `@Tool` 注解的 Java 方法。

下面是一个使用同步模型（`WatsonxChatModel`）的示例，但同样的方法也适用于流式以及部署/网关变体。

```java
static class Tools {

    @Tool
    LocalDate currentDate() {
        return LocalDate.now();
    }

    @Tool
    LocalTime currentTime() {
        return LocalTime.now();
    }
}

interface AiService {
    String chat(String userMessage);
}

ChatModel chatModel = WatsonxChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("mistralai/mistral-small-3-1-24b-instruct-2503")
    .maxOutputTokens(0)
    .build();

AiService aiService = AiServices.builder(AiService.class)
        .chatModel(chatModel)
        .tools(new Tools())
        .build();

String answer = aiService.chat("What is the date today?");
System.out.println(answer);
```

> **注：** 请确保你选择的模型支持工具使用。
---

## 结构化输出

所有 watsonx.ai 聊天模型都可以将响应约束到 JSON Schema。通用的 LangChain4j 文档可在[这里](../../tutorials/structured-outputs.md)找到，而本节介绍 watsonx.ai 特有的行为。

`strictJsonSchema(...)` 构建器方法控制 schema 如何发送给服务，默认为 `true`。在严格模式下，模型必须遵循该 schema，每个属性都标记为 `required`，`additionalProperties` 被设置为 `false`，而未被列入 required 列表的属性会被置为可空。

```java
import static dev.langchain4j.model.chat.Capability.RESPONSE_FORMAT_JSON_SCHEMA;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.watsonx.WatsonxChatModel;
import com.ibm.watsonx.ai.CloudRegion;

ChatModel chatModel = WatsonxChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-4-h-small")
    .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)
    .strictJsonSchema(true) // default value
    .build();
```

> 使用 `strictJsonSchema(false)` 可以将 schema 作为提示而非约束发送。模型仍会尝试生成遵循该 schema 的响应，但当响应偏离它时请求不会失败，required 列表按声明发送，`additionalProperties` 则被省略。当可选字段必须保持可选时，请使用此模式。

> 只有当模型通过 AI 服务使用时，才需要 `supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)`，此时 JSON Schema 是从 AI 服务方法的返回类型生成的。

JSON Schema 的根元素必须是 `JsonObjectSchema` 或 `JsonRawSchema`。任何其他根元素都会导致请求以 `IllegalArgumentException` 失败。

## 启用思考/推理输出

一些基础模型可以在其响应中包含内部*推理*（也称为*思考*）步骤。
具体取决于模型，该推理可能**嵌入在与最终响应相同的文本中**，也可能**单独返回**在来自 `watsonx.ai` 的专用字段中。

要正确地启用并捕获这一行为，你必须根据模型的输出格式配置 `thinking(...)` 构建器方法。
这可确保 LangChain4j 能够从模型输出中自动提取推理内容和响应内容。

有两种主要的配置模式：

- **`ExtractionTags`** → 用于将推理和响应返回在同一个文本块中的模型（例如 **ibm/granite-3-3-8b-instruct**）。
- **`ThinkingEffort`** → 用于已经自动将推理和响应分离的模型（例如 **openai/gpt-oss-120b**）。

> `thinking(...)` 构建器方法可用于 `WatsonxChatModel`、`WatsonxStreamingChatModel`、`WatsonxDeploymentChatModel` 和 `WatsonxDeploymentStreamingChatModel`。Model Gateway 不接受它，因此请改在网关模型上使用 [`reasoningEffort(...)`](#仅网关支持的参数)。

### 同时返回推理与响应的模型

当模型将推理和响应输出在同一个文本字符串中时，使用 **`ExtractionTags`**。
这些标签定义了用于将推理与最终响应分隔开的类 XML 标记。

**示例标签：**

- **推理标签：** `think` - 包含模型的内部推理。
- **响应标签：** `<response>` - 包含面向用户的答案。

#### 行为

- 如果**同时指定两个标签**，它们会被直接用于提取推理和响应片段。
- 如果**只指定推理标签**，该标签之外的所有内容都被视为响应。

#### **ibm/granite-3-3-8b-instruct** 的示例

```java
ChatModel chatModel = WatsonxChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-3-3-8b-instruct")
    .maxOutputTokens(0)
    .thinking(ExtractionTags.of("think", "response"))
    .build();

ChatResponse chatResponse = chatModel.chat(
    UserMessage.userMessage("Why is the sky blue?")
);

AiMessage aiMessage = chatResponse.aiMessage();

System.out.println(aiMessage.thinking());
System.out.println(aiMessage.text());
```

### 分别返回推理与响应的模型

对于已经将推理和响应作为单独字段返回的模型，使用 **`ThinkingEffort`** 来控制模型在生成过程中投入多少推理。
或者，使用布尔标志来启用它。

#### **openai/gpt-oss-120b** 的示例

```java
ChatModel chatModel = WatsonxChatModel.builder()
    .baseUrl(CloudRegion.DALLAS)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("openai/gpt-oss-120b")
    .thinking(ThinkingEffort.HIGH)
    .build();
```

或者

```java
ChatModel chatModel = WatsonxChatModel.builder()
    .baseUrl(CloudRegion.DALLAS)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("openai/gpt-oss-120b")
    .thinking(true)
    .build();
```

### 流式示例

```java
StreamingChatModel model = WatsonxStreamingChatModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-3-3-8b-instruct")
    .thinking(ExtractionTags.of("think", "response"))
    .build();

List<ChatMessage> messages = List.of(
    UserMessage.userMessage("Why is the sky blue?")
);

ChatRequest chatRequest = ChatRequest.builder()
    .messages(messages)
    .build();

model.chat(chatRequest, new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        ...
    }

    @Override
    public void onPartialThinking(PartialThinking partialThinking) {
        ...
    }
});
```

> **注：**
> - 确保所选模型支持推理输出。
> - 对于将推理和响应嵌入单个文本字符串的模型，使用 `ExtractionTags`。
> - 对于已经自动将推理和响应分离的模型，使用 `ThinkingEffort` 或 `thinking(true)`。

## WatsonxModelCatalog

`WatsonxModelCatalog` 提供了一种以编程方式发现和列出 IBM watsonx.ai 上所有可用基础模型的方式。
它实现了 LangChain4j 的 `ModelCatalog` 接口，允许你获取每个模型的详细信息。

### 示例

```java
import dev.langchain4j.model.catalog.ModelCatalog;
import dev.langchain4j.model.catalog.ModelDescription;
import dev.langchain4j.model.watsonx.WatsonxModelCatalog;
import com.ibm.watsonx.ai.CloudRegion;

ModelCatalog modelCatalog = WatsonxModelCatalog.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .build();

var models = modelCatalog.listModels();
```

> 🔗 [SDK 基础模型服务](https://ibm.github.io/watsonx-ai-java-sdk/services/foundation-model-service)

## WatsonxGatewayModelCatalog

`WatsonxGatewayModelCatalog` 是 [Model Gateway](#模型网关) 对应的 `WatsonxModelCatalog`。它列出的不是 watsonx.ai 托管的基础模型，而是配置在网关中的模型，聚合了其中注册的所有提供商。它同样实现了 LangChain4j 的 `ModelCatalog` 接口。

每个返回的 `ModelDescription` 的 `name()` 是应传递给 `WatsonxGatewayChatModel.modelName(...)` 和 `WatsonxGatewayStreamingChatModel.modelName(...)` 的标识符。当网关管理员定义了模型**别名**时，它就是该别名，否则是提供商侧的模型 id。

### 示例

```java
import dev.langchain4j.model.catalog.ModelCatalog;
import dev.langchain4j.model.catalog.ModelDescription;
import dev.langchain4j.model.watsonx.WatsonxGatewayModelCatalog;
import com.ibm.watsonx.ai.CloudRegion;

ModelCatalog modelCatalog = WatsonxGatewayModelCatalog.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .build();

for (ModelDescription model : modelCatalog.listModels()) {
    System.out.println(model.name() + " (" + model.owner() + ")");
}
// → gpt-4o (openai)
// → claude-3-5-sonnet (anthropic)
```

### 网关模型是如何映射的

| `ModelDescription` | 网关字段 | 备注 |
|---|---|---|
| `name()` | `alias`，无别名时为 `id` | 与网关聊天模型一起使用的 id |
| `displayName()` | 与 `name()` 相同 | 网关没有单独的标签 |
| `description()` | `description` | 用户定义的，除非管理员设置了它，否则为 `null` |
| `owner()` | `owned_by` | 提供商，例如 `openai` |
| `createdAt()` | `created` | *网关配置*的 Unix 时间戳，不是模型发布的时间 |
| `type()` | - | 始终为 `ModelType.CHAT`，因为网关不暴露模型能力 |
| `maxInputTokens()` | `metadata.context_window` | 当管理员未配置元数据时为 `null` |
| `maxOutputTokens()` | - | 始终为 `null`，网关不返回它 |

## WatsonxTokenCountEstimator

`WatsonxTokenCountEstimator` 通过调用 watsonx.ai
的分词端点来实现 LangChain4j 的 `TokenCountEstimator` 接口，因此计数来自模型本身的
分词器，而不是本地近似值。
正因如此，`modelName(...)` 是必需的。

### 示例

```java
import dev.langchain4j.model.TokenCountEstimator;
import dev.langchain4j.model.watsonx.WatsonxTokenCountEstimator;
import com.ibm.watsonx.ai.CloudRegion;

TokenCountEstimator tokenCountEstimator = WatsonxTokenCountEstimator.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-4-h-small")
    .build();

int tokenCount = tokenCountEstimator.estimateTokenCountInText("Hello from watsonx.ai");
```

> **注意：** 每次估算都是一次远程调用。`estimateTokenCountInMessage(...)` 还会统计 `AiMessage` 的思考文本和
> 工具执行请求。不支持图像、音频、PDF 和视频内容。

> 🔗 [SDK 分词服务](https://ibm.github.io/watsonx-ai-java-sdk/services/tokenization-service)

## WatsonxModerationModel

`WatsonxModerationModel` 使用 IBM watsonx.ai 提供了 `ModerationModel` 接口的一个 LangChain4j 实现。
它允许你通过**检测器**自动检测和标记文本中的敏感、不安全或违反策略的内容。

可以使用一个或多个**检测器**来识别不同类型的内容，例如：

- **Pii** – 检测个人身份信息（例如电子邮件、电话号码）
- **Hap** – 检测仇恨、辱骂或粗俗言论
- **GraniteGuardian** – 检测有风险或有害的语言

### 示例

```java
ModerationModel model = WatsonxModerationModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .detectors(Hap.ofDefaults(), GraniteGuardian.ofDefaults())
    .build();

Response<Moderation> response = model.moderate("...");
```

### 元数据

每个审核响应都包含一个 `metadata` 映射，提供关于检测结果的额外上下文。

| 键 | 描述 |
|-----|--------------|
| `detection` | 检测器分配的已检测标签或类别 |
| `detection_type` | 触发标记的检测器类型 |
| `start` | 已检测片段的起始字符索引 |
| `end` | 已检测片段的结束字符索引 |
| `score` | 检测的置信度分数 |

这些元数据值可通过 `Response.metadata()` 获取：

```java
Map<String, Object> metadata = response.metadata();
System.out.println("Detection type: " + metadata.get("detection_type"));
System.out.println("Score: " + metadata.get("score"));
```

> 🔗 [SDK 检测服务](https://ibm.github.io/watsonx-ai-java-sdk/services/detection-service)，查看检测器及其
> 选项的完整列表。

## 通过环境变量进行配置

底层 SDK 的内部 HTTP 行为可以通过环境变量定制，无需任何代码改动。
这些设置是可选的，当变量未显式定义时，会使用合理的默认值。

### 重试配置

在发生瞬时故障或身份验证 token 过期时，HTTP 请求会自动重试。
可以使用以下环境变量定制重试行为：

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `WATSONX_RETRY_TOKEN_EXPIRED_MAX_RETRIES` | 身份验证 token 过期（HTTP 401 / 403）时的最大重试次数 | `1` |
| `WATSONX_RETRY_STATUS_CODES_MAX_RETRIES` | 瞬时 HTTP 状态码（`429`、`503`、`504`、`520`）的最大重试次数 | `10` |
| `WATSONX_RETRY_STATUS_CODES_BACKOFF_ENABLED` | 为瞬时重试启用指数退避 | `true` |
| `WATSONX_RETRY_STATUS_CODES_INITIAL_INTERVAL_MS` | 初始重试间隔（毫秒）（用作指数退避的基数） | `20` |

### HTTP IO 执行器配置

流式响应和 HTTP 响应处理由内部 IO 执行器处理。
默认情况下，Java 21+ 使用虚拟线程，Java 17–20 使用缓存线程池。

可以使用以下环境变量定制该行为：

| 环境变量 | 描述 | 默认值 |
|---------------------|-------------|---------|
| `WATSONX_IO_EXECUTOR_THREADS` | 将 IO 执行器限制为固定大小的线程池，线程数即该值 | _未设置_ |

> 🔗 [SDK 环境变量的完整参考](https://ibm.github.io/watsonx-ai-java-sdk/advanced/environment-variables)

## 错误处理

SDK 抛出的 watsonx.ai 错误会被转换为标准的 LangChain4j 异常，因此你可以像处理
任何其他提供商一样处理它们。映射由 watsonx.ai 返回的错误码驱动：

| watsonx.ai 错误码 | LangChain4j 异常 |
|---|---|
| `authentication_token_expired`、`authorization_rejected` | `AuthenticationException` |
| `invalid_input_argument`、`invalid_request_entity`、`json_type_error`、`json_validation_error` | `InvalidRequestException` |
| `model_not_supported` | `ModelNotFoundException` |
| `token_quota_reached` | `RateLimitException` |
| 其他任何错误码 | `LangChain4jException` |

当响应不携带错误体时，异常改为根据 HTTP 状态码选择。超过其 `timeout(...)` 的请求会被报告为 `TimeoutException`。拒绝回答的模型以及被[内联审核](#内联审核)拦截的输入，会被报告为 `ContentFilteredException`。

```java
try {
    String answer = chatModel.chat("Hello from watsonx.ai");
} catch (RateLimitException e) {
    // token quota reached
} catch (InvalidRequestException e) {
    // a request parameter was rejected by watsonx.ai
}
```

> 🔗 [SDK 异常层次结构](https://ibm.github.io/watsonx-ai-java-sdk/advanced/error-handling)，查看底层的
> `WatsonxException` 及其通过 `getCause()` 可获取的 `statusCode()`、`errorCode()` 和 `traceId()`。

## Quarkus

更多详细信息请参见[这里](https://docs.quarkiverse.io/quarkus-langchain4j/dev/watsonx-chat-model.html)。

## 示例

- [WatsonxChatModelTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxChatModelTest.java)
- [WatsonxChatModelReasoningTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxChatModelReasoningTest.java)
- [WatsonxStreamingChatModelTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxStreamingChatModelTest.java)
- [WatsonxStreamingChatModelReasoningTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxStreamingChatModelReasoningTest.java)
- [WatsonxToolsTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxToolsTest.java)
- [WatsonxTokenCounterEstimatorTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxTokenCounterEstimatorTest.java)
- [WatsonxModerationModelTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxModerationModelTest.java)
