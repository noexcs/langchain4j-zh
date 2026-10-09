# AI 服务

到目前为止，我们一直在介绍 `ChatModel`、`ChatMessage`、`ChatMemory` 等底层组件。
在这一层面编程非常灵活，可以完全自由发挥，但这也迫使你编写大量样板代码。
由于基于 LLM 的应用通常需要多个组件协同工作，而不仅仅是单个组件
（例如提示词模板、聊天记忆、LLM、输出解析器、RAG 组件：嵌入模型和向量存储），
并且往往涉及多次交互，因此把所有这些组件编排起来变得更加繁琐。

我们希望你能专注于业务逻辑，而不是底层实现细节。
因此，LangChain4j 目前有两个可以在这方面提供帮助的高层概念：AI 服务（AI Services）和链（Chains）。

## 链（遗留（旧版））

链的概念源自 Python 的 LangChain（在 LCEL 引入之前）。
其思想是为每个常见用例（如聊天机器人、RAG 等）提供一个 `Chain`。
链将多个底层组件组合在一起，并编排它们之间的交互。
它们的主要问题是，当你需要自定义某些内容时，它们过于僵化。
LangChain4j 目前只实现了两个链（`ConversationalChain` 和 `ConversationalRetrievalChain`），
我们暂时没有计划增加更多。

## AI 服务

我们提出了另一个专为 Java 打造的解决方案，称为 AI 服务（AI Services）。
其思想是将与 LLM 和其他组件交互的复杂性隐藏在一个简单的 API 之后。

这种方法与 Spring Data JPA 或 Retrofit 非常相似：你以声明式的方式定义一个具有期望 API 的接口，
而 LangChain4j 会提供一个实现该接口的对象（代理）。
你可以把 AI 服务看作应用中服务层的一个组件。
它提供 _AI_ 服务。因此得名。

AI 服务处理最常见的操作：
- 为 LLM 格式化输入
- 解析来自 LLM 的输出

它们还支持更高级的功能：
- 聊天记忆
- 工具
- RAG

AI 服务可用于构建支持来回交互的有状态聊天机器人，
也可用于自动化那些每次对 LLM 的调用彼此隔离的流程。

让我们看一下最简单的 AI 服务。之后，我们将探索更复杂的示例。

## 最简单的 AI 服务

首先，我们定义一个只包含一个方法 `chat` 的接口，它接收 `String` 作为输入并返回 `String`。
```java
interface Assistant {

    String chat(String userMessage);
}
```

然后，我们创建底层组件。这些组件将在我们的 AI 服务内部被使用。
在这种情况下，我们只需要 `ChatModel`：
```java
ChatModel model = OpenAiChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName(GPT_4_O_MINI)
    .build();
```

