# watsonx.ai

- [watsonx.ai API 参考](https://cloud.ibm.com/apidocs/watsonx-ai#text-embeddings)
- [watsonx.ai Java SDK](https://github.com/IBM/watsonx-ai-java-sdk)
- [watsonx.ai Java SDK 文档](https://ibm.github.io/watsonx-ai-java-sdk/services/embedding-service)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-watsonx</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 认证

Watsonx.ai 支持通过 `Authenticator` 接口进行认证。

这允许你根据部署环境使用不同的认证机制：

- **IBMCloudAuthenticator** – 使用 API 密钥对 **IBM Cloud** 进行认证。这是最简单的方式，在提供 `apiKey(...)` 构建器方法时使用。
- **CP4DAuthenticator** – 对 **Cloud Pak for Data** 部署进行认证。
- **自定义认证器** – 可以使用 `Authenticator` 接口的任何实现。

`WatsonxEmbeddingModel` 和其他服务的构建器接受通过 `.apiKey(...)` 提供的快捷方式，或通过 `.authenticator(...)` 提供的完整 `Authenticator` 实例。

### 示例
```java
WatsonxEmbeddingModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key") // Simple IBM Cloud authentication
    .projectId("your-project-id")
    .modelName("ibm/granite-embedding-278m-multilingual")
    .build();

WatsonxEmbeddingModel.builder()
    .baseUrl("https://my-instance-url")
    .authenticator( // For Cloud Pak for Data deployments
        CP4DAuthenticator.builder()
            .baseUrl("https://my-instance-url")
            .username("username")
            .apiKey("api-key")
            .build()
    )
    .projectId("my-project-id")
    .modelName("ibm/granite-embedding-278m-multilingual")
    .build();
```

### 自定义 HttpClient 和 SSL 配置

#### 使用自定义 HttpClient

所有服务和认证器都支持通过构建器模式使用自定义 `HttpClient` 实例。这对于可能需要配置自定义 TLS/SSL 设置、代理配置或其他 HTTP 客户端属性的 Cloud Pak for Data 环境特别有用。

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

> **注意：** 在 Cloud Pak for Data 中使用自定义 `HttpClient` 时，请确保同时将其设置在服务构建器和认证器构建器上，以保证所有请求具有一致的 HTTP 行为。

#### 禁用 SSL 验证

如果你只需要禁用 SSL 证书验证，可以使用 `verifySsl(false)` 选项，而无需提供自定义 `HttpClient`：

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

你可以在 [https://cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) 页面点击 **Create +** 来创建 API 密钥。

### 如何查找你的项目 ID

1. 访问 [https://dataplatform.cloud.ibm.com/projects/?context=wx](https://dataplatform.cloud.ibm.com/projects/?context=wx)  
2. 打开你的项目  
3. 切换到 **Manage** 选项卡  
4. 从 **Details** 部分复制 **Project ID** 

## WatsonxEmbeddingModel

`WatsonxEmbeddingModel` 使你能够使用 IBM watsonx.ai 生成嵌入，并将其与 LangChain4j 的基于向量的操作（如搜索、检索增强生成（RAG）和相似性比较）集成。

它实现了 LangChain4j 的 `EmbeddingModel` 接口。

```java
EmbeddingModel embeddingModel = WatsonxEmbeddingModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-embedding-278m-multilingual")
    .build();

System.out.println(embeddingModel.embed("Hello from watsonx.ai"));
```
> 🔗 [查看可用的嵌入模型 ID](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html?context=wx&audience=wdp#embed)

## 监听器

`WatsonxEmbeddingModel` 和 `WatsonxGatewayEmbeddingModel` 都接受一个 `EmbeddingModelListener` 列表，在每次请求之前、每次响应之后以及每次出错时收到通知。

```java
EmbeddingModel embeddingModel = WatsonxEmbeddingModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("ibm/granite-embedding-278m-multilingual")
    .listeners(List.of(new EmbeddingModelListener() {

        @Override
        public void onRequest(EmbeddingModelRequestContext context) {
            System.out.println(context.embeddingRequest().inputs().size() + " input(s)");
        }

        @Override
        public void onResponse(EmbeddingModelResponseContext context) {
            System.out.println(context.embeddingResponse().tokenUsage());
        }

        @Override
        public void onError(EmbeddingModelErrorContext context) {
            System.out.println(context.error().getMessage());
        }
    }))
    .build();
```

## 模型网关

IBM watsonx.ai 的**模型网关**暴露了一个与 OpenAI 兼容的嵌入端点，能够将请求路由到由多个提供商托管的模型（例如 OpenAI，或你自己注册的外部提供商），并通过单一的 watsonx.ai 入口点实现。LangChain4j 通过 `WatsonxGatewayEmbeddingModel` 与其集成。

> **注意：** 网关必须先由管理员配置才能使用。你传入的每个 `modelName` 都必须是已在网关注册的 id。

### WatsonxGatewayEmbeddingModel

创建实例时，请指定：

- `baseUrl(...)` – IBM Cloud 端点 URL（可以是 `String`、`URI` 或 `CloudRegion`）
- `apiKey(...)` – IBM Cloud IAM API 密钥（或通过 `.authenticator(...)` 提供完整的 `Authenticator`）
- `modelName(...)` – 在网关注册的嵌入模型 id，采用 OpenAI 风格的写法

不需要 `projectId` 或 `spaceId`，网关会自行解析模型。

```java
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.watsonx.WatsonxGatewayEmbeddingModel;
import com.ibm.watsonx.ai.CloudRegion;

EmbeddingModel embeddingModel = WatsonxGatewayEmbeddingModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("text-embedding-3-small")
    .build();

System.out.println(embeddingModel.embed("Hello from the watsonx.ai Model Gateway"));
```

### 网关专属参数

网关接受三个 watsonx.ai 嵌入端点没有的参数。它们只需在构建器上设置一次，即适用于每个请求。

| 构建器方法 | 描述 |
|---|---|
| `dimensions(...)` | 返回向量的维度数（仅对支持它的模型有效） |
| `encodingFormat(...)` | 返回向量的传输格式，`FLOAT` 或 `BASE64`。SDK 会为你解码 `BASE64`，因此两种格式得到相同的向量 |
| `user(...)` | 最终用户的标识符，用于滥用监控 |

```java
EmbeddingModel embeddingModel = WatsonxGatewayEmbeddingModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("text-embedding-3-small")
    .dimensions(512)
    .encodingFormat(EncodingFormat.BASE64)
    .build();
```

相同的值也可以通过 `ModelGatewayEmbeddingParameters` 按请求传递。给定参数会替换构建器上设置的参数，而不是与之合并。

```java
WatsonxGatewayEmbeddingModel embeddingModel = WatsonxGatewayEmbeddingModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("text-embedding-3-small")
    .build();

ModelGatewayEmbeddingParameters parameters = ModelGatewayEmbeddingParameters.builder()
    .dimensions(256)
    .build();

Response<List<Embedding>> response = embeddingModel.embedAll(
    List.of(TextSegment.from("Hello"), TextSegment.from("World")), parameters);
```

`dimensions` 是这三个参数中唯一一个同时属于 LangChain4j 嵌入请求 API 的参数，因此可以在不离开 `EmbeddingModel` 接口的情况下按请求设置。请求中的值会覆盖构建器中的值，而 `encodingFormat` 和 `user` 保持构建器上设置的值。

```java
EmbeddingResponse response = embeddingModel.embed(EmbeddingRequest.builder()
    .input("Hello from the watsonx.ai Model Gateway")
    .dimensions(256)
    .build());
```

## 示例

- [WatsonxEmbeddingModelTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxEmbeddingModelTest.java)
