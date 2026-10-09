# Ollama

### 什么是 Ollama？

Ollama 是一款先进的 AI 工具，让用户能够轻松地在本地（CPU 和 GPU 模式）设置并运行大型语言模型。
借助 Ollama，用户可以利用 Llama 2 等强大的语言模型，甚至可以自定义和创建自己的模型。Ollama 将模型权重、
配置和数据打包为一个由 Modelfile 定义的单一软件包。它会优化包括 GPU 使用在内的设置和配置细节。

有关 Ollama 的更多详情，请查看以下内容：

- https://ollama.ai/
- https://github.com/jmorganca/ollama

### 演讲

观看在 [Docker Con 23](https://www.dockercon.com/2023/program) 上的这场演讲：

<iframe width="640" height="480" src="https://www.youtube.com/embed/yPuhGtJT55o" title="Introducing Docker’s Generative AI and Machine Learning Stack (DockerCon 2023)" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

观看 [Code to the Moon](https://www.youtube.com/@codetothemoon) 的这段介绍：

<iframe width="640" height="480" src="https://www.youtube.com/embed/jib1wjgIaa4" title="this open source project has a bright future" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

### 快速上手

要开始使用，请将以下依赖添加到你项目的 `pom.xml` 中：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-ollama</artifactId>
    <version>1.22.0</version>
</dependency>

<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>ollama</artifactId>
    <version>1.19.1</version>
</dependency>
```

当 Ollama 运行在 testcontainers 中时，试试这个简单的聊天示例代码：

```java
import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.model.Image;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.ollama.OllamaChatModel;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.DockerClientFactory;
import org.testcontainers.containers.Container;
import org.testcontainers.ollama.OllamaContainer;
import org.testcontainers.utility.DockerImageName;

import java.io.IOException;
import java.util.List;

public class OllamaChatExample {

  private static final Logger log = LoggerFactory.getLogger(OllamaChatExample.class);

  static final String OLLAMA_IMAGE = "ollama/ollama:latest";
  static final String TINY_DOLPHIN_MODEL = "tinydolphin";
  static final String DOCKER_IMAGE_NAME = "tc-ollama/ollama:latest-tinydolphin";

  public static void main(String[] args) {
    // Create and start the Ollama container
    DockerImageName dockerImageName = DockerImageName.parse(OLLAMA_IMAGE);
    DockerClient dockerClient = DockerClientFactory.instance().client();
    List<Image> images = dockerClient.listImagesCmd().withReferenceFilter(DOCKER_IMAGE_NAME).exec();
    OllamaContainer ollama;
    if (images.isEmpty()) {
        ollama = new OllamaContainer(dockerImageName);
    } else {
        ollama = new OllamaContainer(DockerImageName.parse(DOCKER_IMAGE_NAME).asCompatibleSubstituteFor(OLLAMA_IMAGE));
    }
    ollama.start();

    // Pull the model and create an image based on the selected model.
    try {
        log.info("Start pulling the '{}' model ... would take several minutes ...", TINY_DOLPHIN_MODEL);
        Container.ExecResult r = ollama.execInContainer("ollama", "pull", TINY_DOLPHIN_MODEL);
        log.info("Model pulling competed! {}", r);
    } catch (IOException | InterruptedException e) {
        throw new RuntimeException("Error pulling model", e);
    }
    ollama.commitToImage(DOCKER_IMAGE_NAME);

    // Build the ChatModel
    ChatModel model = OllamaChatModel.builder()
            .baseUrl(ollama.getEndpoint())
            .temperature(0.0)
            .logRequests(true)
            .logResponses(true)
            .modelName(TINY_DOLPHIN_MODEL)
            .build();

    // Example usage
    String answer = model.chat("Provide 3 short bullet points explaining why Java is awesome");
    System.out.println(answer);

    // Stop the Ollama container
    ollama.stop();
  }
}

```

如果你的 Ollama 在本地运行，你还可以尝试以下聊天示例代码：

```java
class OllamaChatLocalModelTest {
  static String MODEL_NAME = "llama3.2"; // try other local ollama model names
  static String BASE_URL = "http://localhost:11434"; // local ollama base url

  public static void main(String[] args) {
      ChatModel model = OllamaChatModel.builder()
              .baseUrl(BASE_URL)
              .modelName(MODEL_NAME)
              .build();
      String answer = model.chat("List top 10 cites in China");
      System.out.println(answer);

      model = OllamaChatModel.builder()
              .baseUrl(BASE_URL)
              .modelName(MODEL_NAME)
              .responseFormat(JSON)
              .build();

      String json = model.chat("List top 10 cites in US");
      System.out.println(json);
    }
}
```

当 Ollama 运行在 testcontainers 中时，试试这个简单的流式聊天示例代码：

```java
import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.model.Image;
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler;
import dev.langchain4j.model.chat.StreamingChatModel;
import dev.langchain4j.model.ollama.OllamaStreamingChatModel;
import dev.langchain4j.model.output.Response;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.DockerClientFactory;
import org.testcontainers.containers.Container;
import org.testcontainers.ollama.OllamaContainer;
import org.testcontainers.utility.DockerImageName;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public class OllamaStreamingChatExample {

  private static final Logger log = LoggerFactory.getLogger(OllamaStreamingChatExample.class);

  static final String OLLAMA_IMAGE = "ollama/ollama:latest";
  static final String TINY_DOLPHIN_MODEL = "tinydolphin";
  static final String DOCKER_IMAGE_NAME = "tc-ollama/ollama:latest-tinydolphin";

  public static void main(String[] args) {
    DockerImageName dockerImageName = DockerImageName.parse(OLLAMA_IMAGE);
    DockerClient dockerClient = DockerClientFactory.instance().client();
    List<Image> images = dockerClient.listImagesCmd().withReferenceFilter(DOCKER_IMAGE_NAME).exec();
    OllamaContainer ollama;
    if (images.isEmpty()) {
        ollama = new OllamaContainer(dockerImageName);
    } else {
        ollama = new OllamaContainer(DockerImageName.parse(DOCKER_IMAGE_NAME).asCompatibleSubstituteFor(OLLAMA_IMAGE));
    }
    ollama.start();
    try {
        log.info("Start pulling the '{}' model ... would take several minutes ...", TINY_DOLPHIN_MODEL);
        Container.ExecResult r = ollama.execInContainer("ollama", "pull", TINY_DOLPHIN_MODEL);
        log.info("Model pulling competed! {}", r);
    } catch (IOException | InterruptedException e) {
        throw new RuntimeException("Error pulling model", e);
    }
    ollama.commitToImage(DOCKER_IMAGE_NAME);

    StreamingChatModel model = OllamaStreamingChatModel.builder()
            .baseUrl(ollama.getEndpoint())
            .temperature(0.0)
            .logRequests(true)
            .logResponses(true)
            .modelName(TINY_DOLPHIN_MODEL)
            .build();

    String userMessage = "Write a 100-word poem about Java and AI";

    CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();
    model.chat(userMessage, new StreamingChatResponseHandler() {

        @Override
        public void onPartialResponse(String partialResponse) {
            System.out.print(partialResponse);
        }

        @Override
        public void onCompleteResponse(ChatResponse completeResponse) {
            futureResponse.complete(completeResponse);
        }

        @Override
        public void onError(Throwable error) {
            futureResponse.completeExceptionally(error);
        }
    });

    futureResponse.join();
    ollama.stop();
  }
}
```

如果你的 Ollama 在本地运行，你还可以尝试以下流式聊天示例代码：
```java
class OllamaStreamingChatLocalModelTest {
  static String MODEL_NAME = "llama3.2"; // try other local ollama model names
  static String BASE_URL = "http://localhost:11434"; // local ollama base url

  public static void main(String[] args) {
      StreamingChatModel model = OllamaStreamingChatModel.builder()
              .baseUrl(BASE_URL)
              .modelName(MODEL_NAME)
              .temperature(0.0)
              .build();
      String userMessage = "Write a 100-word poem about Java and AI";

      CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();
      model.chat(userMessage, new StreamingChatResponseHandler() {

          @Override
          public void onPartialResponse(String partialResponse) {
              System.out.print(partialResponse);
          }

          @Override
          public void onCompleteResponse(ChatResponse completeResponse) {
              futureResponse.complete(completeResponse);
          }

          @Override
          public void onError(Throwable error) {
              futureResponse.completeExceptionally(error);
          }
      });

      futureResponse.join();
  }
}
```

### 参数

`OllamaChatModel` 和 `OllamaStreamingChatModel` 类可以使用构建器模式以以下参数实例化：

| 参数                  | 描述                                                                                                       | 类型                      | 示例                     |
|----------------------------|-------------------------------------------------------------------------------------------------------------------|---------------------------|-----------------------------|
| `httpClientBuilder`        | 参见 [Customizable HTTP Client](https://docs.langchain4j.dev/tutorials/customizable-http-client)                                                                                   | `HttpClientBuilder`       |                             |
| `baseUrl`                  | Ollama 服务器的基础 URL。                                                                                                                                                    | `String`                  | http://localhost:11434      |
| `defaultRequestParameters` |                                                                                                                                                                                   | `ChatRequestParameters`   |                             |
| `modelName`                | 要从 Ollama 服务器使用的模型名称。                                                                                                                                  | `String`                  |                             |
| `temperature`              | 控制生成响应的随机性。较高的值（例如 1.0）会产生更多样的输出，而较低的值（例如 0.2）则产生更具确定性的响应。 | `Double`                  |                             |
| `topK`                     | 指定生成过程中每一步要考虑的最高概率 token 数量。                                                                                   | `Integer`                 |                             |
| `topP`                     | 通过为顶级 token 的累积概率设置阈值，控制生成响应的多样性。                                                            | `Double`                  |                             |
| `mirostat`                 |                                                                                                                                                                                   | `Integer`                 |                             |
| `mirostatEta`              |                                                                                                                                                                                   | `Double`                  |                             |
| `mirostatTau`              |                                                                                                                                                                                   | `Double`                  |                             |
| `repeatLastN`              |                                                                                                                                                                                   | `Integer`                 |                             |
| `repeatPenalty`            | 对模型在生成输出中重复相似 token 进行惩罚。                                                                                                         | `Double`                  |                             |
| `seed`                     | 设置随机种子，以复现生成的响应。                                                                                                                  | `Integer`                 |                             |
| `numPredict`               | 为每个输入提示词生成的预测数量。                                                                                                                      | `Integer`                 |                             |
| `numCtx`                   |                                                                                                                                                                                   | `Integer`                 |                             |
| `stop`                     | 一个字符串列表，如果生成了其中任何一个，将标记响应的结束。                                                                                                          | `List<String>`            |                             |
| `minP`                     |                                                                                                                                                                                   | `Double`                  |                             |
| `responseFormat`           | 期望的生成输出格式。TEXT 或 JSON，可附带可选的 JSON Schema 定义                                                                                    | `ResponseFormat`          |                             |
| `think`                    | 控制[思考](https://ollama.com/blog/thinking)。                                                                                                                            | `Boolean`                 |                             |
| `truncate`                 | 控制服务器如何处理超出上下文窗口的提示词。见下文。                                                                                       | `Boolean`                 | `true`（服务器默认值）     |
| `returnThinking`           |                                                                                                                                                                                   | `Boolean`                 |                             |
| `timeout`                  | 允许 API 调用完成的最长时间。                                                                                                                            | `Duration`                | PT60S                       |
| `customHeaders`            | 自定义 HTTP 头。                                                                                                                                                              | `Map<String, String>`     |                             |
| `logRequests`              |                                                                                                                                                                                   | `Boolean`                 |                             |
| `logResponses`             |                                                                                                                                                                                   | `Boolean`                 |                             |
| `listeners`                | 参见 [Chat Model Observability](https://docs.langchain4j.dev/tutorials/observability#chat-model-observability)                                                                     | `List<ChatModelListener>` |                             |
| `supportedCapabilities`    | 由 `AiServices` API 使用的模型能力集合（仅支持 `OllamaChatModel`）                                                                                             | `Set<Capability>`         | RESPONSE_FORMAT_JSON_SCHEMA |
| `maxRetries`               | API 调用失败时的最大重试次数。                                                                                                                        | `Integer`                 |                             |

#### 用法示例
```java
OllamaChatModel ollamaChatModel = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("llama3.1")
    .temperature(0.8)
    .timeout(Duration.ofSeconds(60))
    .build();
```

#### 使用 Spring Boot 的用法示例

导入 Ollama 的 Spring Boot starter：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-ollama-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

!!! note
   此 starter 需要 **Spring Boot 4**。在 **Spring Boot 3** 上，请改用 `langchain4j-ollama-spring-boot-starter`。
   详见 [Spring Boot 集成](../../tutorials/spring-boot-integration.md#支持的版本)。

然后配置 `OllamaChatModel` bean：
```properties
langchain4j.ollama.chat-model.base-url=http://localhost:11434
langchain4j.ollama.chat-model.model-name=llama3.1
langchain4j.ollama.chat-model.temperature=0.8
langchain4j.ollama.chat-model.timeout=PT60S
```

### JSON 模式

```java
OllamaChatModel ollamaChatModel = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("llama3.1")
    .responseFormat(ResponseFormat.JSON)    
    .temperature(0.8)
    .timeout(Duration.ofSeconds(60))
    .build();
```

### 结构化输出

#### 使用构建器定义 JSON Schema

```java
OllamaChatModel ollamaChatModel = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("llama3.1")
    .responseFormat(ResponseFormat.builder()
            .type(ResponseFormatType.JSON)
            .jsonSchema(JsonSchema.builder().rootElement(JsonObjectSchema.builder()
                            .addProperty("name", JsonStringSchema.builder().build())
                            .addProperty("capital", JsonStringSchema.builder().build())
                            .addProperty(
                                    "languages",
                                    JsonArraySchema.builder()
                                            .items(JsonStringSchema.builder().build())
                                            .build())
                            .required("name", "capital", "languages")
                            .build())
                    .build())
            .build())
    .temperature(0.8)
    .timeout(Duration.ofSeconds(60))
    .build();
```

#### 使用 ChatRequest API 的 JSON Schema

```java
OllamaChatModel ollamaChatModel = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("llama3.1")
    .build();

ChatResponse chatResponse = ollamaChatModel.chat(ChatRequest.builder()
        .messages(userMessage("Tell me about Canada."))
        .responseFormat(ResponseFormat.builder()
                .type(ResponseFormatType.JSON)
                .jsonSchema(JsonSchema.builder().rootElement(JsonObjectSchema.builder()
                                .addProperty("name", JsonStringSchema.builder().build())
                                .addProperty("capital", JsonStringSchema.builder().build())
                                .addProperty(
                                        "languages",
                                        JsonArraySchema.builder()
                                                .items(JsonStringSchema.builder().build())
                                                .build())
                                .required("name", "capital", "languages")
                                .build())
                        .build())
                .build())
        .build());

String jsonFormattedResponse = chatResponse.aiMessage().text();

/* jsonFormattedResponse value:

  {
    "capital" : "Ottawa",
    "languages" : [ "English", "French" ],
    "name" : "Canada"
  }

 */


```


### 使用 AiServices 的 Json Schema

当使用受支持能力 `RESPONSE_FORMAT_JSON_SCHEMA` 创建 `OllamaChatModel` 时，`AIService` 会自动从接口返回值生成 schema。更多内容参见 [结构化输出](../../tutorials/structured-outputs.md#使用-json-schema-配合-ai-服务)

```java
OllamaChatModel ollamaChatModel = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("llama3.1")
    .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)    
    .build();
```

### 超出上下文窗口的提示词

默认情况下，Ollama 会丢弃提示词中超出上下文窗口的部分，并根据剩余部分进行回答。响应是正常的 `200`，
且 `promptEvalCount` 统计的是修剪后的提示词，因此无论是响应还是 token 用量都不会显示输入已丢失。

将 `truncate` 设置为 `false` 以改为获取错误。此时服务器会以 HTTP 400 拒绝请求，并同时报告提示词大小和上下文大小：

```java
ChatModel model = OllamaChatModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("llama3.1:8b")
        .numCtx(4096)
        .truncate(false)
        .build();
```

这在多轮智能体循环中非常有用，因为对话会随着每个工具结果不断增长，而被悄悄缩短的提示词比失败的请求更糟。
不设置 `truncate` 即可保持服务器默认行为。

### 思考 / 推理

支持[思考](https://ollama.com/blog/thinking)功能，由以下参数控制：
- `think`：控制 LLM 是否思考以及如何思考：
  - `true`：LLM 会思考，并在单独的 `thinking` 字段中返回思考内容
  - `false`：LLM 不进行思考
  - `null`（未设置）：推理型 LLM（例如 DeepSeek R1）会将用 `think` 和 `think` 分隔的思考内容前置到实际响应之前
- `returnThinking`：控制是否解析 API 响应中的 `thinking` 字段并在 `AiMessage.thinking()` 中返回，以及在使用 `OllamaStreamingChatModel` 时是否调用 `StreamingChatResponseHandler.onPartialThinking()`
和 `TokenStream.onPartialThinking()` 回调。默认禁用。

以下是如何配置思考功能的示例：
```java
ChatModel model = OllamaChatModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("qwen3:0.6b")
        .think(true)
        .returnThinking(true)
        .build();
```

### 自定义消息

除了标准聊天消息类型外，`OllamaChatModel` 和 `OllamaStreamingChatModel` 还支持自定义聊天消息。
自定义消息可用于指定带有任意属性的消息。这对于某些模型（例如 [Granite Guardian](https://ollama.com/library/granite3-guardian)）
非常有用，它们利用非标准消息来评估用于检索增强生成（RAG）的检索到的上下文。

下面看看如何使用 `CustomMessage` 来指定带有任意属性的消息：

```java
OllamaChatModel ollamaChatModel = OllamaChatModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("granite3-guardian")
    .build();
 
String retrievedContext = "One significant part of treaty making is that signing a treaty implies recognition that the other side is a sovereign state and that the agreement being considered is enforceable under international law. Hence, nations can be very careful about terming an agreement to be a treaty. For example, within the United States, agreements between states are compacts and agreements between states and the federal government or between agencies of the government are memoranda of understanding.";

List<ChatMessage> messages = List.of(
    SystemMessage.from("context_relevance"),
    UserMessage.from("What is the history of treaty making?"),
    CustomMessage.from(Map.of(
        "role", "context",
        "content", retrievedContext
    ))
);

ChatResponse chatResponse = ollamaChatModel.chat(ChatRequest.builder().messages(messages).build());

System.out.println(chatResponse.aiMessage().text()); // "Yes" (meaning risk detected by Granite Guardian)
```