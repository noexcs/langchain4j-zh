# watsonx.ai

- [watsonx.ai API 参考](https://cloud.ibm.com/apidocs/watsonx-ai#text-rerank)
- [watsonx.ai Java SDK](https://github.com/IBM/watsonx-ai-java-sdk)
- [watsonx.ai Java SDK 文档](https://ibm.github.io/watsonx-ai-java-sdk/services/rerank-service)

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

这允许你根据不同的部署环境使用不同的身份验证机制：

- **IBMCloudAuthenticator** – 使用 API 密钥与 **IBM Cloud** 进行身份验证。这是最简单的方式，在你提供 `apiKey(...)` 构建器方法时使用。
- **CP4DAuthenticator** – 与 **Cloud Pak for Data** 部署进行身份验证。
- **自定义身份验证器** – 可以使用 `Authenticator` 接口的任意实现。

`WatsonxScoringModel` 和其他服务构建器接受通过 `.apiKey(...)` 的快捷方式，或通过 `.authenticator(...)` 传入完整的 `Authenticator` 实例。

### 示例
```java
WatsonxScoringModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key") // Simple IBM Cloud authentication
    .projectId("your-project-id")
    .modelName("cross-encoder/ms-marco-minilm-l-12-v2")
    .build();

WatsonxScoringModel.builder()
    .baseUrl("https://my-instance-url")
    .authenticator( // For Cloud Pak for Data deployments
        CP4DAuthenticator.builder()
            .baseUrl("https://my-instance-url")
            .username("username")
            .apiKey("api-key")
            .build()
    )
    .projectId("my-project-id")
    .modelName("cross-encoder/ms-marco-minilm-l-12-v2")
    .build();
```

### 自定义 HttpClient 和 SSL 配置

#### 使用自定义 HttpClient

所有服务和身份验证器都支持通过构建器模式使用自定义的 `HttpClient` 实例。这在 Cloud Pak for Data 环境中尤为有用，你可能需要在那里配置自定义的 TLS/SSL 设置、代理配置或其他 HTTP 客户端属性。

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

> **注意：** 在 Cloud Pak for Data 中使用自定义 `HttpClient` 时，请确保在-service 构建器和身份验证器构建器上都设置它，以确保所有请求的 HTTP 行为一致。

#### 禁用 SSL 验证

如果你只需要禁用 SSL 证书验证，可以使用 `verifySsl(false)` 选项，而不必提供自定义的 `HttpClient`：

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

你可以在 [https://cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys) 点击 **Create +** 创建 API 密钥。

### 如何找到你的 Project ID

1. 访问 [https://dataplatform.cloud.ibm.com/projects/?context=wx](https://dataplatform.cloud.ibm.com/projects/?context=wx)  
2. 打开你的项目  
3. 进入 **Manage** 选项卡  
4. 从 **Details** 部分复制 **Project ID** 

## WatsonxScoringModel

`WatsonxScoringModel` 提供了使用 IBM watsonx.ai 模型的 `ScoringModel` 的 LangChain4j 实现。

它特别适用于根据文档（或文本片段）与用户查询的相关性对文档列表进行排序。

### 示例

```java
ScoringModel scoringModel = WatsonxScoringModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .projectId("your-project-id")
    .modelName("cross-encoder/ms-marco-minilm-l-12-v2")
    .build();

var scores = scoringModel.scoreAll(
    List.of(
        TextSegment.from("Example_1"),
        TextSegment.from("Example_2")
    ),
    "Hello from watsonx.ai"
);

System.out.println(scores);
```

> 🔗 [查看可用的 rerank 模型 ID](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html?context=wx&audience=wdp#rerank)

## 示例

- [WatsonxScoringModelTest](https://github.com/langchain4j/langchain4j-examples/blob/main/watsonx-ai-examples/src/main/java/WatsonxScoringModelTest.java)
