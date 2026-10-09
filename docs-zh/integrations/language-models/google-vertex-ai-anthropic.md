# Google Vertex AI Anthropic

Google Vertex AI 提供对 Anthropic 的 Claude 模型的访问，通过 Google Cloud Platform 实现。此集成允许你在利用 Google Cloud 的基础设施和安全特性的同时，使用 Claude 先进的语言能力。

## 快速开始

### 创建 Google Cloud 账号

如果你是 Google Cloud 的新用户，可以在以下页面点击 `Get set up on Google Cloud` 下拉菜单下的 `[create an account]` 按钮来创建新账号：

[Create an account](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#new-to-google-cloud)

### 在你的 Google Cloud Platform 账号中创建项目

在你的 Google Cloud 账号中创建一个新项目，并按照以下步骤启用 Vertex AI API：

[Create a new project](https://cloud.google.com/vertex-ai/docs/start/cloud-environment#set_up_a_project)

请记住你的 `PROJECT_ID`，后续的 API 调用将会用到。

### 在 Vertex AI Model Garden 中启用 Claude 模型

需要在你的 Google Cloud 项目中启用 Claude 模型：

1. 前往 [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
2. 搜索 "Claude" 模型
3. 启用你想使用的 Claude 模型（例如 Claude 3.5 Sonnet、Claude 3 Opus）

### 选择 Google Cloud 认证策略

你的应用程序有几种方式可以向 Google Cloud 服务和 API 进行认证。例如，你可以创建一个 [service account](https://cloud.google.com/docs/authentication/provide-credentials-adc#local-key)（服务账号），并将环境变量 `GOOGLE_APPLICATION_CREDENTIALS` 设置为包含你凭据的 JSON 文件的路径。

你可以在[这里](https://cloud.google.com/docs/authentication/provide-credentials-adc)了解所有认证策略。但为了本地测试的简便，我们将使用通过 `gcloud` 工具进行的认证。

### 安装 Google Cloud CLI（可选）

要在本地访问你的云项目，可以按照[安装说明](https://cloud.google.com/sdk/docs/install)安装 `gcloud` 工具。对于 GNU/Linux 操作系统，安装步骤如下：

1. 下载 SDK：

```bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-467.0.0-linux-x86_64.tar.gz
```

2. 解压压缩包：

```bash
tar -xf google-cloud-cli-467.0.0-linux-x86_64.tar.gz
```

3. 运行安装脚本：

```bash
cd google-cloud-sdk/
./install.sh
```

4. 运行以下命令，设置默认项目和认证凭据：

```bash
gcloud auth application-default login
```

此认证方式与 `langchain4j-vertex-ai-anthropic` 包兼容。

## 添加依赖

首先，将以下依赖添加到项目的 `pom.xml` 中：

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-vertex-ai-anthropic</artifactId>
  <version>1.22.0-beta32</version>
</dependency>
```

或者项目的 `build.gradle`：

```groovy
implementation 'dev.langchain4j:langchain4j-vertex-ai-anthropic:1.22.0-beta32'
```

### 运行示例代码

`PROJECT_ID` 字段代表你创建新的 Google Cloud 项目时设置的变量。

```java
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.chat.request.ChatRequest;
import dev.langchain4j.model.chat.response.ChatResponse;
import dev.langchain4j.model.vertexai.anthropic.VertexAiAnthropicChatModel;

public class VertexAiAnthropicExample {

    private static final String PROJECT_ID = "YOUR-PROJECT-ID";
    private static final String LOCATION = "us-central1";
    private static final String MODEL_NAME = "claude-3-5-sonnet-v2@20241022";

    public static void main(String[] args) {
        ChatModel model = VertexAiAnthropicChatModel.builder()
                .project(PROJECT_ID)
                .location(LOCATION)
                .modelName(MODEL_NAME)
                .maxTokens(1000)
                .temperature(0.7)
                .build();

        ChatResponse response = model.chat(ChatRequest.builder()
                .messages(List.of(UserMessage.from("Hello, Claude!")))
                .build());

        System.out.println(response.aiMessage().text());
    }
}
```

此外还支持流式，通过 `VertexAiAnthropicStreamingChatModel` 类实现：

```java
import dev.langchain4j.model.vertexai.anthropic.VertexAiAnthropicStreamingChatModel;
import dev.langchain4j.model.chat.StreamingChatResponseHandler;

var model = VertexAiAnthropicStreamingChatModel.builder()
        .project(PROJECT_ID)
        .location(LOCATION)
        .modelName(MODEL_NAME)
        .build();

model.

chat(ChatRequest.builder()
    .

messages(List.of(UserMessage.from("Tell me a story")))
        .

build(), new

StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse (String partialResponse){
        System.out.print(partialResponse);
    }

    @Override
    public void onCompleteResponse (ChatResponse completeResponse){
        System.out.println("\nDone!");
    }

    @Override
    public void onError (Throwable error){
        error.printStackTrace();
    }
});
```

你可以使用 `LambdaStreamingResponseHandler` 中的快捷工具函数 `onPartialResponse()` 和 `onPartialResponseAndError()`：

```java
import static dev.langchain4j.model.chat.response.streaming.LambdaStreamingResponseHandler.onPartialResponse;
import static dev.langchain4j.model.chat.response.streaming.LambdaStreamingResponseHandler.onPartialResponseAndError;

model.chat(ChatRequest.builder()
    .messages(List.of(UserMessage.from("Why is the sky blue?")))
    .build(), onPartialResponse(System.out::print));

model.chat(ChatRequest.builder()
    .messages(List.of(UserMessage.from("Why is the sky blue?")))
    .build(), onPartialResponseAndError(System.out::print, Throwable::printStackTrace));
```

### 可用模型

[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/claude) 的可用模型列表。
你可以在 [Claude 模型文档](https://docs.anthropic.com/en/docs/about-claude/models) 中了解这些模型。

## 配置

```java
ChatModel model = VertexAiAnthropicChatModel.builder()
    .project(PROJECT_ID)            // your Google Cloud project ID
    .location(LOCATION)             // where inference takes place, see "Locations" below
    .modelName(MODEL_NAME)          // the Claude model used
    .maxTokens(4096)               // the maximum number of tokens to generate
    .temperature(0.7)              // temperature (between 0 and 1)
    .topP(0.95)                    // topP (between 0 and 1) — cumulative probability
    .topK(40)                      // topK (positive integer) — pick from top K tokens
    .stopSequences(Arrays.asList("Human:", "Assistant:")) // stop sequences
    .enablePromptCaching(true)     // enable prompt caching for cost/latency optimization
    .credentials(credentials)      // custom Google Cloud credentials
    .logRequests(true)             // log input requests
    .logResponses(true)            // log output responses
    .build();
```

流式聊天模型也提供相同的参数。

### 位置

`location` 决定你的请求在哪里处理。Vertex AI 提供三种类型的位置，
你传入 `.location(...)` 的值决定使用哪一种：

| 位置值 | 类型 | 作用 |
|---|---|---|
| `"global"` | 全球 | 将每个请求路由到任何有可用容量的区域。可用性最佳，无价格溢价。除非你有数据驻留要求，否则推荐此项。 |
| `"us"`, `"eu"` | 多区域 | 将每个请求路由到该地理区域内的某个区域，兼顾高可用性与数据驻留。 |
| `"us-east5"`, `"europe-west1"`, ... | 区域 | 将所有请求通过一个特定区域处理。单区域数据驻留和预配置吞吐量所必需。 |

```java
ChatModel model = VertexAiAnthropicChatModel.builder()
    .project(PROJECT_ID)
    .location("global")
    .modelName(MODEL_NAME)
    .build();
```

请注意，模型可用性因位置而异，并且多区域和区域位置相比全球位置有价格溢价。详情请参阅
[全球、多区域和区域端点](https://platform.claude.com/docs/en/build-with-claude/claude-on-vertex-ai#global-multi-region-and-regional-endpoints)。

## 更多示例

Claude 是一个强大的多模态模型，可同时接受文本和图像作为输入。

### 视觉能力

```java
import dev.langchain4j.data.image.Image;
import dev.langchain4j.data.message.ImageContent;
import dev.langchain4j.data.message.TextContent;
import dev.langchain4j.data.message.UserMessage;

ChatModel model = VertexAiAnthropicChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("claude-3-5-sonnet-v2@20241022")
    .build();

Image image = Image.builder()
    .base64Data("base64-encoded-image-data")
    .mimeType("image/jpeg")
    .build();

UserMessage userMessage = UserMessage.from(
    ImageContent.from(image),
    TextContent.from("What do you see in this image?")
);

ChatResponse response = model.chat(ChatRequest.builder()
    .messages(List.of(userMessage))
    .build());

System.out.println(response.aiMessage().text());
```

### 工具调用

```java
import dev.langchain4j.agent.tool.ToolSpecification;
import dev.langchain4j.data.message.ToolExecutionResultMessage;
import dev.langchain4j.model.output.structured.JsonObjectSchema;

ChatModel model = VertexAiAnthropicChatModel.builder()
        .project(PROJECT_ID)
        .location(LOCATION)
        .modelName("claude-3-5-sonnet-v2@20241022")
        .build();

ToolSpecification weatherToolSpec = ToolSpecification.builder()
        .name("getWeatherForecast")
        .description("Get the weather forecast for a location")
        .parameters(JsonObjectSchema.builder()
                .addStringProperty("location", "the location to get the weather forecast for")
                .required("location")
                .build())
        .build();

ChatRequest request = ChatRequest.builder()
        .messages(List.of(UserMessage.from("What is the weather in Paris?")))
        .toolSpecifications(List.of(weatherToolSpec))
        .build();

ChatResponse response = model.chat(request);
```

模型将返回一个工具执行请求，而不是文本消息。
你的职责是通过向模型发送 `ToolExecutionResultMessage` 来提供该执行请求的响应。
然后，模型就能以文本响应作答。

### AiServices 中的工具支持

你可以使用 `AiServices` 创建由工具驱动的自定义助手。
下面的示例展示了一个用于执行数学计算的 `Calculator` 工具，
一个用于指定我们助手约定的 `Assistant` 接口，
然后我们配置 `AiServices` 使用 Claude，并配备聊天记忆和计算器工具。

```java
import dev.langchain4j.service.AiServices;
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.memory.chat.MessageWindowChatMemory;

static class Calculator {
    @Tool("Adds two given numbers")
    double add(double a, double b) {
        return a + b;
    }

    @Tool("Multiplies two given numbers")
    String multiply(double a, double b) {
        return String.valueOf(a * b);
    }
}

interface Assistant {
    String chat(String userMessage);
}

Calculator calculator = new Calculator();

Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(model)
        .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
        .tools(calculator)
        .build();

String answer = assistant.chat("How much is 74589613588 + 4786521789?");
```

### 提示词缓存

Claude 支持提示词缓存，以降低重复或长提示词的成本并改善响应时间：

```java
import dev.langchain4j.data.message.SystemMessage;

ChatModel model = VertexAiAnthropicChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("claude-3-5-sonnet-v2@20241022")
    .enablePromptCaching(true)
    .build();

SystemMessage systemMessage = SystemMessage.from(
    "You are an expert software engineer with deep knowledge of Java, " +
    "Spring Boot, microservices architecture, and cloud-native development. " +
    "Always provide detailed, production-ready code examples with proper " +
    "error handling, logging, and best practices."
);

UserMessage userMessage = UserMessage.from("How do I implement JWT authentication?");

ChatResponse response = model.chat(ChatRequest.builder()
    .messages(List.of(systemMessage, userMessage))
    .build());
```

提示词缓存提供：
- **降低成本**：缓存内容最高可便宜 90%
- **延迟改善**：响应时间最快提升 85%
- **自动优化**：无需手动管理缓存

### 自定义认证

你可以提供自定义的 Google Cloud 凭据：

```java
import com.google.auth.oauth2.GoogleCredentials;
import java.io.FileInputStream;

GoogleCredentials credentials = GoogleCredentials.fromStream(
    new FileInputStream("path/to/service-account-key.json"));

ChatModel model = VertexAiAthropicChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("claude-3-5-sonnet-v2@20241022")
    .credentials(credentials)
    .build();
```

## 参考

[可用位置](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#available-regions)

[Claude 模型文档](https://docs.anthropic.com/en/docs/about-claude/models)

[Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
