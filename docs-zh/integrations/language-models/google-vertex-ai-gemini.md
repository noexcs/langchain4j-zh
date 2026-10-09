# Google Vertex AI Gemini

Vertex AI 是 Google Cloud 的全托管 AI 开发平台，提供对 Google 大型生成式模型的访问，包括上一代（PaLM2）和新一代（Gemini）。

要使用 Vertex AI，首先必须创建一个 Google Cloud Platform 账户。

## 快速上手

### 创建 Google Cloud 账户

如果你是 Google Cloud 的新用户，可以点击下方页面上 `Get set up on Google Cloud` 下拉菜单中的 `[create an account]` 按钮创建新账户：

[创建账户](https://cloud.google.com/vertex-ai/generative-ai/docs/start/quickstarts/quickstart-multimodal#new-to-google-cloud)

### 在你的 Google Cloud Platform 账户中创建一个项目。

在你的 Google Cloud 账户中创建一个新项目，并按照以下步骤启用 Vertex AI API：

[创建新项目](https://cloud.google.com/vertex-ai/docs/start/cloud-environment#set_up_a_project)

请记住你的 `PROJECT_ID`，因为在后续的 API 调用中会用到它。

### 选择 Google Cloud 认证策略

你的应用程序认证到 Google Cloud 服务和 API 有几种方式。例如，你可以创建一个[服务账户](https://cloud.google.com/docs/authentication/provide-credentials-adc#local-key)，并将环境变量 `GOOGLE_APPLICATION_CREDENTIALS` 设置为包含你凭据的 JSON 文件的路径。

你可以[在此处](https://cloud.google.com/docs/authentication/provide-credentials-adc)了解所有认证策略。但为了本地测试的简洁性，我们将使用通过 `gcloud` 工具的认证。

### 安装 Google Cloud CLI（可选）

要在本地访问你的云项目，可以按照[安装说明](https://cloud.google.com/sdk/docs/install)安装 `gcloud` 工具。对于 GNU/Linux 操作系统，安装步骤如下：

1. 下载 SDK：

```bash
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-467.0.0-linux-x86_64.tar.gz
```

2. 解压缩归档：

```bash
tar -xf google-cloud-cli-467.0.0-linux-x86_64.tar.gz
```
3. 运行安装脚本：

```bash
cd google-cloud-sdk/
./install.sh
```

4. 运行以下命令以设置默认项目和认证凭据：

```bash
gcloud auth application-default login
```

这种认证方式与 `vertex-ai`（嵌入模型、PaLM2）和 `vertex-ai-gemini`（Gemini）包都兼容。

## 添加依赖

要开始使用，请将以下依赖添加到项目的 `pom.xml` 中：

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-vertex-ai-gemini</artifactId>
  <version>1.22.0-beta32</version>
</dependency>
```

或项目的 `build.gradle`：

```groovy
implementation 'dev.langchain4j:langchain4j-vertex-ai-gemini:1.22.0-beta32'
```

### 尝试示例代码：

[使用聊天模型进行文本预测的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/vertex-ai-gemini-examples/src/main/java/VertexAiGeminiChatModelExamples.java)

[Gemini Pro Vision 配合图像输入](https://github.com/langchain4j/langchain4j/blob/657aac9519b57afc04ea434ddcfa70d701923b91/langchain4j-vertex-ai-gemini/src/test/java/dev/langchain4j/model/vertexai/VertexAiGeminiChatModelIT.java#L123)

`PROJECT_ID` 字段代表你创建新的 Google Cloud 项目时设置的变量。

```java
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.data.message.ImageContent;
import dev.langchain4j.data.message.TextContent;
import dev.langchain4j.data.message.UserMessage;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.output.Response;
import dev.langchain4j.model.vertexai.gemini.VertexAiGeminiChatModel;

public class GeminiProVisionWithImageInput {

    private static final String PROJECT_ID = "YOUR-PROJECT-ID";
    private static final String LOCATION = "us-central1";
    private static final String MODEL_NAME = "gemini-1.5-flash";
    private static final String CAT_IMAGE_URL = "https://upload.wikimedia.org/" +
        "wikipedia/commons/e/e9/" +
        "Felis_silvestris_silvestris_small_gradual_decrease_of_quality.png";

    public static void main(String[] args) {
        ChatModel visionModel = VertexAiGeminiChatModel.builder()
            .project(PROJECT_ID)
            .location(LOCATION)
            .modelName(MODEL_NAME)
            .build();

        ChatResponse response = visionModel.chat(
            UserMessage.from(
                ImageContent.from(CAT_IMAGE_URL),
                TextContent.from("What do you see?")
            )
        );
        
        System.out.println(response.aiMessage().text());
    }
}
```

多亏 `VertexAiGeminiStreamingChatModel` 类，流式同样受支持：

```java
var model = VertexAiGeminiStreamingChatModel.builder()
        .project(PROJECT_ID)
        .location(LOCATION)
        .modelName(GEMINI_1_5_PRO)
        .build();

model.chat("Why is the sky blue?", new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.print(partialResponse);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse){
        System.print(completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

你可以使用 `LambdaStreamingResponseHandler` 中的 `onPartialResponse()` 和 `onPartialResponseAndError()` 工具函数：

```java
model.chat("Why is the sky blue?", onPartialResponse(System.out::print));
model.chat("Why is the sky blue?", onPartialResponseAndError(System.out::print, Throwable::printStackTrace));
```

### 可用模型

| 模型名称                | 描述                                                                                                                         | 输入                                                  | 属性                                            |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|-------------------------------------------------------|
| `gemini-1.5-flash`        | 为大批量、高质量、高性价比的应用提供速度和效率。                                                        | 文本、代码、图像、音频、视频、带音频的视频、PDF | 最大输入 token 数：1,048,576，最大输出 token 数：8,192 |
| `gemini-1.5-pro`          | 支持文本或聊天提示词，以文本或代码形式响应。支持长达最大输入 token 限制的长上下文理解。 | 文本、代码、图像、音频、视频、带音频的视频、PDF | 最大输入 token 数：2,097,152，最大输出 token 数：8,192 |
| `gemini-1.0-pro`          | 适用于广泛纯文本任务的最佳性能模型。                                                                      | 文本                                                    | 最大输入 token 数：32,760，最大输出 token 数：8,192    |
| `gemini-1.0-pro-vision`   | 性能最佳的图像和视频理解模型，可处理广泛的应用。                                    | 文本、图像、音频、视频、带音频的视频、PDF       | 最大输入 token 数：16,384，最大输出 token 数：2,048    |
| `gemini-1.0-ultra`        | 功能最强的文本模型，针对复杂任务进行了优化，包括指令、代码和推理。                               | 文本                                                    | 最大输入 token 数：8,192，最大输出 token 数：2,048     |
| `gemini-1.0-ultra-vision` | 功能最强的多模态视觉模型。经过优化，支持文本、图像和视频的联合输入。                                | 文本、代码、图像、音频、视频、带音频的视频、PDF | 最大输入 token 数：8,192，最大输出 token 数：2,048     |

你可以在 [Gemini 模型文档页面](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models) 了解有关这些模型的更多信息

请注意，2024 年 3 月时，Ultra 版本通过白名单提供私有访问。因此，你可能会收到类似如下的异常：

```text
Caused by: io.grpc.StatusRuntimeException:
 FAILED_PRECONDITION: Project `1234567890` is not allowed to use Publisher Model
  `projects/{YOUR_PROJECT_ID}/locations/us-central1/publishers/google/models/gemini-ultra`
```

## 配置

```java
ChatModel model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)        // your Google Cloud project ID
    .location(LOCATION)         // the region where AI inference should take place
    .modelName(MODEL_NAME)      // the model used
    .logRequests(true)          // log input requests
    .logResponses(true)         // log output responses
    .maxOutputTokens(8192)      // the maximum number of tokens to generate (up to 8192)
    .temperature(0.7)           // temperature (between 0 and 2)
    .topP(0.95)                 // topP (between 0 and 1) — cumulative probability of the most probable tokens
    .topK(3)                    // topK (positive integer) — pick a token among the most probable ones
    .seed(1234)                 // seed for the random number generator
    .maxRetries(2)              // maximum number of retries
    .responseMimeType("application/json") // to get JSON structured outputs
    .responseSchema(/*...*/)    // structured output following the provided schema
    .safetySettings(/*...*/)    // specify safety settings to filter inappropriate content
    .useGoogleSearch(true)      // to ground responses with Google Search results
    .vertexSearchDatastore(name)// to ground responses with data backed documents 
                                // from a custom Vertex AI Search datastore
    .toolCallingMode(/*...*/)   // AUTO (automatic), ANY (from a list of functions), NONE
    .allowedFunctionNames(/*...*/) // when using ANY tool calling mode, 
                                // specify the allowed function names to be called
    .listeners(/*...*/)         // list of listeners to receive model events
    .credentials(credentials)   // custom Google Cloud credentials    
    .build();
```

流式聊天模型同样提供相同的参数。

## 更多示例

Gemini 是一个 `multimodal`（多模态）模型，输入除了文本之外，还可以接受图像、音频和视频文件以及 PDF。

### 描述图像的内容

```java
ChatModel model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName(GEMINI_1_5_PRO)
    .build();

UserMessage userMessage = UserMessage.from(
    ImageContent.from(CAT_IMAGE_URL),
    TextContent.from("What do you see? Reply in one word.")
);

ChatResponse response = model.chat(userMessage);
```

该 URL 可以是网络 URL，也可以指向存储在 Google Cloud Storage 存储桶中的文件，
例如 `gs://my-bucket/my-image.png`。

你还可以将图像内容作为 Base64 编码字符串传入：

```java
String base64Data = Base64.getEncoder().encodeToString(readBytes(CAT_IMAGE_URL));
UserMessage userMessage = UserMessage.from(
        ImageContent.from(base64Data, "image/png"),
        TextContent.from("What do you see? Reply in one word.")
);
```

### 针对 PDF 文档提问

```java
var model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName(GEMINI_1_5_PRO)
    .logRequests(true)
    .logResponses(true)
    .build();

UserMessage message = UserMessage.from(
    PdfFileContent.from(Paths.get("src/test/resources/gemini-doc-snapshot.pdf").toUri()),
    TextContent.from("Provide a summary of the document")
);

ChatResponse response = model.chat(message);
```

### 工具调用

```java
ChatModel model = VertexAiGeminiChatModel.builder()
        .project(PROJECT_ID)
        .location(LOCATION)
        .modelName(GEMINI_1_5_PRO)
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
        .messages(UserMessage.from("What is the weather in Paris?"))
        .toolSpecifications(weatherToolSpec)
        .build();

ChatResponse response = model.chat(request);
```

模型将返回一个工具执行请求，而不是文本消息。
你的职责是将该执行请求的响应提供给模型，
方法是向模型发送一个 `ToolExecutionResultMessage`。
之后模型就可以返回文本响应。

并行函数调用也受支持，即当模型在单个响应中请求多个工具执行时。

### AiServices 中的工具支持

你可以使用 `AiServices` 创建你自己的、由工具驱动的助手。
下面的示例展示了一个用于进行一些数学计算的 `Calculator` 工具，
一个用于指定我们助手契约的 `Assistant` 接口，
然后我们配置 `AiServices` 使用 Gemini，并配备聊天记忆和计算器工具。

```java
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

### 使用 Google 搜索结果支撑响应

LLM 不一定知道所有可能问题的答案！
对于近期事件或在其最后一次训练结束之后发生的信息，更是如此。
你可以使用 Google 搜索的最新结果来支撑 Gemini 的回答：

```java
var modelWithSearch = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("gemini-1.5-flash-001")
    .useGoogleSearch(true)
    .build();

String resp = modelWithSearch.chat("What is the score of yesterday's football match from Paris Saint Germain?");
```

### 使用 Vertex AI Search 结果支撑响应

当处理私有的内部信息、文档和数据时，你可以使用
[Vertex AI Search 数据存储](https://cloud.google.com/generative-ai-app-builder/docs/create-data-store-es)来存放这些文档。
然后你可以用这些文档为 Gemini 的回答做支撑：

```java
var modelWithSearch = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("gemini-1.5-flash-001")
    .vertexSearchDatastore("name_of_the_datastore")
    .build();
```

### JSON 结构化输出

你可以要求 Gemini 只返回有效的 JSON 输出：

```java
var modelWithResponseMimeType = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("gemini-1.5-flash-001")
    .responseMimeType("application/json")
    .build();

String userMessage = "Return JSON with two fields: name and surname of Klaus Heisler.";
String jsonResponse = modelWithResponseMimeType.chat(userMessage).content().text();
// {"name": "Klaus", "surname": "Heisler"}
```

### 使用 JSON Schema 实现严格的 JSON 结构化输出

如果提示词没有精确描述期望的 JSON 输出，即使使用了 `responseMimeType("application/json)`，
模型在响应方式上仍可能有些"发挥"。
要确保更严格的 JSON 结构化输出，你可以为响应指定一个 JSON Schema：

```java
Schema schema = Schema.newBuilder()
    .setType(Type.OBJECT)
    .putProperties("name", Schema.newBuilder()
        .setType(Type.STRING)
        .build())
    .putProperties("address", Schema.newBuilder()
        .setType(Type.OBJECT)
        .putProperties("street", 
            Schema.newBuilder().setType(Type.STRING).build())
        .putProperties("zipcode",
           Schema.newBuilder().setType(Type.STRING).build())
    .build())
.build();

var model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName(GEMINI_1_5_PRO)
    .responseMimeType("application/json")
    .responseSchema(Schema)
    .build();
```

一个便捷方法允许你为 Java 类生成 Schema：

```java
class Artist {
    public String artistName;
    int artistAge;
    protected boolean artistAdult;
    private String artistAddress;
    public Pet[] pets;
}

class Pet {
    public String name;
}

Schema schema = SchemaHelper.fromClass(Artist.class);

var model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName(GEMINI_1_5_PRO)
    .responseMimeType("application/json")
    .responseSchema(schema)
    .build();
```

另一个方法允许你从 JSON Schema 字符串创建 Schema：
`SchemaHelper.fromJson(...)`。

Gemini 支持 JSON 对象和数组作为结构化输出，
但 JSON 字符串枚举作为输出也有一个特殊场景，
这在要求 Gemini 执行分类任务（例如情感分析）时特别有用：

```java
var model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName(GEMINI_1_5_PRO)
    .logRequests(true)
    .logResponses(true)
    .responseSchema(Schema.newBuilder()
        .setType(Type.STRING)
        .addAllEnum(Arrays.asList("POSITIVE", "NEUTRAL", "NEGATIVE"))
        .build())
    .build();
```

在这种情况下，隐式的响应 MIME 类型被设置为 `text/x.enum`
（这不是一个官方注册的 MIME 类型）。

### 指定安全设置

如果你想过滤或拦截有害内容，可以设置带有不同阈值级别的安全设置：

```java
HashMap<HarmCategory, SafetyThreshold> safetySettings = new HashMap<>();
safetySettings.put(HARM_CATEGORY_HARASSMENT, BLOCK_LOW_AND_ABOVE);
safetySettings.put(HARM_CATEGORY_DANGEROUS_CONTENT, BLOCK_ONLY_HIGH);
safetySettings.put(HARM_CATEGORY_SEXUALLY_EXPLICIT, BLOCK_MEDIUM_AND_ABOVE);

var model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("gemini-1.5-flash-001")
    .safetySettings(safetySettings)
    .logRequests(true)
    .logResponses(true)
    .build();
```

### 自定义认证

你可以提供自定义的 Google Cloud 凭据：

```java
import com.google.auth.oauth2.GoogleCredentials;
import java.io.FileInputStream;

GoogleCredentials credentials = GoogleCredentials.fromStream(
    new FileInputStream("path/to/service-account-key.json"));

var model = VertexAiGeminiChatModel.builder()
    .project(PROJECT_ID)
    .location(LOCATION)
    .modelName("gemini-1.5-flash-001")
    .credentials(credentials)
    .build();
```

## 参考资料

[可用位置](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations#available-regions)

[多模态能力](https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/overview#multimodal_models)


## 示例

- [Google Vertex AI Gemini 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/vertex-ai-gemini-examples/src/main/java)