最后，我们可以使用 `AiServices` 类来创建我们 AI 服务的实例：
```java
Assistant assistant = AiServices.create(Assistant.class, model);
```
!!! note
   在 [Quarkus](https://docs.quarkiverse.io/quarkus-langchain4j/dev/ai-services.html)
   和 [Spring Boot](spring-boot-integration.md#声明式-ai-服务的-spring-boot-starter) 应用中，
   自动配置会负责创建 `Assistant` bean。
   这意味着你不需要调用 `AiServices.create(...)`，只需在任何需要 `Assistant` 的地方直接注入/自动装配即可。

现在我们可以使用 `Assistant`：
```java
String answer = assistant.chat("Hello");
System.out.println(answer); // Hello, how can I help you?
```

## 它如何工作？

你把接口的 `Class` 和底层组件一起提供给 `AiServices`，
`AiServices` 会创建一个实现该接口的代理对象。
目前它使用反射，但我们也在考虑其他替代方案。
这个代理对象负责处理所有输入和输出的转换。
在这种情况下，输入是一个单独的 `String`，而我们使用的是以 `ChatMessage` 为输入的 `ChatModel`。
因此，`AiService` 会自动将其转换为 `UserMessage` 并调用 `ChatModel`。
由于 `chat` 方法的输出类型是 `String`，在 `ChatModel` 返回 `AiMessage` 之后，
它会在从 `chat` 方法返回之前被转换为 `String`。

## Quarkus 应用中的 AI 服务
[LangChain4j Quarkus 扩展](https://docs.quarkiverse.io/quarkus-langchain4j/dev/index.html)
极大地简化了在 Quarkus 应用中使用 AI 服务。

更多信息可以在[这里](https://docs.quarkiverse.io/quarkus-langchain4j/dev/ai-services.html)找到。

## Spring Boot 应用中的 AI 服务
[LangChain4j Spring Boot starter](spring-boot-integration.md#声明式-ai-服务的-spring-boot-starter)
极大地简化了在 Spring Boot 应用中使用 AI 服务。

## @SystemMessage

现在，我们来看一个更复杂的示例。
我们将强制 LLM 使用俚语回复 😉

这通常通过在 `SystemMessage` 中提供指令来实现。

```java
interface Friend {

    @SystemMessage("You are a good friend of mine. Answer using slang.")
    String chat(String userMessage);
}

Friend friend = AiServices.create(Friend.class, model);

String answer = friend.chat("Hello"); // Hey! What's up?
```

在这个示例中，我们添加了 `@SystemMessage` 注解，并附带了我们想要使用的系统提示词模板。
它会在幕后被转换为 `SystemMessage`，并与 `UserMessage` 一起发送给 LLM。

`@SystemMessage` 还可以从资源中加载提示词模板：
`@SystemMessage(fromResource = "my-prompt-template.txt")`

`@SystemMessage` 也可以声明在 AI 服务接口上，
在这种情况下，它将应用于该 AI 服务暴露的所有方法，包括继承的方法：

```java
@SystemMessage("You are a good friend of mine. Answer using slang.")
interface Friend {

    String chat(String userMessage);

    String chatAgain(String userMessage);
}
```

声明在方法上的 `@SystemMessage` 优先于声明在接口上的 `@SystemMessage`。
仅声明在父接口上的 `@SystemMessage` 不会被子 AI 服务接口继承。

### 系统消息提供商
系统消息也可以使用系统消息提供商动态定义：
```java
Friend friend = AiServices.builder(Friend.class)
    .chatModel(model)
    .systemMessageProvider(chatMemoryId -> "You are a good friend of mine. Answer using slang.")
    .build();
```
如你所见，你可以基于聊天记忆 ID（用户或会话）提供不同的系统消息。

### 系统消息转换器

系统消息转换器允许你在每次调用时动态修改系统消息，
即在其从 `@SystemMessage` 或 `systemMessageProvider` 解析出来之后、但在
[`chatRequestTransformer`](#编程式-chatrequest-重写) 运行之前。
当你需要无论系统消息最初如何配置，都要向其追加或前置内容时，这很有用。

```java
Friend friend = AiServices.builder(Friend.class)
    .chatModel(model)
    .systemMessageProvider(chatMemoryId -> "You are a good friend of mine. Answer using slang.")
    .systemMessageTransformer(systemMessage -> systemMessage + " Today's date is " + LocalDate.now() + ".")
    .build();
```

如果没有配置系统消息，转换器将接收到 `null`。

当你还需要访问调用上下文（例如方法名或其参数）时，
请使用接受 `InvocationContext` 的双参数重载：

```java
Friend friend = AiServices.builder(Friend.class)
    .chatModel(model)
    .systemMessageProvider(chatMemoryId -> "You are a good friend of mine. Answer using slang.")
    .systemMessageTransformer((systemMessage, context) ->
            systemMessage + " Tenant: " + context.invocationParameters().get("tenant") + ".")
    .build();
```

## @UserMessage

现在，假设我们使用的模型不支持系统消息，
或者我们就是想用 `UserMessage` 来实现这一目的。
```java
interface Friend {

    @UserMessage("You are a good friend of mine. Answer using slang. {{it}}")
    String chat(String userMessage);
}

Friend friend = AiServices.create(Friend.class, model);

String answer = friend.chat("Hello"); // Hey! What's shakin'?
```
我们把 `@SystemMessage` 注解替换成了 `@UserMessage`，
并指定了一个包含变量 `it` 的提示词模板，该变量引用唯一的方法参数。

你也可以用 `@V` 注解 `String userMessage`，
并为提示词模板变量指定一个自定义名称：
```java
interface Friend {

    @UserMessage("You are a good friend of mine. Answer using slang. {{message}}")
    String chat(@V("message") String userMessage);
}
```

!!! note
   请注意，在 Quarkus 或 Spring Boot 中使用 LangChain4j 时，无需使用 `@V`。
   只有在 Java 编译期间未启用 `-parameters` 选项时，才需要该注解。

`@UserMessage` 还可以从资源中加载提示词模板：
`@UserMessage(fromResource = "my-prompt-template.txt")`

## 编程式 ChatRequest 重写

在某些情况下，在 `ChatRequest` 发送给 LLM 之前对其进行修改会很有用。例如，可能需要向用户消息追加一些额外上下文，或根据某些外部条件修改系统消息。

可以通过为 AI 服务配置一个实现了对 `ChatRequest` 所应用的转换的 `UnaryOperator<ChatRequest>` 来实现：

```java
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .chatRequestTransformer(transformingFunction)  // Configures the transformation function to be applied to the ChatRequest
    .build();
```

如果需要同时访问 `ChatMemory` 才能实现所需的 `ChatRequest` 转换，也可以为 `chatRequestTransformer` 方法配置一个 `BiFunction<ChatRequest, Object, ChatRequest>`，其中传递给该函数的第二个参数是记忆 ID。

## ChatRequestParameters

另一个自由度是按每次调用配置参数（如 temperature、toolsChoice、最大 token 数等）。例如，你可能希望某些请求更具“创造性”（较高的 temperature），而其他请求更具确定性（较低的 temperature）。

为此，你可以创建一个还接受 `ChatRequestParameters` 类型（或任何提供商特定类型，如 `OpenAiChatRequestParameters`）参数的 AI 服务方法。这会告诉 LangChain4j 在每次调用时接受并合并这些参数。

!!! note
   请注意，在 `ChatRequestParameters` 中指定的 `toolSpecifications` 和 `responseFormat` 将覆盖由 AI 服务生成的那些。

在接口中定义第二个参数：

```java
interface AssistantWithChatParams {

    String chat(@UserMessage String userMessage, ChatRequestParameters params);
}
```

构建 AI 服务：

```java
AssistantWithChatParams assistant = AiServices.builder(AssistantWithChatParams.class)
    .chatModel(openAiChatModel)  // or whichever model
    .build();
```

使用任何按调用传入的参数进行调用：

```java
ChatRequestParameters customParams = ChatRequestParameters.builder()
    .temperature(0.85)
    .build();

String answer = assistant.chat("Hi there!", customParams);
```

作为参数传递给 AI 服务方法的 `ChatRequestParameters` 也会传递到前面一节讨论的 `chatRequestTransformer`，因此如有需要，也可以在那里对其进行访问和修改。

## 有效的 AI 服务方法示例

以下是一些有效的 AI 服务方法的示例。

<details>
<summary>`UserMessage`</summary>

```java
String chat(String userMessage);

String chat(@UserMessage String userMessage);

String chat(@UserMessage String userMessage, ChatRequestParameters parameters);

String chat(@UserMessage String userMessage, @V("country") String country); // userMessage contains "{{country}}" template variable

String chat(@UserMessage String userMessage, @UserMessage Content content); // content can be one of: TextContent, ImageContent, AudioContent, VideoContent, PdfFileContent

String chat(@UserMessage String userMessage, @UserMessage ImageContent image); // second argument can be one of: TextContent, ImageContent, AudioContent, VideoContent, PdfFileContent

String chat(@UserMessage String userMessage, @UserMessage List<Content> contents);

String chat(@UserMessage String userMessage, @UserMessage List<ImageContent> images);

@UserMessage("What is the capital of Germany?")
String chat();

@UserMessage("What is the capital of {{it}}?")
String chat(String country);

@UserMessage("What is the capital of {{country}}?")
String chat(@V("country") String country);

@UserMessage("What is the {{something}} of {{country}}?")
String chat(@V("something") String something, @V("country") String country);

@UserMessage("What is the capital of {{country}}?")
String chat(String country); // this works only in Quarkus and Spring Boot applications
```
</details>

<details>
<summary>`SystemMessage` 和 `UserMessage`</summary>

```java
@SystemMessage("Given a name of a country, answer with a name of it's capital")
String chat(String userMessage);

@SystemMessage("Given a name of a country, answer with a name of it's capital")
String chat(@UserMessage String userMessage);

@SystemMessage("Given a name of a country, {{answerInstructions}}")
String chat(@V("answerInstructions") String answerInstructions, @UserMessage String userMessage);

@SystemMessage("Given a name of a country, answer with a name of it's capital")
String chat(@UserMessage String userMessage, @V("country") String country); // userMessage contains "{{country}}" template variable

@SystemMessage("Given a name of a country, {{answerInstructions}}")
String chat(@V("answerInstructions") String answerInstructions, @UserMessage String userMessage, @V("country") String country); // userMessage contains "{{country}}" template variable

@SystemMessage("Given a name of a country, answer with a name of it's capital")
@UserMessage("Germany")
String chat();

@SystemMessage("Given a name of a country, {{answerInstructions}}")
@UserMessage("Germany")
String chat(@V("answerInstructions") String answerInstructions);

@SystemMessage("Given a name of a country, answer with a name of it's capital")
@UserMessage("{{it}}")
String chat(String country);

@SystemMessage("Given a name of a country, answer with a name of it's capital")
@UserMessage("{{country}}")
String chat(@V("country") String country);

@SystemMessage("Given a name of a country, {{answerInstructions}}")
@UserMessage("{{country}}")
String chat(@V("answerInstructions") String answerInstructions, @V("country") String country);
```
</details>

## 多模态

除了文本内容之外（或作为替代），
AI 服务方法可以接受一个或多个 `Content` 或 `List<Content>` 参数：

```java
String chat(@UserMessage String userMessage, @UserMessage Content content);

String chat(@UserMessage String userMessage, @UserMessage ImageContent image);

String chat(@UserMessage String userMessage, @UserMessage ImageContent image, @UserMessage AudioContent audio);

String chat(@UserMessage String userMessage, @UserMessage List<Content> contents);

String chat(@UserMessage String userMessage, @UserMessage List<ImageContent> images);

String chat(Content content);

String chat(AudioContent content);

String chat(List<Content> contents);

String chat(List<AudioContent> contents);

String chat(@UserMessage Content content1, @UserMessage Content content2);

String chat(@UserMessage AudioContent audio, @UserMessage ImageContent image);
```

AI 服务将按照参数声明的顺序把所有内容放入最终的 `UserMessage` 中。

有关可用内容类型的更多细节，请查看 [Content API](chat-and-language-models.md#多模态)。


## 返回类型

AI 服务方法可以返回以下类型之一：
- `String` - 在这种情况下，LLM 生成的输出不做任何处理/解析就直接返回
- [结构化输出](structured-outputs.md#支持的类型) 支持的任何类型 - 在这种情况下，
AI 服务会在返回之前将 LLM 生成的输出解析为所需的类型
- `TokenStream` - 用于[在其生成的同时](ai-services.md#流式)接收响应
- `CompletableFuture<T>` / `CompletionStage<T>` 或 `Flow.Publisher<...>` - 用于[不阻塞调用线程](non-blocking.md)地执行交互
（实验性功能）

任何类型都可以额外包装成 `Result<T>`，以获取关于 AI 服务调用的额外元数据：
- `TokenUsage` - AI 服务调用期间使用的 token 总数。如果 AI 服务对 LLM 进行了多次调用
（例如因为执行了工具），它会累加所有调用的 token 使用量。
- Sources - 在 [RAG](ai-services.md#rag) 检索期间检索到的 `Content`
- AI 服务调用期间执行的所有[工具](ai-services.md#工具函数调用)（包括请求和结果）
- 最终聊天响应的 `FinishReason`
- 所有中间 `ChatResponse`
- 最终的 `ChatResponse`

示例：
```java
interface Assistant {
    
    @UserMessage("Generate an outline for the article on the following topic: {{it}}")
    Result<List<String>> generateOutlineFor(String topic);
}

Result<List<String>> result = assistant.generateOutlineFor("Java");

List<String> outline = result.content();
TokenUsage tokenUsage = result.tokenUsage();
List<Content> sources = result.sources();
List<ToolExecution> toolExecutions = result.toolExecutions();
FinishReason finishReason = result.finishReason();
```

!!! note
   `Result<T>` 中的 `T` 是 LLM 产生的内容，因此它必须是 LLM 实际能够生成的类型：
   `String`、枚举、POJO、这些类型的集合等。
   LangChain4j 自身的类型，如 `ChatResponse`、`ChatMessage`、`TextSegment`、`Embedding` 或 `TokenUsage`，
   不能用作 `T`（也不能用作 `List<T>`/`Set<T>` 返回类型的元素）：
   创建时 AI 服务会因 `IllegalConfigurationException` 而失败。
   最终 `ChatResponse` 所携带的一切已经可以直接在 `Result<T>` 上获取，例如：
   ```java
   ChatResponse chatResponse = result.finalResponse();
   ```

## 结构化输出

如果你希望从 LLM 接收结构化输出（例如一个复杂的 Java 对象，
而不是 `String` 中的非结构化文本），
你可以把 AI 服务方法的返回类型从 `String` 改为其他类型。

!!! note
   关于结构化输出的更多信息可以在[这里](structured-outputs.md)找到。

几个示例：

### 作为返回类型的 `boolean`

```java
interface SentimentAnalyzer {

    @UserMessage("Does {{it}} has a positive sentiment?")
    boolean isPositive(String text);

}

SentimentAnalyzer sentimentAnalyzer = AiServices.create(SentimentAnalyzer.class, model);

boolean positive = sentimentAnalyzer.isPositive("It's wonderful!");
// true
```

### 作为返回类型的 `Enum`
```java
enum Priority {
    CRITICAL, HIGH, LOW
}

interface PriorityAnalyzer {
    
    @UserMessage("Analyze the priority of the following issue: {{it}}")
    Priority analyzePriority(String issueDescription);
}

PriorityAnalyzer priorityAnalyzer = AiServices.create(PriorityAnalyzer.class, model);

Priority priority = priorityAnalyzer.analyzePriority("The main payment gateway is down, and customers cannot process transactions.");
// CRITICAL
```

!!! tip
   对于是/否问题以及在固定选项之间做选择（如上面的示例），你还可以考虑
   [决策服务](decision-services.md)，它们使用[决策模型](decision-models.md)
   而不是聊天模型：它们可以为每个答案返回一个概率，并且使用专用的决策模型时，
   通常更快、成本更低。

### 作为返回类型的 POJO
```java
class Person {

    @Description("first name of a person") // you can add an optional description to help an LLM have a better understanding
    String firstName;
    String lastName;
    LocalDate birthDate;
    Address address;
}

@Description("an address") // you can add an optional description to help an LLM have a better understanding
class Address {
    String street;
    Integer streetNumber;
    String city;
}

interface PersonExtractor {

    @UserMessage("Extract information about a person from {{it}}")
    Person extractPersonFrom(String text);
}

PersonExtractor personExtractor = AiServices.create(PersonExtractor.class, model);

String text = """
            In 1968, amidst the fading echoes of Independence Day,
            a child named John arrived under the calm evening sky.
            This newborn, bearing the surname Doe, marked the start of a new journey.
            He was welcomed into the world at 345 Whispering Pines Avenue
            a quaint street nestled in the heart of Springfield
            an abode that echoed with the gentle hum of suburban dreams and aspirations.
            """;

Person person = personExtractor.extractPersonFrom(text);

System.out.println(person); // Person { firstName = "John", lastName = "Doe", birthDate = 1968-07-04, address = Address { ... } }
```

## JSON 模式

在提取自定义 POJO（实际上是 JSON，之后再解析为 POJO）时，
建议在模型配置中启用“JSON 模式”。
这样，LLM 将被强制以有效 JSON 进行回复。

!!! note
   请注意，JSON 模式与工具/函数调用是类似的功能，
   但它们具有不同的 API，用于不同的目的。

   当你_始终_需要 LLM 以结构化格式（有效 JSON）回复时，JSON 模式非常有用。
   此外，通常不需要状态/记忆，因此每次与 LLM 的交互都相互独立。
   例如，你可能想从文本中提取信息，比如该文本中提到的所有人列表，
   或将自由形式的产品评论转换为包含 `String productName`、`Sentiment sentiment`、`List<String> claimedProblems` 等字段的结构化表单。

   另一方面，当 LLM 需要能够执行某些操作时
   （例如查询数据库、搜索网络、取消用户的预订等），工具/函数会很有用。
   在这种情况下，会向 LLM 提供一份带有其预期 JSON schema 的工具列表，它会自主决定
   是否调用其中任何一个来满足用户请求。

   早期，函数调用常被用于结构化数据提取，
   但现在我们有 JSON 模式功能，它更适合这一目的。

以下是启用 JSON 模式的方法：

- 对于 OpenAI：
  - 对于支持 [Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/) 的较新模型（如 `gpt-4o-mini`、`gpt-4o-2024-08-06`）：
    ```java
    OpenAiChatModel.builder()
        ...
        .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)
        .strictJsonSchema(true)
        .build();
    ```
    更多细节见[这里](../integrations/language-models/open-ai.md#结构化输出)。
  - 对于较旧的模型（如 gpt-3.5-turbo、gpt-4）：
    ```java
    OpenAiChatModel.builder()
        ...
        .responseFormat("json_object")
        .build();
    ```

- 对于 Azure OpenAI：
```java
AzureOpenAiChatModel.builder()
    ...
    .responseFormat(new ChatCompletionsJsonResponseFormat())
    .build();
```

- 对于 Vertex AI Gemini：
```java
VertexAiGeminiChatModel.builder()
    ...
    .responseMimeType("application/json")
    .build();
```

或者通过从 Java 类指定一个显式 schema：

```java
VertexAiGeminiChatModel.builder()
    ...
    .responseSchema(SchemaHelper.fromClass(Person.class))
    .build();
```

从 JSON schema：

```java
VertexAiGeminiChatModel.builder()
    ...
    .responseSchema(Schema.builder()...build())
    .build();
```

- 对于 Google AI Gemini：
```java
GoogleAiGeminiChatModel.builder()
    ...
    .responseFormat(ResponseFormat.JSON)
    .build();
```

或者通过从 Java 类指定一个显式 schema：

```java
GoogleAiGeminiChatModel.builder()
    ...
    .responseFormat(ResponseFormat.builder()
        .type(JSON)
        .jsonSchema(JsonSchemas.jsonSchemaFrom(Person.class).get())
        .build())
    .build();
```

从 JSON schema：

```java
GoogleAiGeminiChatModel.builder()
    ...
    .responseFormat(ResponseFormat.builder()
        .type(JSON)
        .jsonSchema(JsonSchema.builder()...build())
        .build())
    .build();
```

- 对于 Mistral AI：
```java
MistralAiChatModel.builder()
    ...
    .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA)
    .strictJsonSchema(true)
    .build();
```

- 对于 Ollama：
```java
OllamaChatModel.builder()
    ...
    .responseFormat(JSON)
    .build();
```

- 对于其他模型提供商：如果底层模型提供商不支持 JSON 模式，
提示词工程是你的最佳选择。此外，可以尝试降低 `temperature` 以获得更高的确定性。

[更多示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/OtherServiceExamples.java)


## 流式

使用 `TokenStream` 返回类型时，AI 服务可以按 token [流式返回响应](response-streaming.md)。
`Flow.Publisher` 返回类型以不阻塞调用线程的方式流式执行相同的交互 -
参见[非阻塞与响应式](non-blocking.md)。

```java
interface Assistant {

    TokenStream chat(String message);
}

StreamingChatModel model = OpenAiStreamingChatModel.builder()
    .apiKey(System.getenv("OPENAI_API_KEY"))
    .modelName(GPT_4_O_MINI)
    .build();

Assistant assistant = AiServices.create(Assistant.class, model);

TokenStream tokenStream = assistant.chat("Tell me a joke");

CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();

tokenStream
    .onPartialResponse((String partialResponse) -> System.out.println(partialResponse))
    .onPartialThinking((PartialThinking partialThinking) -> System.out.println(partialThinking))
    .onRetrieved((List<Content> contents) -> System.out.println(contents))
    .onIntermediateResponse((ChatResponse intermediateResponse) -> System.out.println(intermediateResponse))
     // This will be invoked every time a new partial tool call (usually containing a single token of the tool's arguments) is available.
    .onPartialToolCall((PartialToolCall partialToolCall) -> System.out.println(partialToolCall))
     // This will be invoked right before a tool is executed. BeforeToolExecution contains ToolExecutionRequest (e.g. tool name, tool arguments, etc.)
    .beforeToolExecution((BeforeToolExecution beforeToolExecution) -> System.out.println(beforeToolExecution))
     // This will be invoked right after a tool is executed. ToolExecution contains ToolExecutionRequest and tool execution result.
    .onToolExecuted((ToolExecution toolExecution) -> System.out.println(toolExecution))
     // This will be invoked for raw provider streaming events that are not already exposed via the typed callbacks above (e.g. server-tool lifecycle events). See the "Unmapped Raw Events" section of Response Streaming.
    .onUnmappedRawEvent((Object rawEvent) -> System.out.println(rawEvent))
    .onCompleteResponse((ChatResponse response) -> futureResponse.complete(response))
    .onError((Throwable error) -> futureResponse.completeExceptionally(error))
    .start();

futureResponse.join(); // Blocks the main thread until the streaming process (running in another thread) is complete
```

### 流式取消

如果你希望取消流式处理，可以从以下回调之一执行：
- `onPartialResponseWithContext(BiConsumer<PartialResponse, PartialResponseContext>)`
- `onPartialThinkingWithContext(BiConsumer<PartialThinking, PartialThinkingContext>)`

例如：
```java
tokenStream
    .onPartialResponseWithContext((PartialResponse partialResponse, PartialResponseContext context) -> {
        process(partialResponse);
        if (shouldCancel()) {
            context.streamingHandle().cancel();
        }
    })
    .onCompleteResponse((ChatResponse response) -> futureResponse.complete(response))
    .onError((Throwable error) -> futureResponse.completeExceptionally(error))
    .start();
```

当调用 `StreamingHandle.cancel()` 时，LangChain4j 会关闭连接并停止流式处理。
一旦调用了 `StreamingHandle.cancel()`，`TokenStream` 将不再接收任何后续回调。

### Flux
你也可以使用 `Flux<String>` 来替代 `TokenStream`。
`Flow.Publisher<String>` 无需额外模块即可获得相同的流 -
参见[非阻塞与响应式](non-blocking.md)。
为此，请导入 `langchain4j-reactor` 模块：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-reactor</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
```java
interface Assistant {

  Flux<String> chat(String message);
}
```

`Flux<String>` 由 `TokenStream` 支撑，因此适用于每个提供商。同一模块还包含
[非阻塞模式](non-blocking.md)的 Reactor 绑定——`Mono<T>` 和
`Flux<AiServiceStreamingEvent>`——它们仅在实现了这些功能的提供商上可用。

[流式示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithStreamingExample.java)


## 聊天记忆

AI 服务可以使用[聊天记忆](chat-memory.md)来“记住”之前的交互：
```java
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
    .build();
```
在这种场景下，AI 服务的所有调用都将使用同一个 `ChatMemory` 实例。
但如果你有多个用户，这种方式将行不通，
因为每个用户都需要自己独立的 `ChatMemory` 实例来维持各自的对话。

解决这个问题的方法是使用 `ChatMemoryProvider`：
```java
interface Assistant  {
    String chat(@MemoryId int memoryId, @UserMessage String message);
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(10))
    .build();

String answerToKlaus = assistant.chat(1, "Hello, my name is Klaus");
String answerToFrancine = assistant.chat(2, "Hello, my name is Francine");
```
在这种场景下，`ChatMemoryProvider` 将提供两个不同的 `ChatMemory` 实例，每个记忆 ID 对应一个。

以这种方式使用 `ChatMemory` 时，同样重要的是清除不再需要的对话的记忆，以避免内存泄漏。要使 AI 服务内部使用的聊天记忆可访问，只需让定义它的接口继承 `ChatMemoryAccess` 接口即可。
```java
interface Assistant extends ChatMemoryAccess {
    String chat(@MemoryId int memoryId, @UserMessage String message);
}
```

这样就可以既访问单个对话的 `ChatMemory` 实例，又能在对话结束时将其清除。
```java
String answerToKlaus = assistant.chat(1, "Hello, my name is Klaus");
String answerToFrancine = assistant.chat(2, "Hello, my name is Francine");

List<ChatMessage> messagesWithKlaus = assistant.getChatMemory(1).messages();
boolean chatMemoryWithFrancineEvicted = assistant.evictChatMemory(2);
```

!!! note
   请注意，如果 AI 服务方法没有带 `@MemoryId` 注解的参数，
   `ChatMemoryProvider` 中 `memoryId` 的值将默认为字符串 `"default"`。

!!! note
   请注意，不应并发地对相同的 `@MemoryId` 调用 AI 服务，
   因为这可能导致 `ChatMemory` 损坏。
   目前，AI 服务没有实现任何机制来防止对相同 `@MemoryId` 的并发调用。

- [带有单一 ChatMemory 的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithMemoryExample.java)
- [每个用户一个 ChatMemory 的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithMemoryForEachUserExample.java)
- [带有单一持久化 ChatMemory 的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithPersistentMemoryExample.java)
- [每个用户一个持久化 ChatMemory 的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithPersistentMemoryForEachUserExample.java)


## 工具（函数调用）

可以为 AI 服务配置 LLM 可使用的工具：
```java
class Tools {
    
    @Tool
    int add(int a, int b) {
        return a + b;
    }

    @Tool
    int multiply(int a, int b) {
        return a * b;
    }
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .tools(new Tools())
    .build();

String answer = assistant.chat("What is 1+2 and 3*4?");
```
在这种场景下，LLM 会在给出最终答案之前请求执行 `add(1, 2)` 和 `multiply(3, 4)` 方法。
LangChain4j 会自动执行这些方法。

关于工具的更多细节可以在[这里](tools.md#高层工具-api)找到。


## RAG

可以为 AI 服务配置 `ContentRetriever` 以启用[朴素 RAG](rag.md#naive-rag)：
```java
EmbeddingStore embeddingStore  = ...
EmbeddingModel embeddingModel = ...

ContentRetriever contentRetriever = new EmbeddingStoreContentRetriever(embeddingStore, embeddingModel);

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .contentRetriever(contentRetriever)
    .build();
```

配置 `RetrievalAugmentor` 可提供更大的灵活性，
启用[高级 RAG](rag.md#advanced-rag)能力，如查询转换、重排等：
```java
RetrievalAugmentor retrievalAugmentor = DefaultRetrievalAugmentor.builder()
        .queryTransformer(...)
        .queryRouter(...)
        .contentAggregator(...)
        .contentInjector(...)
        .executor(...)
        .build();

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .retrievalAugmentor(retrievalAugmentor)
    .build();
```

### 作为工具的 RAG 

默认情况下，每次用户查询都会执行内容检索。
或者，可以将检索视为一种类似工具的能力，只在模型判断需要额外上下文时才会被调用。
采用这种方法，检索仍然是 RAG 流程的一部分，但它是条件执行的，从而避免了对简单查询的无谓搜索。

要实现这一点，你可以将 `ContentRetriever` 封装在一个 `@Tool` 中，并将其注册到 AiServices。这样 LLM 就可以根据工具的描述自主决定是否触发检索。

#### 1. 定义检索工具

创建一个封装 `ContentRetriever` 的类。  
`@Tool` 的描述至关重要，因为它会告知 LLM 何时调用搜索。

```java
import dev.langchain4j.agent.tool.Tool;
import dev.langchain4j.rag.content.retriever.ContentRetriever;
import dev.langchain4j.rag.query.Query;

import java.util.stream.Collectors;

static class SearchTool {

    private final ContentRetriever contentRetriever;

    SearchTool(ContentRetriever contentRetriever) {
        this.contentRetriever = contentRetriever;
    }

    @Tool("Search for technical information about LangChain4j and RAG configurations")
    public String search(String query) {
        // This logic is only executed when the LLM determines retrieval is necessary
        return contentRetriever.retrieve(new Query(query)).stream()
                .map(content -> content.textSegment().text())
                .collect(Collectors.joining("\n\n"));
    }
}
```

#### 2. 将工具注册到 AiServices

不要使用全局的 RetrievalAugmentor，而是把检索逻辑注册为一个工具。

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(model)
        .tools(new SearchTool(contentRetriever))
        .build();
```

#### 3. 预期行为

LLM 会将用户意图与工具描述进行比对，以决定是否执行搜索。

**场景 A — 一般对话**

- **输入：**  
  `Hello, how are you today?`

- **行为：**  
  LLM 直接根据其内部知识进行回复，而不调用工具。


**场景 B — 技术问题**

- **输入：**  
  `How do I configure a ContentRetriever?`

- **行为：**  
  LLM 识别出技术意图，调用 `search()`，并基于检索到的文档生成回复。

这种方法使检索能够像工具一样作为**按需能力**发挥作用，而不是每次查询的强制步骤。

关于 RAG 的更多细节可以在[这里](rag.md)找到。

更多 RAG 示例可以在[这里](https://github.com/langchain4j/langchain4j-examples/tree/main/rag-examples/src/main/java)找到。


## 自动审核

AI 服务可以自动执行内容审核。当检测到不当内容时，会抛出 `ModerationException`，其中包含原始的 `Moderation` 对象。
该对象包含有关被标记内容的信息，例如被标记的具体文本。

在构建 AI 服务时可以配置自动审核：

```java
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .moderationModel(moderationModel)  // Configures moderation  model
    .build();
```


[示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithAutoModerationExample.java)

## 链接多个 AI 服务
你的基于 LLM 的应用的逻辑越复杂，
就越有必要像软件开发中的常见做法那样，把它拆分成更小的部分。

例如，向系统提示词中塞入大量指令以涵盖所有可能的场景，
容易出现错误且效率低下。如果指令太多，LLM 可能会忽略其中一些。
此外，指令呈现的先后顺序也很重要，这使得整个过程更具挑战性。

这一原则同样适用于工具、RAG 以及 `temperature`、`maxTokens` 等模型参数。

你的聊天机器人很可能不需要时刻感知你所拥有的每一个工具。
例如，当用户只是向聊天机器人打招呼或道别时，
让 LLM 访问数十甚至数百个工具（LLM 调用中包含的每个工具都会消耗大量 token）既昂贵，有时甚至危险，
还可能导致意外结果（LLM 可能产生幻觉，或被诱导用非预期的输入调用工具）。

关于 RAG：类似地，有时候需要向 LLM 提供一些上下文，
但并非总是如此，因为这会产生额外成本（更多上下文 = 更多 token）
并增加响应时间（更多上下文 = 更高延迟）。

关于模型参数：在某些情况下，你可能需要 LLM 具有高度确定性，
因此会设置较低的 `temperature`。在其他情况下，你可能会选择较高的 `temperature`，依此类推。

关键在于，更小、更具体的组件更易于开发、测试、维护和理解，成本也更低。

另一个需要考虑的方面涉及两个极端：
- 你希望应用高度确定性强，
由应用控制流程，LLM 只是其中一个组件吗？
- 还是你希望 LLM 拥有完全自主权来驱动你的应用？

又或许根据情况混合两者？
当你把应用分解为更小、更易管理的部分时，所有这些选择都是可行的。

AI 服务可以作为普通（确定性的）软件组件使用，并与其组合：
- 你可以一个接一个地调用 AI 服务（即链式调用）。
- 你可以使用确定性的或由 LLM 驱动的 `if`/`else` 语句（AI 服务可以返回 `boolean`）。
- 你可以使用确定性的或由 LLM 驱动的 `switch` 语句（AI 服务可以返回 `enum`）。
- 你可以使用确定性的或由 LLM 驱动的 `for`/`while` 循环（AI 服务可以返回 `int` 和其他数值类型）。
- 你可以在单元测试中模拟 AI 服务（因为它是一个接口）。
- 你可以独立地对每个 AI 服务进行集成测试。
- 你可以分别评估每个 AI 服务，并为其找到最优参数。
- 等等

让我们来看一个简单的示例。
我想为我的公司构建一个聊天机器人。
如果用户向聊天机器人打招呼，
我希望它使用预定义的问候语进行回复，而不依赖 LLM 来生成问候语。
如果用户提问，我希望 LLM 使用公司内部知识库（即 RAG）来生成回复。

以下是将该任务分解为两个独立 AI 服务的方法：
```java
interface GreetingExpert {

    @UserMessage("Is the following text a greeting? Text: {{it}}")
    boolean isGreeting(String text);
}

interface ChatBot {

    @SystemMessage("You are a polite chatbot of a company called Miles of Smiles.")
    String reply(String userMessage);
}

class MilesOfSmiles {

    private final GreetingExpert greetingExpert;
    private final ChatBot chatBot;
    
    ...
    
    public String handle(String userMessage) {
        if (greetingExpert.isGreeting(userMessage)) {
            return "Greetings from Miles of Smiles! How can I make your day better?";
        } else {
            return chatBot.reply(userMessage);
        }
    }
}

GreetingExpert greetingExpert = AiServices.create(GreetingExpert.class, llama2);

ChatBot chatBot = AiServices.builder(ChatBot.class)
    .chatModel(gpt4)
    .contentRetriever(milesOfSmilesContentRetriever)
    .build();

MilesOfSmiles milesOfSmiles = new MilesOfSmiles(greetingExpert, chatBot);

String greeting = milesOfSmiles.handle("Hello");
System.out.println(greeting); // Greetings from Miles of Smiles! How can I make your day better?

String answer = milesOfSmiles.handle("Which services do you provide?");
System.out.println(answer); // At Miles of Smiles, we provide a wide range of services ...
```

注意我们是如何为“识别文本是否为问候语”这一简单任务使用更便宜的 Llama2，
而为更复杂的任务使用搭配内容检索器（RAG）的更昂贵的 GPT-4。

这是一个非常简单的、甚至有点天真的示例，但希望它能说明这一思路。

现在，我可以同时模拟 `GreetingExpert` 和 `ChatBot`，并独立测试 `MilesOfSmiles`
我也可以分别对 `GreetingExpert` 和 `ChatBot` 进行集成测试。
我可以分别评估它们，为每个子任务找到最合适的参数，
或者从长远来看，甚至为每个具体子任务微调一个小型专用模型。


## 测试

- [客户支持智能体集成测试示例](https://github.com/langchain4j/langchain4j-examples/blob/main/customer-support-agent-example/src/test/java/dev/langchain4j/example/CustomerSupportAgentIT.java)


## 相关教程
- [Siva](https://www.sivalabs.in/) 撰写的 [LangChain4j AiServices 教程](https://www.sivalabs.in/langchain4j-ai-services-tutorial/)
