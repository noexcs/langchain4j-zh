# Google AI Gemini

https://ai.google.dev/gemini-api/docs

## 目录

- [Maven 依赖](#maven-依赖)
- [API 密钥](#api-密钥)
- [可用模型](#可用模型)
- [GoogleAiGeminiChatModel](#googleaigeminichatmodel)
    - [配置](#配置)
    - [默认请求参数](#默认请求参数)
- [GoogleAiGeminiStreamingChatModel](#googleaigeministreamingchatmodel)
- [安全设置与安全评级](#安全设置与安全评级)
- [工具](#工具)
- [结构化输出](#结构化输出)
- [Python 代码执行](#python-代码执行)
- [多模态](#多模态)
- [思考](#思考)
    - [Gemini 3 Pro](#gemini-3-pro)
- [Gemini Files API](#gemini-files-api)
    - [上传文件](#上传文件)
    - [管理文件](#管理文件)
    - [文件状态](#文件状态)
- [上下文缓存](#上下文缓存)
- [批处理](#批处理)
    - [GoogleAiBatchChatModel](#googleaibatchchatmodel)
    - [创建批处理任务](#创建批处理任务)
    - [处理批处理响应](#处理批处理响应)
    - [轮询结果](#轮询结果)
    - [管理批处理任务](#管理批处理任务)
    - [基于文件的批处理](#基于文件的批处理)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-google-ai-gemini</artifactId>
    <version>1.22.0</version>
</dependency>
```

## API 密钥

可在此免费获取 API 密钥：https://ai.google.dev/gemini-api/docs/api-key 。

## 可用模型

请参阅文档中的[可用模型列表](https://ai.google.dev/gemini-api/docs/models/gemini)。

* `gemini-3-pro-preview`
* `gemini-2.5-pro`
* `gemini-2.5-flash`
* `gemini-2.5-flash-lite`
* `gemini-2.0-flash`
* `gemini-2.0-flash-lite`

## GoogleAiGeminiChatModel

可以使用常规的 `chat(...)` 方法：

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    ...
    .build();

String response = gemini.chat("Hello Gemini!");
```

也可以使用 `ChatResponse chat(ChatRequest req)` 方法：

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

ChatResponse chatResponse = gemini.chat(ChatRequest.builder()
    .messages(UserMessage.from(
        "How many R's are there in the word 'strawberry'?"))
    .build());

String response = chatResponse.aiMessage().text();
```

### 配置

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .httpClientBuilder(...)
    .defaultRequestParameters(...)
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .baseUrl(...)
    .modelName("gemini-2.5-flash")
    .maxRetries(...)
    .temperature(1.0)
    .topP(0.95)
    .topK(64)
    .seed(42)
    .frequencyPenalty(...)
    .presencePenalty(...)
    .maxOutputTokens(8192)
    .timeout(Duration.ofSeconds(60))
    .responseFormat(ResponseFormat.JSON) // or .responseFormat(ResponseFormat.builder()...build()) 
    .stopSequences(List.of(...))
    .toolConfig(GeminiFunctionCallingConfig.builder()...build()) // or below
    .toolConfig(GeminiMode.ANY, List.of("fnOne", "fnTwo"))
    .allowCodeExecution(true)
    .includeCodeExecution(true)
    .logRequestsAndResponses(true)
    .safetySettings(List<GeminiSafetySetting> or Map<GeminiHarmCategory, GeminiHarmBlockThreshold>)
    .thinkingConfig(...)
    .returnThinking(true)
    .sendThinking(true)
    .responseLogprobs(...)
    .logprobs(...)
    .enableEnhancedCivicAnswers(...)
    .mediaResolution(GeminiMediaResolutionLevel.MEDIA_RESOLUTION_HIGH)
    .mediaResolutionPerPartEnabled(true)
    .listeners(...)
    .supportedCapabilities(...)
    .build();
```

### 默认请求参数

除了（或替代）上面展示的各个独立的构建器方法，你还可以通过 `defaultRequestParameters(...)` 提供一个单独的
`ChatRequestParameters` 对象。这些参数将应用于模型发出的每个请求，除非被单个 `ChatRequest` 的参数所覆盖。

你可以传入通用的 `ChatRequestParameters`，也可以传入 Gemini 专用的 `GoogleAiGeminiChatRequestParameters`。
后者额外暴露了 Gemini 独有的选项，例如 `aspectRatio` 和 `imageSize`：

```java
GoogleAiGeminiChatRequestParameters parameters = GoogleAiGeminiChatRequestParameters.builder()
    .modelName("gemini-2.5-flash")
    .temperature(1.0)
    .maxOutputTokens(8192)
    .aspectRatio("16:9") // Gemini-specific
    .imageSize("2K")     // Gemini-specific
    .build();

ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .defaultRequestParameters(parameters)
    .build();
```

当同一个参数既通过 `defaultRequestParameters(...)` 设置，又通过独立的构建器方法
（例如 `modelName(String)`）设置时，独立构建器方法设置的值优先：

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .defaultRequestParameters(GoogleAiGeminiChatRequestParameters.builder()
        .modelName("gemini-2.5-flash")
        .temperature(1.0)
        .build())
    .temperature(0.0) // overrides temperature from defaultRequestParameters
    .build();
// effective parameters: modelName=gemini-2.5-flash, temperature=0.0
```

## GoogleAiGeminiStreamingChatModel
`GoogleAiGeminiStreamingChatModel` 允许逐 token 流式输出响应文本。
响应必须由 `StreamingChatResponseHandler` 处理。
```java
StreamingChatModel gemini = GoogleAiGeminiStreamingChatModel.builder()
        .apiKey(System.getenv("GEMINI_AI_KEY"))
        .modelName("gemini-2.5-flash")
        .build();

CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();

gemini.chat("Tell me a joke about Java", new StreamingChatResponseHandler() {

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
```

## 安全设置与安全评级

Gemini 会基于一系列危害类别（例如
`HARM_CATEGORY_HARASSMENT` 或 `HARM_CATEGORY_DANGEROUS_CONTENT`）检查你发送的提示词及其生成的内容。

你可以通过模型构建器上的 `safetySettings(...)` 控制这些检查的严格程度：

```java
ChatModel model = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .safetySettings(Map.of(
        GeminiHarmCategory.HARM_CATEGORY_HARASSMENT, GeminiHarmBlockThreshold.BLOCK_ONLY_HIGH,
        GeminiHarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, GeminiHarmBlockThreshold.BLOCK_LOW_AND_ABOVE))
    .build();
```

Gemini 会在响应中报告这些检查的结果。要读取它，请将 `ChatResponse.metadata()` 转换为
`GoogleAiGeminiChatResponseMetadata`：

```java
ChatResponse chatResponse = model.chat(ChatRequest.builder()
    .messages(UserMessage.from("Hello!"))
    .build());

var metadata = (GoogleAiGeminiChatResponseMetadata) chatResponse.metadata();

// how the generated content was rated
for (GeminiSafetyRating rating : metadata.safetyRatings()) {
    System.out.println(rating.category() + " -> " + rating.probability());
}
```

有三项可用信息：

| 方法                  | 含义                                                                            |
|-------------------------|------------------------------------------------------------------------------------|
| `safetyRatings()`       | **生成的内容**的评级，每个危害类别一个条目。若无则为空。 |
| `promptSafetyRatings()` | **你的提示词**的评级。若无则为空。                                        |
| `blockReason()`         | Gemini 直接拒绝该提示词的原因；若未拒绝则为 `null`。                     |

当 Gemini 拒绝某个提示词时，它不会返回任何内容。在这种情况下，`blockReason()` 会被设置（例如
`"SAFETY"`、`"PROHIBITED_CONTENT"` 或 `"BLOCKLIST"`），`AiMessage` 不包含文本，且 `finishReason()` 为
`CONTENT_FILTER`：

```java
var metadata = (GoogleAiGeminiChatResponseMetadata) chatResponse.metadata();

if (metadata.blockReason() != null) {
    System.out.println("Prompt was rejected: " + metadata.blockReason());
    metadata.promptSafetyRatings().forEach(rating ->
            System.out.println("  " + rating.category() + ": " + rating.probability()));
}
```

`GeminiSafetyRating.category()` 和 `probability()` 是持有原始 API 值的普通 `String`，因此
Google 日后引入的危害类别会被原样传递，而不会导致你的应用出错。

`GoogleAiGeminiStreamingChatModel`（在传递给
`onCompleteResponse` 的 `ChatResponse` 上）和 `GoogleAiGeminiBatchChatModel` 也可获取相同的数据。

## 工具

支持工具（又称函数调用），包括并行调用。
你可以使用接受 `ChatRequest` 的 `chat(ChatRequest)` 方法，通过配置
一个或多个 `ToolSpecification`，让 Gemini 知道它可以请求调用某个函数。
也可以使用 LangChain4j 的 `AiServices` 来定义它们。

下面是一个使用 `AiServices` 的天气工具示例：

```java
record WeatherForecast(
    String location,
    String forecast,
    int temperature) {}

class WeatherForecastService {
    @Tool("Get the weather forecast for a location")
    WeatherForecast getForecast(
        @P("Location to get the forecast for") String location) {
        if (location.equals("Paris")) {
            return new WeatherForecast("Paris", "sunny", 20);
        } else if (location.equals("London")) {
            return new WeatherForecast("London", "rainy", 15);
        } else if (location.equals("Tokyo")) {
            return new WeatherForecast("Tokyo", "warm", 32);
        } else {
            return new WeatherForecast("Unknown", "unknown", 0);
        }
    }
}

interface WeatherAssistant {
    String chat(String userMessage);
}

WeatherForecastService weatherForecastService =
    new WeatherForecastService();

ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .temperature(0.0)
    .build();

WeatherAssistant weatherAssistant =
    AiServices.builder(WeatherAssistant.class)
        .chatModel(gemini)
        .tools(weatherForecastService)
        .build();

String tokyoWeather = weatherAssistant.chat(
        "What is the weather forecast for Tokyo?");

System.out.println("Gemini> " + tokyoWeather);
// Gemini> The weather forecast for Tokyo is warm
//         with a temperature of 32 degrees.
```

### 使用 `$ref`、`$defs` 或原始 JSON Schema 的工具参数

工具参数通常使用 Gemini 的 `parameters` 字段进行描述，该字段能理解一组固定的
schema 关键字。标准 JSON Schema 走得更远：它可以用 `$ref` 和 `$defs` 让文档的某一部分指向另一部分，
还具有 `parameters` 没有位置容纳的 `minimum` 和 `maximum` 等关键字。

当工具参数中包含这类内容时，LangChain4j 会改用以接受原始 JSON Schema 的
Gemini 字段 `parametersJsonSchema` 来发送它们，schema 会原样到达 API。
你无需配置任何东西，也无需打开任何开关：

```java
JsonObjectSchema priceRange = JsonObjectSchema.builder()
        .addNumberProperty("min")
        .addNumberProperty("max")
        .build();

ToolSpecification searchProducts = ToolSpecification.builder()
        .name("search_products")
        .description("Search the catalog")
        .parameters(JsonObjectSchema.builder()
                .definitions(Map.of("PriceRange", priceRange))
                .addStringProperty("query")
                // a reference to the definition above, resolved by Gemini
                .addProperty("retail_price", JsonReferenceSchema.builder()
                        .reference("PriceRange")
                        .build())
                // a fragment of JSON Schema, sent exactly as written
                .addProperty("max_results", JsonRawSchema.from(
                        "{\"type\":\"integer\",\"minimum\":1,\"maximum\":50}"))
                .required("query")
                .build())
        .build();
```

这并不限于你手写的 schema，也覆盖 LangChain4j 为你构建的工具：参数类型自引用的 `@Tool`
方法，以及 schema 使用 `$ref` 的 MCP 工具。

响应 schema 也采用相同处理方式，参见[原始响应 Schema](#原始响应-schema)。

!!! note
    Gemini 会拒绝 `$schema` 关键字。由 schema 生成器输出的文档通常以
    `"$schema": "https://json-schema.org/draft/2020-12/schema"` 开头，因此在将文档传给
    `JsonRawSchema` 之前请删掉该行，否则请求会因 `400` 而失败。

## 结构化输出

有关结构化输出的更多信息，请参见[此处](../../tutorials/structured-outputs.md)。

### 从自由文本中进行类型安全的数据提取
大语言模型非常擅长从非结构化文本中提取结构化信息。
在下面的示例中，借助 `AiServices`，我们从一段天气预报文本中获取了一个类型安全的 `WeatherForecast` 对象：
```java
// A type-safe / strongly-typed object 
// representing the weather forecast

record WeatherForecast(
    @Description("minimum temperature")
    Integer minTemperature,
    @Description("maximum temperature")
    Integer maxTemperature,
    @Description("chances of rain")
    boolean rain
) { }

// An interface contract, to interact with Gemini

interface WeatherForecastAssistant {
    WeatherForecast extract(String forecast);
}

// Let's extract the data:

ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // this is required to enable structured outputs feature
    .build();

WeatherForecastAssistant forecastAssistant =
    AiServices.builder(WeatherForecastAssistant.class)
        .chatModel(gemini)
        .build();

WeatherForecast forecast = forecastAssistant.extract("""
    Morning: The day dawns bright and clear in Osaka, with crisp
    autumn air and sunny skies. Expect temperatures to hover
    around 18°C (64°F) as you head out for your morning stroll
    through Namba.
    Afternoon: The sun continues to shine as the city buzzes with
    activity. Temperatures climb to a comfortable 22°C (72°F).
    Enjoy a leisurely lunch at one of Osaka's many outdoor cafes,
    or take a boat ride on the Okawa River to soak in the beautiful
    scenery.
    Evening: As the day fades, expect clear skies and a slight chill
    in the air. Temperatures drop to 15°C (59°F). A cozy dinner at a
    traditional Izakaya will be the perfect way to end your day in
    Osaka.
    Overall: A beautiful autumn day in Osaka awaits, perfect for
    exploring the city's vibrant streets, enjoying the local cuisine,
    and soaking in the sights.
    Don't forget: Pack a light jacket for the evening and wear
    comfortable shoes for all the walking you'll be doing.
    """);
```

### 响应格式 / 响应 Schema
你可以在创建 `GoogleAiGeminiChatModel` 时或调用它时指定 `ResponseFormat`。

特别是对于 JSON 格式，你可以通过创建相应的 Java 对象以编程方式定义 schema，也可以直接提供原始 JSON schema。 
#### 响应 Schema
下面看一下在创建 `GoogleAiGeminiChatModel` 时如何为一份食谱定义 JSON schema 的示例。
在这个示例中，我们使用 `JsonObjectSchema` 类来声明 JSON schema。
```java
ResponseFormat responseFormat = ResponseFormat.builder()
        .type(ResponseFormatType.JSON)
        .jsonSchema(JsonSchema.builder() // see [1] below
                .rootElement(JsonObjectSchema.builder()
                        .addStringProperty("title")
                        .addIntegerProperty("preparationTimeMinutes")
                        .addProperty("ingredients", JsonArraySchema.builder()
                                .items(new JsonStringSchema())
                                .build())
                        .addProperty("steps", JsonArraySchema.builder()
                                .items(new JsonStringSchema())
                                .build())
                        .build())
                .build())
        .build();

ChatModel gemini = GoogleAiGeminiChatModel.builder()
        .apiKey(System.getenv("GEMINI_AI_KEY"))
        .modelName("gemini-2.5-flash")
        .responseFormat(responseFormat)
        .build();

String recipeResponse = gemini.chat("Suggest a dessert recipe with strawberries");

System.out.println(recipeResponse);
```
说明：
- [1] - 可以使用 `JsonSchemas.jsonSchemaFrom()` 辅助方法从你的类自动生成 `JsonSchema`。
```java
JsonSchema jsonSchema = JsonSchemas.jsonSchemaFrom(TripItinerary.class).get();
```

下面看一下在调用 `GoogleAiGeminiChatModel` 时如何为一份食谱定义 JSON schema 的示例：
```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
        .apiKey(System.getenv("GEMINI_AI_KEY"))
        .modelName("gemini-2.5-flash")
        .build();

ResponseFormat responseFormat = ...;

ChatRequest chatRequest = ChatRequest.builder()
        .messages(UserMessage.from("Suggest a dessert recipe with strawberries"))
        .responseFormat(responseFormat)
        .build();

ChatResponse chatResponse = gemini.chat(chatRequest);

System.out.println(chatResponse.aiMessage().text());
```

#### 原始响应 Schema
另一个示例展示了如何使用 Gemini API 的 `responseJsonSchema`，通过 `JsonRawSchema` 类提供原始 JSON schema。  
请注意，只能使用 Gemini API 的[支持的数据类型](https://ai.google.dev/gemini-api/docs/structured-output?example=recipe#json_schema_support)。
只要响应 schema 内部任何位置包含 `JsonRawSchema` 或 `JsonReferenceSchema`，就会使用同一个字段，因此 `$ref` 和 `$defs` 在这里同样有效。
```
String rawSchema = """
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string"
    },
    "birthDate": {
      "type": "string",
      "format": "date"
    },
    "preferredContactTime": {
      "type": "string",
      "format": "time"
      },
    "height": {
      "type": "number",
      "minimum": 1.83,
      "maximum": 1.88
    },
    "role": {
      "type": "string",
      "enum": ["developer", "maintainer", "researcher"]
    },
    "isAvailable": { "type": "boolean" },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1,
      "maxItems": 5
    },
    "address": {
      "type": "object",
      "properties": {
        "city": { "type": "string" },
        "streetName": { "type": "string" },
        "streetNumber": { "type": "string" }
      },
      "required": ["city", "streetName", "streetNumber"],
      "additionalProperties": true
    }
  },
  "required": ["name", "birthDate", "height", "role", "tags", "address"]
}
""";

JsonRawSchema jsonRawSchema = JsonRawSchema.builder().schema(rawSchema).build();
JsonSchema jsonSchema = JsonSchema.builder().rootElement(jsonRawSchema).build();
        
ResponseFormat responseFormat = ResponseFormat.builder()
        .type(ResponseFormatType.JSON)
        .jsonSchema(jsonSchema)
        .build();

GoogleAiGeminiChatModel gemini = GoogleAiGeminiChatModel.builder()
        .apiKey(GOOGLE_AI_GEMINI_API_KEY)
        .modelName("gemini-2.5-flash-lite")
        .logRequests(true)
        .logResponses(true)
        .responseFormat(responseFormat)
        .build();
        
UserMessage userMessage = UserMessage.from(
        """
           Tell me about a detective named Sherlock Holmes,
           who was born on November 28 1852 and sees the world over six feet from the ground.
           He is a trouble-seeker, an active volunteer and lives in London at 221B Baker Street.
           He plays the violin and he likes to conduct various physics and chemistry experiments.
           He accepts clients or prefers to be contacted at 09:00am.
           """);

ChatResponse response = gemini.chat(ChatRequest.builder()
        .messages(userMessage)
        .build());
```
### JSON 模式

你可以强制 Gemini 以 JSON 格式回复：

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .responseFormat(ResponseFormat.JSON)
    .build();

String roll = gemini.chat("Roll a 6-sided dice");

System.out.println(roll);
// {"roll": "3"}
```

系统提示词可以进一步描述 JSON 输出应有的样子。
Gemini 通常会遵循建议的 schema，但这并不保证。
如果你希望确保 JSON schema 被应用，应如上一节所述定义响应格式。


## Python 代码执行

除了函数调用之外，Google AI Gemini 还允许你在沙箱环境中创建并执行 Python 代码。
在需要更复杂的计算或逻辑的场景中，这一点尤为有用。

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .allowCodeExecution(true)
    .includeCodeExecutionOutput(true)
    .build();
```

有两个构建器方法：
* `allowCodeExecution(true)`：让 Gemini 知道它可以编写并执行 Python 代码
* `includeCodeExecutionOutput(true)`：如果你希望看到它实际生成的 Python 脚本及其执行输出

```java
ChatResponse mathQuizz = gemini.chat(
    SystemMessage.from("""
        You are an expert mathematician.
        When asked a math problem or logic problem,
        you can solve it by creating a Python program,
        and execute it to return the result.
        """),
    UserMessage.from("""
        Implement the Fibonacci and Ackermann functions.
        What is the result of `fibonacci(22)` - ackermann(3, 4)?
        """)
);
```

Gemini 会编写一段 Python 脚本，在其服务器上执行，并返回结果。
由于我们要求查看执行代码和输出，回答将如下所示：

~~~
Code executed:
```python
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def ackermann(m, n):
    if m == 0:
        return n + 1
    elif n == 0:
        return ackermann(m - 1, 1)
    else:
        return ackermann(m - 1, ackermann(m, n - 1))

print(fibonacci(22) - ackermann(3, 4))
```
Output:
```
17586
```
The result of `fibonacci(22) - ackermann(3, 4)` is **17586**.

I implemented the Fibonacci and Ackermann functions in Python.
Then I called `fibonacci(22) - ackermann(3, 4)` and printed the result.
~~~

如果我们没有要求代码/输出，则只会收到以下文本：

```
The result of `fibonacci(22) - ackermann(3, 4)` is **17586**.

I implemented the Fibonacci and Ackermann functions in Python.
Then I called `fibonacci(22) - ackermann(3, 4)` and printed the result.
```

## 多模态

Gemini 是一个多模态模型，这意味着它除了文本之外，还能接受并生成不同的_模态_。

### 输入模态

在输入方面，Gemini 接受：
* 图片（`ImageContent`）
* 视频（`VideoContent`）
* 音频文件（`AudioContent`）
* PDF 文件（`PdfFileContent`）

下面的示例展示了如何将文本提示词与图片混合：

```java
// PNG of the cute colorful parrot mascot of the LangChain4j project
String base64Img = b64encoder.encodeToString(readBytes(
  "https://avatars.githubusercontent.com/u/132277850?v=4"));

ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

ChatResponse response = gemini.chat(
    UserMessage.from(
        ImageContent.from(base64Img, "image/png"),
        TextContent.from("""
            Do you think this logo fits well
            with the project description?
            """)
    )
);
```

### 图像生成输出

某些 Gemini 模型（例如 `gemini-2.5-flash-image`）可以生成图像作为响应的一部分。当图像被生成后，它们会被存储在 `AiMessage` 属性中，并可以使用 `GeneratedImageHelper` 工具类进行访问。

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey("Your API Key")
    .modelName("gemini-2.5-flash-image")
    .build();

ChatResponse response = gemini.chat(UserMessage.from("A high-resolution, studio-lit product photograph of a minimalist ceramic coffee mug in matte black"));

// Extract generated images from the response
AiMessage aiMessage = response.aiMessage();
List<Image> generatedImages = GeneratedImageHelper.getGeneratedImages(aiMessage);

if (GeneratedImageHelper.hasGeneratedImages(aiMessage)) {
    System.out.println("Generated " + generatedImages.size() + " image(s)");
    System.out.println("Text response: " + aiMessage.text());

    for (Image image : generatedImages) {
        String base64Data = image.base64Data();
        String mimeType = image.mimeType();
        
        // You can now save the image, display it, or process it further
        // For example, save to file:
        byte[] imageBytes = Base64.getDecoder().decode(base64Data);
        Files.write(Paths.get("generated_image.png"), imageBytes);
    }
} else {
    System.out.println("Text response: " + aiMessage.text());
}
```

### 媒体分辨率

你可以控制发送给模型的媒体（图像、视频、PDF）的分辨率。这可以全局设置，也可以按部分（按图像）设置。

#### 全局媒体分辨率

要为请求中所有媒体部分设置媒体分辨率，请使用 `.mediaResolution()` 构建器方法：

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .mediaResolution(GeminiMediaResolutionLevel.MEDIA_RESOLUTION_LOW) // or MEDIUM, HIGH, ULTRA_HIGH, UNSPECIFIED
    .build();
```

#### 按部分的媒体分辨率（Gemini 3）

使用 Gemini 3 时，你可以使用 `ImageContent` 中的 `DetailLevel` 为单独的图像指定分辨率。
首先，在构建器中启用此功能，然后在 `ImageContent` 上设置详细级别：

```java
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-3-pro-preview")
    .mediaResolutionPerPartEnabled(true)
    .build();

ChatResponse response = gemini.chat(
    UserMessage.from(
        ImageContent.from(url1, ImageContent.DetailLevel.LOW),
        ImageContent.from(url2, ImageContent.DetailLevel.HIGH),
        TextContent.from("Compare these two images")
    )
);
```

支持的 `DetailLevel` 值及其到 Gemini 分辨率级别的映射：
- `LOW` -> `MEDIA_RESOLUTION_LOW`
- `MEDIUM` -> `MEDIA_RESOLUTION_MEDIUM`
- `HIGH` -> `MEDIA_RESOLUTION_HIGH`
- `ULTRA_HIGH` -> `MEDIA_RESOLUTION_ULTRA_HIGH`（token 数量最高，特定用例（如 computer use）所需）
- `AUTO` -> `MEDIA_RESOLUTION_UNSPECIFIED`

## 思考

`GoogleAiGeminiChatModel` 和 `GoogleAiGeminiStreamingChatModel`
均支持[思考](https://ai.google.dev/gemini-api/docs/thinking)。

以下参数也控制思考行为：
- `GeminiThinkingConfig.includeThoughts` 和 `thinkingBudget`：启用思考，更多详情见[此处](https://ai.google.dev/gemini-api/docs/thinking)。
- `returnThinking`：控制是否返回思考内容（如果可用），存放在 `AiMessage.thinking()` 中，
  以及在使用 `GoogleAiGeminiStreamingChatModel` 时是否调用 `StreamingChatResponseHandler.onPartialThinking()` 和 `TokenStream.onPartialThinking()`
  回调。
  默认禁用。如果启用，thinking 签名也会存储在 `AiMessage.attributes()` 中并返回。
- `sendThinking`：控制在后续请求中是否将存储在 `AiMessage` 中的思考内容和签名发送给 LLM。
- 默认禁用。

!!! note
    请注意，当 `returnThinking` 未设置（为 `null`）且设置了 `thinkingConfig` 时，
    思考文本会被前置到 `AiMessage.text()` 字段中的实际响应之前，
    并且将调用 `StreamingChatResponseHandler.onPartialResponse()`，
    而不是 `StreamingChatResponseHandler.onPartialThinking()`。

下面是一个配置思考的示例：
```java
GeminiThinkingConfig thinkingConfig = GeminiThinkingConfig.builder()
        .includeThoughts(true)
        .thinkingBudget(250)
        .build();

ChatModel model = GoogleAiGeminiChatModel.builder()
        .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
        .modelName("gemini-2.5-flash")
        .thinkingConfig(thinkingConfig)
        .returnThinking(true)
        .sendThinking(true)
        .build();
```

### Gemini 3 Pro

在 Gemini 3 Pro 中，思考配置引入了_思考级别_，取值为 `"low"` 或 `"high"`（默认为 high）。
可以在思考配置中设置该级别：
```java
GoogleAiGeminiChatModel modelHigh = GoogleAiGeminiChatModel.builder()
        .modelName("gemini-3-pro-preview")
        .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
        .thinkingConfig(GeminiThinkingConfig.builder()
                .thinkingLevel(LOW) // or HIGH
                .build())
        .sendThinking(true)
        .returnThinking(true)
        .build();
```

你可以传入字符串 `"high"` / `"low"`，也可以传入 `GeminiThinkingConfig.GeminiThinkingLevel.HIGH`
/ `GeminiThinkingConfig.GeminiThinkingLevel.LOW` 枚举值。

使用 Gemini 3 Pro 时，必须将 `sendThinking()` 和 `returnThinking()` 配置为 `true`，
以确保[思考签名](https://ai.google.dev/gemini-api/docs/thought-signatures)能够正确地传递给模型。

## Gemini Files API

Gemini Files API 允许你上传和管理媒体文件，供 Gemini 模型使用。当你的请求总大小超过 20 MB 时，这尤其有用，因为文件可以单独上传，并在你的内容生成请求中引用。

### 主要特性

- **多模态支持**：上传图片、音频、视频和文档
- **存储**：文件存储 48 小时
- **容量**：每个项目最多 20 GB 文件，单个文件最大 2 GB
- **免费**：Files API 免费使用

### 上传文件

你可以通过两种方式上传文件：

**从文件路径：**

```java
GeminiFiles filesApi = GeminiFiles.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .build();

// Upload from a file path
Path filePath = Paths.get("path/to/your/file.pdf");
GeminiFile uploadedFile = filesApi.uploadFile(filePath, "My Document");

System.out.println("File uploaded: " + uploadedFile.name());
System.out.println("File URI: " + uploadedFile.uri());
```

**从字节数组：**

```java
byte[] fileBytes = Files.readAllBytes(Paths.get("path/to/file.jpg"));
GeminiFile uploadedFile = filesApi.uploadFile(
    fileBytes,
    "image/jpeg",
    "My Image"
);
```

### 管理文件

**列出所有已上传的文件：**

```java
List<GeminiFile> files = filesApi.listFiles();
for (GeminiFile file : files) {
    System.out.println("File: " + file.displayName() + " (" + file.name() + ")");
}
```

**获取文件元数据：**

```java
GeminiFile file = filesApi.getMetadata("files/abc123");
System.out.println("File size: " + file.sizeBytes() + " bytes");
System.out.println("MIME type: " + file.mimeType());
System.out.println("Created: " + file.createTime());
System.out.println("Expires: " + file.expirationTime());
```

**删除文件：**

```java
filesApi.deleteFile("files/abc123");
System.out.println("File deleted successfully");
```

### 文件状态

文件在其生命周期中可以处于不同的状态：

```java
GeminiFile file = filesApi.getMetadata("files/abc123");

if (file.isActive()) {
    System.out.println("File is ready to use");
} else if (file.isProcessing()) {
    System.out.println("File is still being processed");
} else if (file.isFailed()) {
    System.out.println("File processing failed");
}
```

## 上下文缓存

[上下文缓存 API](https://ai.google.dev/gemini-api/docs/generate-content/caching) 将大型且频繁复用的上下文（系统指令、长文档）一次性存储在 Google 的服务器上，这样后续请求可以按名称引用它，而无需重新发送，从而降低输入 token 成本和延迟。

`GeminiCaches` 管理缓存的生命周期（创建 / 获取 / 列出 / 删除）。消息使用聊天模型所用的相同消息映射进行缓存，因此你始终处于 LangChain4j 的 `ChatMessage` 领域：

```java
GeminiCaches caches = GeminiCaches.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .build();

// Cache a large, reusable context (a system instruction plus a long document)
GeminiCachedContent cache = caches.createCache(
    "gemini-2.5-flash",
    List.of(
        SystemMessage.from("You are a precise assistant answering questions about the attached document."),
        UserMessage.from(longDocumentText)),
    Duration.ofHours(1));

// Reuse it across many requests via cachedContentName
ChatModel gemini = GoogleAiGeminiChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .cachedContentName(cache.name())
    .build();

String answer = gemini.chat("Summarize the cached document in 3 bullet points.");

// Manage the cache lifecycle
caches.getCache(cache.name());
caches.listCaches();
caches.deleteCache(cache.name());
```

`createCache` 有三种过期形式：不带过期参数时使用 API 默认值（目前为 1 小时）；带 `Duration` 时设置相对存活时间；带 `Instant` 时设置绝对过期时间。

> 注意：显式上下文缓存需要付费层级；免费层级不可用。

## 批处理

### GoogleAiBatchChatModel

`GoogleAiBatchChatModel` 提供了一个以更低成本（[标准定价的 50%](https://ai.google.dev/gemini-api/docs/batch-api)）异步处理大量聊天请求的接口。它非常适合具有 24 小时完成时限 SLO 的非紧急、大规模任务。

### 创建批处理任务

**内联批处理创建：**

```java
GoogleAiGeminiBatchChatModel batchModel = GoogleAiGeminiBatchChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

// Create batch requests
List<ChatRequest> requests = List.of(
    ChatRequest.builder()
        .messages(UserMessage.from("What is the capital of France?"))
        .build(),
    ChatRequest.builder()
        .messages(UserMessage.from("What is the capital of Germany?"))
        .build(),
    ChatRequest.builder()
        .messages(UserMessage.from("What is the capital of Italy?"))
        .build()
);

// Submit the batch (generic API, no Gemini-specific options)
BatchResponse<ChatResponse> response = batchModel.submit(new BatchRequest<>(requests));

// Or, to set a Gemini-specific display name and priority, use GeminiBatchRequest:
BatchResponse<ChatResponse> response = batchModel.submit(GeminiBatchRequest.from(
    requests,
    "Geography Questions Batch", // display name
    0L                           // priority (optional, defaults to 0)
));
```

**基于文件的批处理创建：**

对于更大的批次，或者当你需要更多控制请求格式时，可以从上传的文件创建批次：

```java
// First, upload a file with batch requests
GeminiFiles filesApi = GeminiFiles.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .build();

GeminiFile uploadedFile = filesApi.uploadFile(
    Paths.get("batch_chat_requests.jsonl"),
    "Batch Chat Requests"
);

// Wait for file to be active
while (uploadedFile.isProcessing()) {
    Thread.sleep(1000);
    uploadedFile = filesApi.getMetadata(uploadedFile.name());
}

// Create batch from file
BatchResponse<ChatResponse> response = batchModel.submit("My Batch Job", uploadedFile);
```

### 处理批处理响应

`BatchResponse` 暴露当前的 `state()`，以及按请求划分的 `results()` 和
`responses()` / `errors()` 便捷视图。根据 `state()` 进行分支处理（使用 `state().isTerminal()`
判断批次是否仍在进行中）：

```java
BatchResponse<ChatResponse> response = batchModel.submit(new BatchRequest<>(requests));

if (!response.state().isTerminal()) {
    System.out.println("Batch is " + response.state());
    System.out.println("Batch ID: " + response.batchId());
} else if (response.state() == BatchState.SUCCEEDED) {
    System.out.println("Batch completed successfully!");

    // Process successful responses
    for (ChatResponse chatResponse : response.responses()) {
        System.out.println(chatResponse.aiMessage().text());
    }

    // Check for individual request errors within the batch
    if (!response.errors().isEmpty()) {
        System.out.println("Some requests failed:");
        for (BatchError error : response.errors()) {
            System.err.println("Error code: " + error.code() + ", message: " + error.message());
        }
    }
} else {
    System.err.println("Batch " + response.state() + ": " + response.errors());
}
```

**注意：** `state() == SUCCEEDED` 的批次表示批处理任务已完成，但批次内的单个
请求可能已失败。`errors()` 列表包含任何单个请求的
失败（例如超时、速率限制），而 `responses()` 包含成功的响应。
两者都是便捷视图，永远不会为 `null`（无内容可报告时为空），因此请检查
`!responses().isEmpty()` / `!errors().isEmpty()` 以优雅地处理部分失败。

### 将结果与请求对应

`responses()` 和 `errors()` 是扁平视图，无法跟踪哪个输入产生了哪个结果。
当你需要将每个结果映射回其来源请求时，请改用 `results()`：它
为每个请求返回一个 `BatchItemResult`，**与提交的请求顺序相同**，因此
第 i 个结果对应第 i 个请求。每个结果要么是 `BatchItemResult.Success`
（携带 `response()`），要么是 `BatchItemResult.Failure`（携带 `error()`）：

```java
BatchResponse<ChatResponse> result = batchModel.submit(new BatchRequest<>(requests));
// ... poll until terminal ...

List<BatchItemResult<ChatResponse>> results = result.results();
for (int i = 0; i < results.size(); i++) {
    BatchItemResult<ChatResponse> item = results.get(i);
    if (item.isSuccess()) {
        System.out.println("Request #" + i + " -> " + item.response().aiMessage().text());
    } else {
        BatchError error = item.error();
        System.err.println("Request #" + i + " failed: " + error.code() + " - " + error.message());
    }
}
```

### 轮询结果

由于批处理是异步的，你需要轮询获取结果（结果的处理最多可能需要 24 小时）：

```java
BatchResponse<ChatResponse> result = batchModel.submit(new BatchRequest<>(requests));
String batchId = result.batchId();

// Poll until the batch reaches a terminal state
while (!result.state().isTerminal()) {
    Thread.sleep(5000); // Wait 5 seconds between polls
    result = batchModel.retrieve(batchId);
}

// Process final result
if (result.state() == BatchState.SUCCEEDED) {
    System.out.println("Successful responses: " + result.responses().size());
    for (ChatResponse chatResponse : result.responses()) {
        System.out.println(chatResponse.aiMessage().text());
    }

    // Handle any individual request failures
    if (!result.errors().isEmpty()) {
        System.out.println("Failed requests: " + result.errors().size());
        for (BatchError error : result.errors()) {
            System.err.println("Error: " + error.code() + " - " + error.message());
        }
    }
} else {
    System.err.println("Batch did not succeed: " + result.state());
}
```

### 管理批处理任务

**取消批处理任务：**

```java
String batchId = // ... obtained from submit(...)

try {
    batchModel.cancel(batchId);
    System.out.println("Batch cancelled successfully");
} catch (HttpException e) {
    System.err.println("Failed to cancel batch: " + e.getMessage());
}
```

**删除批处理任务：**

```java
batchModel.deleteBatchJob(batchId);
System.out.println("Batch deleted successfully");
```

**列出批处理任务：**

```java
// List first page of batch jobs
BatchPage<ChatResponse> page = batchModel.list(new BatchPagination(10, null));

for (BatchResponse<ChatResponse> batch : page.batches()) {
    System.out.println("Batch: " + batch);
}

// Get next page if available
if (page.nextPageToken() != null) {
    BatchPage<ChatResponse> nextPage = batchModel.list(new BatchPagination(10, page.nextPageToken()));
}
```

### 基于文件的批处理

对于高级使用场景，你可以将批处理请求写入 JSONL 文件并上传：

```java
// Create a JSONL file with batch requests
Path batchFile = Files.createTempFile("batch", ".jsonl");

try (JsonLinesWriter writer = new StreamingJsonLinesWriter(batchFile)) {
    List<BatchFileRequest<ChatRequest>> fileRequests = List.of(
        new BatchFileRequest<>("request-1", ChatRequest.builder()
            .messages(UserMessage.from("Question 1"))
            .build()),
        new BatchFileRequest<>("request-2", ChatRequest.builder()
            .messages(UserMessage.from("Question 2"))
            .build())
    );
    
    batchModel.writeBatchToFile(writer, fileRequests);
}

// Upload the file
GeminiFiles filesApi = GeminiFiles.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .build();

GeminiFile uploadedFile = filesApi.uploadFile(batchFile, "Batch Chat Requests");

// Create batch from file
BatchResponse<ChatResponse> response = batchModel.submit("File-Based Chat Batch", uploadedFile);
```

### 批处理任务状态

`BatchState` 枚举表示批处理任务的可能状态：

- `PENDING`：批次已排队，等待处理
- `RUNNING`：批次正在处理中
- `SUCCEEDED`：批次成功完成（终止状态）
- `FAILED`：批处理失败（终止状态）
- `CANCELLED`：批次被用户取消（终止状态）
- `EXPIRED`：批次在完成前过期（终止状态）
- `UNSPECIFIED`：状态未知或未提供

对 `BatchResponse.state()` 使用 `BatchState.isTerminal()` 即可判断何时可以停止轮询。

### 设置批处理优先级

高优先级批次会先于低优先级批次处理。通过 `GeminiBatchRequest` 设置优先级：

```java
// High priority batch
BatchResponse<ChatResponse> highPriority = batchModel.submit(GeminiBatchRequest.from(
    urgentRequests, "Urgent Batch", 100L));

// Low priority batch
BatchResponse<ChatResponse> lowPriority = batchModel.submit(GeminiBatchRequest.from(
    backgroundRequests, "Background Batch", -50L));
```

### 配置

`GoogleAiGeminiBatchChatModel` 支持与 `GoogleAiGeminiChatModel` 相同的配置选项：

```java
GoogleAiGeminiBatchChatModel batchModel = GoogleAiGeminiBatchChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .temperature(0.7)
    .topP(0.95)
    .topK(40)
    .maxOutputTokens(2048)
    .maxRetries(3)
    .timeout(Duration.ofMinutes(5))
    .logRequestsAndResponses(true)
    .build();
```

### 重要约束

- **模型一致性**：批次中的所有请求必须使用相同的模型
- **大小限制**：内联 API 支持的请求总大小不超过 20MB
- **成本**：与实时请求相比，批处理提供 50% 的成本降低
- **处理时间**：24 小时 SLO，但完成速度通常快得多
- **使用场景**：最适合大规模、非紧急的任务，如数据预处理或评估


### 示例：完整工作流

```java
GoogleAiGeminiBatchChatModel batchModel = GoogleAiGeminiBatchChatModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-2.5-flash")
    .build();

// Prepare batch requests
List<ChatRequest> requests = new ArrayList<>();
for (int i = 0; i < 50; i++) {
    requests.add(ChatRequest.builder()
        .messages(UserMessage.from("Generate a creative story idea #" + i))
        .build());
}

// Submit batch
BatchResponse<ChatResponse> result = batchModel.submit(GeminiBatchRequest.from(
    requests, "Story Ideas Batch", 0L));
String batchId = result.batchId();

// Poll for completion
int attempts = 0;
int maxAttempts = 720; // 1 hour with 5-second intervals
while (!result.state().isTerminal()) {
    if (attempts++ >= maxAttempts) {
        throw new RuntimeException("Batch processing timeout");
    }
    Thread.sleep(5000);
    result = batchModel.retrieve(batchId);
    System.out.println("Status: " + result.state());
}

// Process results
if (result.state() == BatchState.SUCCEEDED) {
    System.out.println("Generated " + result.responses().size() + " stories");
    for (int i = 0; i < result.responses().size(); i++) {
        ChatResponse chatResponse = result.responses().get(i);
        System.out.println("Story #" + i + ": " + chatResponse.aiMessage().text());
    }

    // Report any failures
    if (!result.errors().isEmpty()) {
        System.err.println(result.errors().size() + " requests failed:");
        for (BatchError error : result.errors()) {
            System.err.println("  - Code " + error.code() + ": " + error.message());
        }
    }
} else {
    System.err.println("Batch did not succeed: " + result.state());
}
```

## 了解更多

如果你想了解更多关于 Google AI Gemini 模型的信息，请查看其
[文档](https://ai.google.dev/gemini-api/docs/models/gemini)。
