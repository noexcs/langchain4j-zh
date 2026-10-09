# Azure OpenAI

!!! note
    这是 `Azure OpenAI` 集成的文档。该集成使用 Microsoft 的 Azure SDK，如果你在使用 Microsoft Java 技术栈（包括高级的 Azure 认证机制），则最适合你。

    LangChain4j 提供了 3 种不同的 OpenAI 集成来使用聊天模型，这是其中的第 3 种：

    - [OpenAI](open-ai.md) 使用 OpenAI REST API 的自定义 Java 实现，最适合 Quarkus（因为它使用 Quarkus REST client）和 Spring（因为它使用 Spring 的 RestClient）。
    - [OpenAI Official SDK](open-ai-official.md) 使用官方的 OpenAI Java SDK。
    - [Azure OpenAI](azure-open-ai.md) 使用 Microsoft 的 Azure SDK，如果你在使用 Microsoft Java 技术栈（包括高级的 Azure 认证机制），则最适合你。

Azure OpenAI 提供托管在 Azure 上的 OpenAI 语言模型（`gpt-4`、`gpt-4o` 等），使用 [Azure OpenAI Java SDK](https://learn.microsoft.com/en-us/java/api/overview/azure/ai-openai-readme)。

## Azure OpenAI 文档

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## Maven 依赖

### 纯 Java

`langchain4j-azure-open-ai` 库可在 Maven Central 上获取。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-azure-open-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

### Spring Boot

提供了一个 Spring Boot starter，可以更轻松地配置 `langchain4j-azure-open-ai` 库。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-azure-open-ai-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

!!! note
    此 starter 需要 **Spring Boot 4**。在 **Spring Boot 3** 上，请改用 `langchain4j-azure-open-ai-spring-boot-starter`。
    详情请参阅 [Spring Boot Integration](../../tutorials/spring-boot-integration.md#支持的版本)。

!!! note
    在使用任何 Azure OpenAI 模型之前，你需要先[部署](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)它们。

## 使用 API 密钥创建 `AzureOpenAiChatModel`

### 纯 Java

```java
ChatModel model = AzureOpenAiChatModel.builder()
        .endpoint(System.getenv("AZURE_OPENAI_URL"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .deploymentName("gpt-4o")
        ...
        .build();
```

这将使用指定的端点、API 密钥和部署名称创建一个 `AzureOpenAiChatModel` 实例。
其他参数可以在构建器中提供值来自定义。

### Spring Boot

在 `application.properties` 中添加：
```properties
langchain4j.azure-open-ai.chat-model.endpoint=${AZURE_OPENAI_URL}
langchain4j.azure-open-ai.chat-model.service-version=...
langchain4j.azure-open-ai.chat-model.api-key=${AZURE_OPENAI_KEY}
langchain4j.azure-open-ai.chat-model.non-azure-api-key=${OPENAI_API_KEY}
langchain4j.azure-open-ai.chat-model.deployment-name=gpt-4o
langchain4j.azure-open-ai.chat-model.max-completion-tokens=...
langchain4j.azure-open-ai.chat-model.max-tokens=...
langchain4j.azure-open-ai.chat-model.temperature=...
langchain4j.azure-open-ai.chat-model.top-p=
langchain4j.azure-open-ai.chat-model.logit-bias=...
langchain4j.azure-open-ai.chat-model.user=
langchain4j.azure-open-ai.chat-model.stop=...
langchain4j.azure-open-ai.chat-model.presence-penalty=...
langchain4j.azure-open-ai.chat-model.frequency-penalty=...
langchain4j.azure-open-ai.chat-model.seed=...
langchain4j.azure-open-ai.chat-model.strict-json-schema=...
langchain4j.azure-open-ai.chat-model.timeout=...
langchain4j.azure-open-ai.chat-model.max-retries=...
langchain4j.azure-open-ai.chat-model.log-requests-and-responses=...
langchain4j.azure-open-ai.chat-model.user-agent-suffix=
langchain4j.azure-open-ai.chat-model.custom-headers=...
langchain4j.azure-open-ai.chat-model.reasoningEffort=...
```
上述部分参数的说明见[这里](https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#completions)。

该配置将创建一个 `AzureOpenAiChatModel` bean（使用默认模型参数），
既可以被 [AI 服务](../../tutorials/spring-boot-integration.md#spring-boot-starters) 使用，
也可以在需要的地方自动装配，例如：

```java
@RestController
class ChatModelController {

    ChatModel chatModel;

    ChatModelController(ChatModel chatModel) {
        this.chatModel = chatModel;
    }

    @GetMapping("/model")
    public String model(@RequestParam(value = "message", defaultValue = "Hello") String message) {
        return chatModel.chat(message);
    }
}
```

## 使用 Azure 凭据创建 `AzureOpenAiChatModel`

API 密钥可能存在一些安全问题（可能被提交到代码库、被随意传递等）。
如果你想提升安全性，建议使用 Azure 凭据。
为此，需要在项目中添加 `azure-identity` 依赖。

```xml
<dependency>
    <groupId>com.azure</groupId>
    <artifactId>azure-identity</artifactId>
    <scope>compile</scope>
</dependency>
```

然后，你可以使用 [DefaultAzureCredentialBuilder](https://learn.microsoft.com/en-us/java/api/com.azure.identity.defaultazurecredentialbuilder?view=azure-java-stable) API 来创建 `AzureOpenAiChatModel`：

```java
ChatModel model = AzureOpenAiChatModel.builder()
        .deploymentName("gpt-4o")
        .endpoint(System.getenv("AZURE_OPENAI_URL"))
        .tokenCredential(new DefaultAzureCredentialBuilder().build())
        .build();
```

!!! note
    注意，你需要使用托管标识（Managed Identities）来部署你的模型。更多信息请参阅 [Azure CLI 部署脚本](https://github.com/langchain4j/langchain4j-examples/blob/main/azure-open-ai-examples/src/main/script/deploy-azure-openai-security.sh)。

## 工具

工具（也称为"函数调用"）已获支持，并允许模型调用你 Java 代码中的方法，包括并行工具调用。
"函数调用"在 OpenAI 文档的[这里](https://platform.openai.com/docs/guides/function-calling)有描述。

!!! note
    关于如何在 LangChain4j 中使用"函数调用"的完整教程见[这里](../../tutorials/tools.md)。

函数可以使用 `ToolSpecification` 类来指定，或者更简单地使用 `@Tool` 注解，如下面的示例：

```java
class StockPriceService {

    private Logger log = Logger.getLogger(StockPriceService.class.getName());

    @Tool("Get the stock price of a company by its ticker")
    public double getStockPrice(@P("Company ticker") String ticker) {
        log.info("Getting stock price for " + ticker);
        if (Objects.equals(ticker, "MSFT")) {
            return 400.0;
        } else {
            return 0.0;
        }
    }
}
```

然后，你可以像这样在 AI `Assistant` 中使用 `StockPriceService`：

```java

interface Assistant {
    String chat(String userMessage);
}

public class Demo {
    String functionCalling(Model model) {
        String question = "Is the current Microsoft stock higher than $450?";
        StockPriceService stockPriceService = new StockPriceService();

        Assistant assistant = AiServices.builder(Assistant.class)
                .chatModel(model)
                .tools(stockPriceService)
                .build();

        String answer = assistant.chat(question);

        model.addAttribute("answer", answer);
        return "demo";
    }
}
```

## 结构化输出

结构化输出确保模型的响应遵循 JSON schema。

!!! note
    关于在 LangChain4j 中使用结构化输出的文档见[这里](../../tutorials/structured-outputs.md)，下面一节将提供 Azure OpenAI 专属的信息。

需要配置模型参数，将 `strictJsonSchema` 设置为 `true`，才能强制遵循 JSON Schema：

```java
ChatModel model = AzureOpenAiChatModel.builder()
        .endpoint(System.getenv("AZURE_OPENAI_URL"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .deploymentName("gpt-4o")
        .strictJsonSchema(true)
        .supportedCapabilities(Set.of(RESPONSE_FORMAT_JSON_SCHEMA))
        .build();
```

!!! note
    如果 `strictJsonSchema` 设置为 `false` 而你提供了 JSON Schema，模型仍会尝试生成遵循该 schema 的响应，但如果响应未遵循 schema 则不会失败。这样做的一个原因是为了获得更好的性能。

然后，你可以按照下面的详细说明，使用高层级 `Assistant` API 或低层级 `ChatModel` API 来使用该模型。
在使用高层级 `Assistant` API 时，请配置 `supportedCapabilities(Set.of(RESPONSE_FORMAT_JSON_SCHEMA))` 以启用基于 JSON schema 的结构化输出。

### 使用高层级 `Assistant` API

与上一节的工具类似，结构化输出也可以与 AI `Assistant` 配合自动使用：

```java

interface PersonAssistant {
    Person extractPerson(String message);
}

class Person {
    private final String name;
    private final List<String> favouriteColors;

    public Person(String name, List<String> favouriteColors) {
        this.name = name;
        this.favouriteColors = favouriteColors;
    }

    public String getName() {
        return name;
    }

    public List<String> getFavouriteColors() {
        return favouriteColors;
    }
}
```

此 `Assistant` 会确保响应遵循与 `Person` 类对应的 JSON schema，如下面的示例：

```java
String question = "Julien likes the colors blue, white and red";

PersonAssistant assistant = AiServices.builder(PersonAssistant.class)
                .chatModel(chatModel)
                .build();

Person person = assistant.extractPerson(question);
```

### 使用低层级 `ChatModel` API

这与高层级 API 的过程类似，但这次需要手动配置 JSON schema，以及将 JSON 响应映射为 Java 对象。

配置好模型后，必须在每个请求的 `ChatRequest` 对象中指定 JSON Schema。
然后，模型将生成遵循该 schema 的响应，如本例所示：

```java
ChatRequest chatRequest = ChatRequest.builder()
    .messages(UserMessage.from("Julien likes the colors blue, white and red"))
    .responseFormat(ResponseFormat.builder()
        .type(JSON)
        .jsonSchema(JsonSchema.builder()
            .name("Person")
            .rootElement(JsonObjectSchema.builder()
                .addStringProperty("name")
                .addProperty("favouriteColors", JsonArraySchema.builder()
                    .items(new JsonStringSchema())
                    .build())
                .required("name", "favouriteColors")
                .build())
            .build())
        .build())
    .build();

String answer = chatModel.chat(chatRequest).aiMessage().text();
```

在本例中，`answer` 将是：
```json
{
  "name": "Julien",
  "favouriteColors": ["blue", "white", "red"]
}
```

随后，该 JSON 响应通常会使用 Jackson 之类的库反序列化为 Java 对象。

## 创建 `AzureOpenAiStreamingChatModel` 以流式获取结果

此实现与上面的 `AzureOpenAiChatModel` 类似，但它会逐 token 流式返回响应。

### 纯 Java
```java
StreamingChatModel model = AzureOpenAiStreamingChatModel.builder()
        .endpoint(System.getenv("AZURE_OPENAI_URL"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .deploymentName("gpt-4o")
        ...
        .build();
```

### Spring Boot
在 `application.properties` 中添加：
```properties
langchain4j.azure-open-ai.streaming-chat-model.endpoint=${AZURE_OPENAI_URL}
langchain4j.azure-open-ai.streaming-chat-model.service-version=...
langchain4j.azure-open-ai.streaming-chat-model.api-key=${AZURE_OPENAI_KEY}
langchain4j.azure-open-ai.streaming-chat-model.deployment-name=gpt-4o
langchain4j.azure-open-ai.streaming-chat-model.max-completion-tokens=...
langchain4j.azure-open-ai.streaming-chat-model.max-tokens=...
langchain4j.azure-open-ai.streaming-chat-model.temperature=...
langchain4j.azure-open-ai.streaming-chat-model.top-p=...
langchain4j.azure-open-ai.streaming-chat-model.logit-bias=...
langchain4j.azure-open-ai.streaming-chat-model.user=...
langchain4j.azure-open-ai.streaming-chat-model.stop=...
langchain4j.azure-open-ai.streaming-chat-model.presence-penalty=...
langchain4j.azure-open-ai.streaming-chat-model.frequency-penalty=...
langchain4j.azure-open-ai.streaming-chat-model.seed=...
langchain4j.azure-open-ai.streaming-chat-model.timeout=...
langchain4j.azure-open-ai.streaming-chat-model.max-retries=...
langchain4j.azure-open-ai.streaming-chat-model.log-requests-and-responses=...
langchain4j.azure-open-ai.streaming-chat-model.user-agent-suffix=...
langchain4j.azure-open-ai.streaming-chat-model.customHeaders=...
langchain4j.azure-open-ai.streaming-chat-model.reasoningEffort=...
```

## 音频转录

Azure OpenAI 现已支持音频转录，你可以使用托管在 Azure 上的先进模型，将音频文件中的口语转换为文本。

### Maven 依赖

音频转录功能包含在主包 `langchain4j-azure-open-ai` 中：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-azure-open-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

### 纯 Java 用法

你可以使用 `AzureOpenAiAudioTranscriptionModel` 转录音频文件：

```java
import dev.langchain4j.data.audio.Audio;
import dev.langchain4j.model.audio.AudioTranscriptionRequest;
import dev.langchain4j.model.audio.AudioTranscriptionResponse;
import java.io.File;
import java.nio.file.Files;

AzureOpenAiAudioTranscriptionModel model = AzureOpenAiAudioTranscriptionModel.builder()
    .endpoint(System.getenv("AZURE_OPENAI_URL"))
    .apiKey(System.getenv("AZURE_OPENAI_KEY"))
    .deploymentName("your-audio-model-deployment-name") // e.g., "whisper"
    .build();

// Read audio file as binary data
File audioFile = new File("path/to/audio-file.wav");
byte[] audioData = Files.readAllBytes(audioFile.toPath());

// Create Audio object with binary data
Audio audio = Audio.builder()
    .binaryData(audioData)
    .build();

// Create transcription request
AudioTranscriptionRequest request = AudioTranscriptionRequest.builder()
    .audio(audio)
    .prompt("This is an audio file containing ...") // optional
    .language("en") // optional
    .temperature(0.0) // optional
    .build();

// Transcribe audio
AudioTranscriptionResponse response = model.transcribe(request);
String transcript = response.text();
System.out.println(transcript);
```

### 说明

- **部署**：你必须在 Azure OpenAI 资源中部署一个音频转录模型（如 Whisper）。详情请参阅 [Azure OpenAI 文档](https://learn.microsoft.com/en-us/azure/ai-services/openai/)。
- **支持的格式**：支持 WAV、MP3、FLAC 等常见音频格式。
- **配额与定价**：音频转录会消耗你 Azure 订阅的资源。请在 Azure portal 中查看适用的配额和定价。

## 示例

- [Azure OpenAI 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/azure-open-ai-examples/src/main/java)
- [AzureOpenAiSecurityExamples](https://github.com/langchain4j/langchain4j-examples/blob/main/azure-open-ai-examples/src/main/java/AzureOpenAiSecurityExamples.java) 及其 [Azure CLI 部署脚本](https://github.com/langchain4j/langchain4j-examples/blob/main/azure-open-ai-examples/src/main/script/deploy-azure-openai-security.sh)
