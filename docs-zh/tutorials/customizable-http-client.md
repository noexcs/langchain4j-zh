# 可自定义的 HTTP 客户端

部分 LangChain4j 模块（目前是 OpenAI 和 Ollama）支持自定义用于
调用 LLM 提供商 API 的 HTTP 客户端。

`langchain4j-http-client` 模块实现了一个 `HttpClient` SPI，
那些模块使用它来调用 LLM 提供商的 REST API。
这意味着底层的 HTTP 客户端可以自定义，
并且任何其他的 HTTP 客户端都可以通过实现 `HttpClient` SPI 来集成。

目前，有以下几种开箱即用的实现：
- `langchain4j-http-client-jdk` 模块中的 `JdkHttpClient`。
  当使用受支持的模块（例如 `langchain4j-open-ai`）时，默认使用它。
- `langchain4j-http-client-spring-boot4-restclient`/`langchain4j-http-client-spring-restclient` 模块中的 `SpringRestClient`。
  当使用受支持模块的 Spring Boot starter（例如 `langchain4j-open-ai-spring-boot4-starter`/`langchain4j-open-ai-spring-boot-starter`）时，默认使用它。
- `langchain4j-http-client-apache` 模块中的 `ApacheHttpClient`。
- `langchain4j-http-client-okhttp` 模块中的 `OkHttpClient`。

## 自定义 JDK 的 `HttpClient`

```java
HttpClient.Builder httpClientBuilder = HttpClient.newBuilder()
        .sslContext(...);

JdkHttpClientBuilder jdkHttpClientBuilder = JdkHttpClient.builder()
        .httpClientBuilder(httpClientBuilder);

OpenAiChatModel model = OpenAiChatModel.builder()
        .httpClientBuilder(jdkHttpClientBuilder)
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();
```

!!! note
   `HttpClient` 的实现还可以提供非阻塞的对应方法：用于单个响应的 `executeAsync(...)`，
   以及用于解析后的服务器发送事件的冷 `Flow.Publisher` 的 `stream(...)`。内置的 JDK、OkHttp 和
   Apache 客户端都实现了这两者。
   另请参阅 [非阻塞与响应式](non-blocking.md)。

## 自定义 Spring 的 `RestClient`

```java
RestClient.Builder restClientBuilder = RestClient.builder()
        .requestFactory(new HttpComponentsClientHttpRequestFactory());

SpringRestClientBuilder springRestClientBuilder = SpringRestClient.builder()
        .restClientBuilder(restClientBuilder)
        .streamingRequestExecutor(new VirtualThreadTaskExecutor());

OpenAiChatModel model = OpenAiChatModel.builder()
        .httpClientBuilder(springRestClientBuilder)
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();
```

## 自定义 Apache 的 `HttpClient`

```java
org.apache.hc.client5.http.impl.classic.HttpClientBuilder httpClientBuilder = org.apache.hc.client5.http.impl.classic.HttpClientBuilder.create();

ApacheHttpClientBuilder apacheHttpClientBuilder = ApacheHttpClient.builder()
        .httpClientBuilder(httpClientBuilder);

OpenAiChatModel model = OpenAiChatModel.builder()
        .httpClientBuilder(apacheHttpClientBuilder)
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();
```
