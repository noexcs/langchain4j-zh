# 工具（函数调用）

一些 LLM 除了能生成文本外，还能触发动作。

!!! note
  所有支持工具的 LLM 都可以在[这里](../integrations/language-models/index.md)找到（参见 "Tools" 列）。

!!! note
  并非所有 LLM 对工具的支持程度都相同。
  理解、选择并正确使用工具的能力在很大程度上取决于具体的模型及其能力。
  有些模型可能完全不支持工具，而另一些模型可能需要精心设计的提示词工程
  或额外的系统指令。

有一个称为"工具"（tools）或"函数调用"（function calling）的概念。
它允许 LLM 在必要时调用一个或多个可用工具，这些工具通常由开发者定义。
工具可以是任何东西：一次网页搜索、对外部 API 的调用，或执行某段特定的代码，等等。
LLM 实际上并不能自己调用工具；相反，它们会在响应中表达
调用某个特定工具的意图（而不是以纯文本方式响应）。
作为开发者，我们随后应使用提供的参数执行该工具，并把
工具执行的结果报告回去。

例如，我们知道 LLM 本身并不擅长数学。
如果你的用例涉及偶尔的数学计算，你可能想为 LLM 提供一个"数学工具"。
通过在向 LLM 发出的请求中声明一个或多个工具，
当它认为合适时，就可以决定调用其中一个。
给定一个数学问题以及一组数学工具，LLM 可能会决定，为了正确回答该问题，
它应该先调用所提供的某个数学工具。

我们来看看它在实践中是如何工作的（有工具和没有工具的情况）：

一个不使用工具的消息交互示例：
```
Request:
- messages:
    - UserMessage:
        - text: What is the square root of 475695037565?

Response:
- AiMessage:
    - text: The square root of 475695037565 is approximately 689710.
```
很接近，但不正确。

一个使用以下工具的消息交互示例：
```java
@Tool("Sums 2 given numbers")
double sum(double a, double b) {
    return a + b;
}

@Tool("Returns a square root of a given number")
double squareRoot(double x) {
    return Math.sqrt(x);
}
```

```
Request 1:
- messages:
    - UserMessage:
        - text: What is the square root of 475695037565?
- tools:
    - sum(double a, double b): Sums 2 given numbers
    - squareRoot(double x): Returns a square root of a given number

Response 1:
- AiMessage:
    - toolExecutionRequests:
        - squareRoot(475695037565)


... here we are executing the squareRoot method with the "475695037565" argument and getting "689706.486532" as a result ...


Request 2:
- messages:
    - UserMessage:
        - text: What is the square root of 475695037565?
    - AiMessage:
        - toolExecutionRequests:
            - squareRoot(475695037565)
    - ToolExecutionResultMessage:
        - text: 689706.486532

Response 2:
- AiMessage:
    - text: The square root of 475695037565 is 689706.486532.
```

正如你所见，当 LLM 能够使用工具时，它可以在合适的时候决定调用其中一个。

这是一个非常强大的功能。
在这个简单的例子中，我们给 LLM 提供了基础的数学工具，
但想象一下，如果我们给它例如 `googleSearch` 和 `sendEmail` 这样的工具，
以及类似"我的朋友想了解 AI 领域的最新新闻。请把简短的摘要发送到 friend@email.com。"这样的查询，
那么它可以先用 `googleSearch` 工具找到最新新闻，
然后再进行总结，并使用 `sendEmail` 工具通过电子邮件发送摘要。

!!! note
  为了增加 LLM 以正确的参数调用正确的工具的可能性，
  我们应该提供清晰且无歧义的：
  - 工具的名称
  - 工具的功能描述以及何时应使用它
  - 每个工具参数的描述

  一个好的经验法则：如果人类能够理解一个工具的用途和如何使用它，
  那么 LLM 很可能也能理解。

LLM 经过了专门的微调，以判断何时调用工具以及如何调用它们。
一些模型甚至可以一次调用多个工具，例如，
[OpenAI](https://platform.openai.com/docs/guides/function-calling/parallel-function-calling)。

!!! note
  请注意，并非所有模型都支持工具。
  要查看哪些模型支持工具，请参见[此](https://docs.langchain4j.dev/integrations/language-models/)页面上的 "Tools" 列。

!!! note
  请注意，工具/函数调用与 [JSON 模式](ai-services.md#json-模式) 并不相同。

# 两个抽象层次

LangChain4j 为使用工具提供了两个抽象层次：
- 低层，使用 `ChatModel` 和 `ToolSpecification` API
- 高层，使用 [AI 服务](ai-services.md) 和带 `@Tool` 注解的 Java 方法

## 底层工具 API

在低层，你可以使用 `ChatModel`
的 `chat(ChatRequest)` 方法。`StreamingChatModel` 中也有一个类似的方法。

在创建 `ChatRequest` 时，你可以指定一个或多个 `ToolSpecification`。

`ToolSpecification` 是一个包含关于工具所有信息的对象：
- 工具的 `name`
- 工具的 `description`
- 工具的 `parameters` 及其描述
- 工具的 `metadata`。
默认情况下，它不会发送给 LLM 提供商，你必须在创建 `ChatModel` 时
明确指定应发送哪些 metadata 键。
目前，工具 metadata 仅由 `langchain4j-anthropic` 模块支持。
当工具由 [McpToolProvider](mcp.md#mcp-工具提供器) 提供时，
`metadata` 可以包含 MCP 特有的条目。

建议尽可能多地提供关于工具的信息：
一个清晰的名称、一份全面的描述，以及每个参数的描述，等等。

### 创建 ToolSpecification

创建 `ToolSpecification` 有两种方式：

1. 手动
```java
ToolSpecification toolSpecification = ToolSpecification.builder()
    .name("getWeather")
    .description("Returns the weather forecast for a given city")
    .parameters(JsonObjectSchema.builder()
        .addStringProperty("city", "The city for which the weather forecast should be returned")
        .addEnumProperty("temperatureUnit", List.of("CELSIUS", "FAHRENHEIT"))
        .required("city") // the required properties should be specified explicitly
        .build())
    .build();
```

有关 `JsonObjectSchema` 的更多信息，请参见[这里](structured-outputs.md#jsonobjectschema)。

2. 使用辅助方法：
- `ToolSpecifications.toolSpecificationsFrom(Class)`
- `ToolSpecifications.toolSpecificationsFrom(Object)`
- `ToolSpecifications.toolSpecificationFrom(Method)`

```java
class WeatherTools { 
  
    @Tool("Returns the weather forecast for a given city")
    String getWeather(
            @P("The city for which the weather forecast should be returned") String city,
            TemperatureUnit temperatureUnit
    ) {
        ...
    }
}

List<ToolSpecification> toolSpecifications = ToolSpecifications.toolSpecificationsFrom(WeatherTools.class);
```

### JSON 序列化

`ToolSpecification` 可以使用 `toJson()` 和 `fromJson()` 方法序列化为 JSON，并反序列化回来。
这在某些场景下非常有用，例如当你想把工具规格存储在数据库中或通过网络传输它们时。

```java
String json = toolSpecification.toJson();

ToolSpecification deserialized = ToolSpecification.fromJson(json);
```

默认情况下，使用一个专用的 Jackson `ObjectMapper` 进行 JSON 转换。
你可以通过 SPI 提供自己的 `ToolSpecificationJsonCodec` 实现，
方法是实现 `ToolSpecificationJsonCodecFactory` 并将其注册到
`META-INF/services/dev.langchain4j.spi.agent.tool.ToolSpecificationJsonCodecFactory`。

### 使用 `ChatModel`

当你有了 `List<ToolSpecification>` 之后，就可以调用模型：
```java
ChatRequest request = ChatRequest.builder()
    .messages(UserMessage.from("What will the weather be like in London tomorrow?"))
    .toolSpecifications(toolSpecifications)
    .build();
ChatResponse response = model.chat(request);
AiMessage aiMessage = response.aiMessage();
```

如果 LLM 决定调用工具，返回的 `AiMessage` 将在
`toolExecutionRequests` 字段中包含数据。
在这种情况下，`AiMessage.hasToolExecutionRequests()` 将返回 `true`。
根据 LLM 的不同，它可以包含一个或多个 `ToolExecutionRequest` 对象
（一些 LLM 支持并行调用多个工具）。

每个 `ToolExecutionRequest` 应包含：
- 工具调用的 `id`。请注意，一些 LLM 提供商（例如 Google、Ollama）可能会省略此 ID。
- 要调用的工具的 `name`，例如：`getWeather`
- `arguments`，例如：`{ "city": "London", "temperatureUnit": "CELSIUS" }`

你需要使用 `ToolExecutionRequest` 中的信息手动执行这些工具。

如果你想把工具执行的结果发送回 LLM，
你需要创建一个 `ToolExecutionResultMessage`（每个 `ToolExecutionRequest` 对应一个），
并将它与所有之前的消息一起发送：
```java

String result = "It is expected to rain in London tomorrow.";
ToolExecutionResultMessage toolExecutionResultMessage = ToolExecutionResultMessage.from(toolExecutionRequest, result);
ChatRequest request2 = ChatRequest.builder()
        .messages(List.of(userMessage, aiMessage, toolExecutionResultMessage))
        .toolSpecifications(toolSpecifications)
        .build();
ChatResponse response2 = model.chat(request2);
```

#### 多模态工具结果
`ToolExecutionResultMessage` 还可以携带图像等非文本内容。
除了使用 `text()`，你还可以使用带 `contents()` 的构建器：

```java
ToolExecutionResultMessage toolExecutionResultMessage = ToolExecutionResultMessage.builder()
        .id(toolExecutionRequest.id())
        .toolName(toolExecutionRequest.name())
        .contents(
                TextContent.from("Here is the photo"),
                ImageContent.from(Image.builder()
                        .base64Data(base64Data)
                        .mimeType("image/png")
                        .build())
        )
        .build();
```

!!! note
  并非所有 LLM 提供商都支持多模态工具结果。
  有关提供商支持的详细信息，请参见[返回图像和多模态内容](tools.md#返回图像和多模态内容)。

### 使用 `StreamingChatModel`

当你有了 `List<ToolSpecification>` 之后，就可以调用模型：
```java
ChatRequest request = ChatRequest.builder()
    .messages(UserMessage.from("What will the weather be like in London tomorrow?"))
    .toolSpecifications(toolSpecifications)
    .build();

model.chat(request, new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.println("onPartialResponse: " + partialResponse);
    }

    @Override
    public void onPartialToolCall(PartialToolCall partialToolCall) {
        System.out.println("onPartialToolCall: " + partialToolCall);
    }

    @Override
    public void onCompleteToolCall(CompleteToolCall completeToolCall) {
        System.out.println("onCompleteToolCall: " + completeToolCall);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        System.out.println("onCompleteResponse: " + completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        error.printStackTrace();
    }
});
```

如果 LLM 决定调用工具，`onPartialToolCall(PartialToolCall)` 回调
通常会被多次调用，之后才会最终调用 `onCompleteToolCall(CompleteToolCall)` 回调，
表示该工具调用的流式传输已经完成。

!!! note
  请注意，并非所有 LLM 提供商都会流式传输部分工具调用。
  一些提供商（例如 Bedrock、Google、Mistral、Ollama）只返回完整的工具调用。
  在这些情况下，`onPartialToolCall` 回调不会被调用——只会调用 `onCompleteToolCall`。

下面是一个单次工具调用的流式传输可能的样子：
```
onPartialToolCall(index = 0, id = "call_abc", name = "get_weather", partialArguments = "{\"")
onPartialToolCall(index = 0, id = "call_abc", name = "get_weather", partialArguments = "city")
onPartialToolCall(index = 0, id = "call_abc", name = "get_weather", partialArguments = ""\":\"")
onPartialToolCall(index = 0, id = "call_abc", name = "get_weather", partialArguments = "London")
onPartialToolCall(index = 0, id = "call_abc", name = "get_weather", partialArguments = "\"}")
onCompleteToolCall(index = 0, id = "call_abc", name = "get_weather", arguments = "{\"city\":\"London\"}")
```

如果 LLM 发起了多个工具调用，`index` 会递增，使你能将
不同的 `PartialToolCall` 相互关联，并与最终的 `CompleteToolCall` 关联起来。

当完整响应的流式传输结束并且调用了 `onCompleteResponse(ChatResponse)` 时，
`ChatResponse` 内的 `AiMessage` 将包含流式传输期间发生的所有工具调用。

## 高层工具 API
在高层抽象中，你可以使用 `@Tool` 注解标注任何 Java 方法，
并在创建 [AI 服务](ai-services.md#工具函数调用) 时指定它们。

AI 服务会自动将此类方法转换为 `ToolSpecification`，
并将它们包含在与 LLM 的每次交互的请求中。
当 LLM 决定调用工具时，AI 服务会自动执行相应的方法，
该方法的返回值（如果有的话）会被发送回 LLM。
你可以在 `DefaultToolExecutor` 中找到实现细节。

几个工具示例：
```java
@Tool("Searches Google for relevant URLs, given the query")
public List<String> searchGoogle(@P("search query") String query) {
    return googleSearchService.search(query);
}

@Tool("Returns the content of a web page, given the URL")
public String getWebPageContent(@P("URL of the page") String url) {
    Document jsoupDocument = Jsoup.connect(url).get();
    return jsoupDocument.body().text();
}
```

### 工具方法的限制
带 `@Tool` 注解的方法：
- 可以是静态的，也可以是非静态的
- 可以具有任意可见性（public、private 等）。

### 工具方法的参数
带 `@Tool` 注解的方法可以接受任意数量、各种类型的参数：
- 原始类型：`int`、`double` 等
- 对象类型：`String`、`Integer`、`Double` 等
- 自定义 POJO（可以包含嵌套的 POJO）
- `enum`
- 多态类型（sealed 接口/类，或带有 Jackson
  `@JsonSubTypes` / `@JsonTypeInfo` 注解的类型）——参见[多态工具参数](#多态工具参数)
- `List<T>`/`Set<T>`，其中 `T` 是上述类型之一
- `Map<K,V>`（你需要用 `@P` 在参数描述中手动指定 `K` 和 `V` 的类型）

也支持没有参数的方法。

#### 参数名称

默认情况下，如果未指定 `@P` 的 `name` 属性，参数名称将通过反射获取。
然而，如果没有 `-parameters` javac 选项，反射返回的是 `arg0`、`arg1` 这样的通用名称。
参数的语义含义就会丢失，这可能会让 LLM 感到困惑。

在 `@P` 中设置 `name` 在以下两种情况下有用：

1. **缺少 `-parameters` javac 选项** —— 以避免 LLM 看到 `arg0`/`arg1` 这类通用名称。
   请注意，Quarkus 和 Spring 等框架默认启用 `-parameters`，
   因此实际的方法参数名称会被保留，使用这些框架时你通常不需要设置 `name`。
2. **为 LLM 使用自定义名称** —— 当你希望 LLM 看到的参数名称与源代码中的不同
   （例如，为了匹配特定的 API 契约，或提供一个更具描述性的名称）。

**示例：**

```java
@Tool
void getTemperature(
        @P("Temperature value") double value,
        @P("Unit of temperature") Optional<String> unit) {
    ...
}
```

#### 必填与可选

默认情况下，所有工具方法的参数都被视为**_必填的_**。
这意味着该参数会被列在发送给 LLM 的 JSON schema 的 `required` 数组中，
指示它生成一个值。
可以通过为参数添加 `@P(required = false)` 注解来使其变为可选：
```java
@Tool
String getTemperature(String location, @P(required = false) Unit unit) {
    ...
}
```

作为替代，你可以将参数声明为 `Optional<T>`：
```java
@Tool
String getTemperature(String location, Optional<Unit> unit) {
    ...
}
```

复杂参数的字段和子字段默认也被视为**_必填的_**。
你可以通过为字段添加 `@JsonProperty(required = false)` 注解来使其变为可选：
```java
record User(String name, @JsonProperty(required = false) String email) {}

@Tool
void add(User user) {
    ...
}
```

!!! note
  请注意，当与[结构化输出](structured-outputs.md)一起使用时，
  所有字段和子字段默认都被视为**_可选的_**。

!!! caution 必填只是建议性的：LLM 仍可能省略参数
  `required` 标志控制发送给 LLM 的 JSON schema（必填参数会被列在
  schema 的 `required` 数组中）。LLM 被期望遵守这一点，但在实践中它可能
  无视该 schema，仍然省略某个参数。

  在 LangChain4j 1.x 中，这种情况仅针对**原始类型**参数（`int`、`long`、`boolean`、…）进行检测——
  缺失的原始类型参数会触发 `ToolArgumentsErrorHandler`（参见下文[错误处理](#处理工具参数错误)）。
  **缺失的对象参数不会被校验**：即使 schema 将该参数标记为必填，`null` 也会被传递给
  带 `@Tool` 注解的方法。

  我们计划在 LangChain4j 2.0 中消除这种不对称性，以统一校验所有必填参数。
  如果这一计划中的变更会影响你的使用场景，请
  [提交一个 issue](https://github.com/langchain4j/langchain4j/issues)，以便我们在其落地之前听取你的反馈。

  如果你希望使用一个真正的回退值，而不是 `null`（或者针对原始类型参数，而不是报错），请使用
  [`@P(defaultValue = ...)`](#默认参数值)。

#### 默认参数值

`@P(defaultValue = "...")` 声明了一个值，当 LLM
省略该参数时，LangChain4j 会用它进行替代。这是让参数变为可选并为你的工具方法
提供一个合理回退值的最简单方式。

```java
enum SortBy { RELEVANCE, DATE, RATING }

@Tool
List<Article> searchArticles(
    String query,
    @P(defaultValue = "10") int limit,
    @P(defaultValue = "[\"en\"]") List<String> languages,
    @P(defaultValue = "RELEVANCE") SortBy sortBy
) {
    // When the LLM omits them:
    //   'limit'     -> 10
    //   'languages' -> ["en"]
    //   'sortBy'    -> SortBy.RELEVANCE
}
```

**设置 `defaultValue` 意味着该参数在 JSON schema 中变为可选** —— 该参数
无论 `@P(required)` 如何设置，都*不会*被列在 schema 的 `required` 数组中。
LLM 会被告知它可以省略该参数；如果它省略了，LangChain4j 会在调用
你的方法之前填入默认值。

**支持的类型：**

| 类型                         | 格式                   | 示例                                  |
|------------------------------|--------------------------|------------------------------------------|
| `String`                     | 逐字使用                 | `defaultValue = "USD"`                   |
| 原始类型 / 装箱原始类型       | 按类型进行转换           | `"10"`、`"3.14"`、`"true"`               |
| `enum`                       | 枚举常量名               | `defaultValue = "EUR"`                   |
| `UUID`                       | `UUID.fromString`        | `"550e8400-e29b-41d4-a716-446655440000"` |
| `BigDecimal`、`BigInteger`   | 数字字面量               | `"1.5"`、`"100"`                         |
| `List<T>` / `Set<T>` / 数组  | JSON 数组                | `"[\"a\",\"b\"]"`、`"[1,2,3]"`           |
| `Map<K,V>`                   | JSON 对象                | `"{\"a\":1,\"b\":2}"`                    |
| POJO（包括嵌套）             | JSON 对象                | `"{\"name\":\"Klaus\",\"age\":42}"`      |

默认值字符串在 AI 服务注册时解析。如果无法将其转换为参数的类型，
AI 服务的构建会立即失败，抛出 `IllegalConfigurationException`，
并指明有问题的参数——拼写错误会在启动时被发现，而不是在第一次 LLM 调用时。

**默认值只适用于参数缺失，不适用于错误的值。** 如果 LLM 提供了一个
无法完成类型强制转换的参数（例如把 `"banana"` 传给 `int`），类型转换错误会
照常传播——默认值*不会*被用作回退。

**默认值在每次调用时都会重新解析，**因此一个修改了带默认值的
`List`/`Map`/POJO 的工具不会污染后续的调用：

```java
@Tool
void process(@P(defaultValue = "[\"a\",\"b\"]") List<String> tags) {
    tags.add("processed"); // safe — next invocation still receives ["a","b"]
}
```

**限制**（在注册时以 `IllegalConfigurationException` 拒绝）：

- `defaultValue` 不能与 `Optional<T>` 组合使用 —— `Optional` 已经编码了
  "缺失"的语义；请只选用其中一种机制。
- `defaultValue` 不能设置在由 LangChain4j 注入的参数上（`@ToolMemoryId`、
  `InvocationContext` 等）—— 它们并不来自 LLM。

#### 多态工具参数

工具参数可以是多态类型——其具体子类型由
LLM 在调用时决定的基础类型。Sealed 接口和 sealed 类无需注解即可使用；
普通的抽象类和接口必须使用 Jackson 的
`@JsonSubTypes` 声明其子类型。
发送给 LLM 的 schema 包含针对所允许子类型的 `anyOf`，每个子类型都带有一个
判别属性（默认为 `"type"`），以便 LLM 表明它生成的是哪一种具体
类型；LangChain4j 会在调用你的工具方法之前，
把 LLM 的参数反序列化为正确的子类型。

这对作为参数的多态类型、由多态类型组成的
`List<T>` / `Set<T>`，以及嵌套在其他 POJO 参数内的多态类型都有效。

**Sealed 接口和类——无需注解：**

```java
sealed interface Animal permits Dog, Cat {}

record Dog(String name, String breed) implements Animal {}

record Cat(String name, boolean indoor) implements Animal {}

class AnimalRegistry {

    @Tool("Registers a single animal")
    void registerAnimal(Animal animal) { /* dispatched to Dog or Cat */ }

    @Tool("Registers a batch of animals")
    void registerAnimals(List<Animal> animals) { /* mixed Dog / Cat */ }

    @Tool("Registers an owner with their pet")
    void registerOwner(Owner owner) { /* Owner.pet is dispatched */ }
}

record Owner(String name, Animal pet) {}
```

**Jackson 的 `@JsonSubTypes` / `@JsonTypeInfo`** 也得到支持，它们允许你将传输线上的
名称与 Java 类名解耦：

```java
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "kind")
@JsonSubTypes({
    @JsonSubTypes.Type(value = Square.class, name = "square"),
    @JsonSubTypes.Type(value = Circle.class, name = "circle")
})
interface Shape {}

class ShapeRegistry {

    @Tool("Registers a shape")
    void registerShape(Shape shape) { /* dispatched to Square or Circle */ }
}
```

所支持的 `@JsonTypeInfo` 选项集合、判别属性名称的解析顺序、
`defaultImpl` 的行为、`visible` 标志以及字段冲突检测，在
结构化输出的[多态类型](structured-outputs.md#多态类型)一节中有
详细说明——它们同样适用于工具参数。

#### 递归参数

递归参数（例如 `Person` 类带有一个 `Set<Person> children` 字段）
目前仅由 OpenAI 支持。

### 工具方法的返回类型
带 `@Tool` 注解的方法可以返回任意类型，包括 `void`。
如果方法的返回类型是 `void`，当方法成功返回时，会向 LLM 发送 "Success" 字符串。

如果方法的返回类型是 `String`，返回值会原样发送给 LLM，不做任何转换。

对于其他返回类型，返回值在发送给 LLM 之前会被转换为 JSON 字符串。

#### 返回图像和多模态内容

工具还可以返回图像和其他非文本内容。当工具返回以下类型之一时，
结果会作为多模态内容（例如图像）发送给 LLM，而不是被序列化为 JSON 文本：

- `Image` —— 作为单个图像发送
- `ImageContent` —— 作为单个图像内容发送
- `Content` —— 作为单个内容元素发送（例如 `TextContent`、`ImageContent`）
- `List<Content>` —— 作为多个内容元素发送
- `Content[]` —— 作为多个内容元素发送

例如，一个拍照并返回图像的工具：
```java
@Tool("Takes a photo and returns it")
Image takePhoto() {
    byte[] imageBytes = camera.capture();
    return Image.builder()
            .base64Data(Base64.getEncoder().encodeToString(imageBytes))
            .mimeType("image/png")
            .build();
}
```

或者一个同时返回文本和图像的工具：
```java
@Tool("Takes a photo and returns it with a description")
List<Content> takePhoto() {
    Image image = camera.capture();
    return List.of(
            TextContent.from("Photo taken at " + LocalDateTime.now()),
            ImageContent.from(image)
    );
}
```

!!! note
  并非所有 LLM 提供商都支持多模态工具结果。
  目前支持在工具结果中包含图像的提供商包括 Anthropic、Amazon Bedrock 和 Google AI Gemini。
  如果工具返回非文本内容，其他提供商会抛出 `UnsupportedFeatureException`。

### 将 AI 服务用作其他 AI 服务的工具

AI 服务也可以被用作其他 AI 服务的工具。这在许多智能体用例中非常有用：其中一个 AI 服务可以请求另一个更专业的 AI 服务来帮助执行特定任务。例如，在定义了以下 AI 服务之后：

```java
    interface RouterAgent {

        @dev.langchain4j.service.UserMessage("""
            Analyze the following user request and categorize it as 'legal', 'medical' or 'technical',
            then forward the request as it is to the corresponding expert provided as a tool.
            Finally return the answer that you received from the expert without any modification.

            The user request is: '{{it}}'.
            """)
        String askToExpert(String request);
    }

    interface MedicalExpert {

        @dev.langchain4j.service.UserMessage("""
            You are a medical expert.
            Analyze the following user request under a medical point of view and provide the best possible answer.
            The user request is {{it}}.
            """)
        @Tool("A medical expert")
        String medicalRequest(String request);
    }

    interface LegalExpert {

        @dev.langchain4j.service.UserMessage("""
            You are a legal expert.
            Analyze the following user request under a legal point of view and provide the best possible answer.
            The user request is {{it}}.
            """)
        @Tool("A legal expert")
        String legalRequest(String request);
    }

    interface TechnicalExpert {

        @dev.langchain4j.service.UserMessage("""
            You are a technical expert.
            Analyze the following user request under a technical point of view and provide the best possible answer.
            The user request is {{it}}.
            """)
        @Tool("A technical expert")
        String technicalRequest(String request);
    }
```

`RouterAgent` 可以被配置为把另外 3 个 AI 服务用作工具，它们分别是特定领域的专家，负责将用户请求路由到其中一个。

```java
MedicalExpert medicalExpert = AiServices.builder(MedicalExpert.class)
        .chatModel(model)
        .build();
LegalExpert legalExpert = AiServices.builder(LegalExpert.class)
        .chatModel(model)
        .build();
TechnicalExpert technicalExpert = AiServices.builder(TechnicalExpert.class)
        .chatModel(model)
        .build();

RouterAgent routerAgent = AiServices.builder(RouterAgent.class)
        .chatModel(model)
        .tools(medicalExpert, legalExpert, technicalExpert)
        .build();

routerAgent.askToExpert("I broke my leg what should I do");
```

!!! note
  将 AI 服务用作其他 AI 服务的工具是一项强大的功能，它使构建复杂的智能体系统成为可能。然而，这种方法也伴随着一些重要且值得注意的缺点：
  - 这种实现要求 LLM 将用户请求不做任何修改地复制粘贴为一次工具调用，这可能是一个容易出错的操作。
  - 作为工具调用另一个 LLM 的那个 LLM，必须像任何其他工具调用一样重新处理其响应，这在时间和消耗的 token 两方面都可能是浪费的计算。
  - 充当工具的智能体是一个完全独立的 AI 服务，无法访问调用它的 agent 的聊天记忆，因此无法利用聊天记忆来提供更充分的回答。


### `@Tool`
任何带 `@Tool` 注解的 Java 方法，
只要在构建 AI 服务时被_显式_指定，就可以由 LLM 执行：
```java
interface MathGenius {
    
    String ask(String question);
}

class Calculator {
    
    @Tool
    double add(int a, int b) {
        return a + b;
    }

    @Tool
    double squareRoot(double x) {
        return Math.sqrt(x);
    }
}

MathGenius mathGenius = AiServices.builder(MathGenius.class)
    .chatModel(model)
    .tools(new Calculator())
    .build();

String answer = mathGenius.ask("What is the square root of 475695037565?");

System.out.println(answer); // The square root of 475695037565 is 689706.486532.
```

当 `ask` 方法被调用时，如上节所述，会与 LLM 发生 2 次交互。
在这些交互之间，`squareRoot` 方法会被自动调用。

`@Tool` 注解具有以下字段：
- `name`：工具的名称。如果未提供，方法名将作为工具的名称。
- `value`：工具的描述。
- `returnBehavior`：更多细节参见[这里](tools.md#立即返回工具执行请求的结果)
- `metadata`：一个有效的 JSON 字符串，包含针对特定 LLM 提供商的工具 metadata 条目。
默认情况下，它不会发送给 LLM 提供商，你必须在创建 `ChatModel` 时
明确指定应发送哪些 metadata 键。
目前，工具 metadata 仅由 `langchain4j-anthropic` 模块支持。

根据工具的不同，即使没有任何描述，LLM 也可能理解得很好
（例如，`add(a, b)` 就很明显），
但通常最好提供清晰且有意义的名称和描述。
这样，LLM 就有更多信息来决定是否调用给定的工具，以及该如何调用。

### 继承与工具发现

当你把一个工具对象传给 AI 服务时，LangChain4j 会从该对象的类、它的所有父类（直到但不包括 `Object`）以及所实现接口中的 `default` 和 `static` 方法中发现 `@Tool` 方法。

```java
class BaseMathTools {

    @Tool("Calculates the sum of two numbers")
    int sum(int a, int b) {
        return a + b;
    }
}

class AdvancedMathTools extends BaseMathTools {

    @Tool("Calculates the product of two numbers")
    int multiply(int a, int b) {
        return a * b;
    }
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .tools(new AdvancedMathTools()) // both "sum" and "multiply" are available
    .build();
```

子类可以重写父类中的 `@Tool` 方法。在这种情况下，只会使用子类的版本——包括其 `@Tool` 注解：

```java
class ParentTools {

    @Tool("Returns the greeting")
    String greet(String name) {
        return "Hello, " + name;
    }
}

class ChildTools extends ParentTools {

    @Override
    @Tool(name = "greet_formal", value = "Returns a formal greeting")
    String greet(String name) {
        return "Good day, " + name;
    }
}
```

在这里，LLM 将看到一个名为 `greet_formal`、描述为 "Returns a formal greeting" 的单个工具。

当一个方法重写或实现了带 `@Tool` 注解的方法而未重复该注解时，它同样是一个工具方法。
当工具在接口中声明、在别处实现时，这一点很方便：

```java
interface WeatherTools {

    @Tool("Returns the weather in the given city")
    String weather(String city);
}

class OpenMeteoWeatherTools implements WeatherTools {

    @Override
    public String weather(String city) {
        return ...;
    }
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .tools(new OpenMeteoWeatherTools()) // "weather" is available, described as declared in the interface
    .build();
```

除非重写方法声明了自己的 `@Tool` 注解，否则 LLM 看到的是被重写方法上的 `@Tool` 注解。

这也是当工具对象被包装在代理中时工具依然能正常工作的原因，
例如应用了 `@Aspect`、`@Transactional` 或 `@Async` 的 Spring bean。
这样的代理是一个重写了工具方法的生成子类，而 Java 不会把方法注解
复制到重写方法上，因此注解会在被代理的类上查找。
工具通过代理被调用，因此拦截器和切面仍然会执行。

如果子类声明了一个与父类方法同名但参数不同的方法（是重载，而非重写），两个方法都会被发现。由于工具名称必须唯一且默认使用方法名，你必须为其中至少一个方法指定显式的名称：

```java
class ParentTools {

    @Tool(name = "process_text", value = "Processes a text input")
    String process(String input) {
        return input.toUpperCase();
    }
}

class ChildTools extends ParentTools {

    @Tool(name = "process_number", value = "Processes a numeric input")
    int process(int input) {
        return input * 2;
    }
}
```

如果两个方法解析出相同的工具名称，在创建 AI 服务时会抛出 `IllegalArgumentException`。

### `@P`
方法参数可以选择性地用 `@P` 注解。

`@P` 注解具有以下可选字段：

- `name`：LLM 看到的参数名称。如果未指定，则使用实际的方法参数名。
- `description`：参数的描述（`value` 的别名）。默认为空。
- `value`：参数的描述（`description` 的别名）。默认为空。
- `required`：参数是否必填，默认为 `true`。

#### 参数名称

`name` 属性会覆盖 LLM 将看到的参数名称。
设置 `name` 在以下两种情况下有用：

1. **缺少 `-parameters` javac 选项。**
   没有 `-parameters` javac 选项时，Java 反射返回的是 `arg0`、`arg1` 等通用名称。
   参数的语义含义就会丢失，这可能会让 LLM 感到困惑。
   设置 `name` 可以恢复一个有意义的名称。
   请注意，Quarkus 和 Spring 等框架默认启用 `-parameters`，
   因此实际的方法参数名称会被保留，使用这些框架时你通常不需要设置 `name`。

2. **为 LLM 使用自定义名称。**
   当你希望 LLM 看到的参数名称与开发者在源代码中使用的不同
   （例如，为了匹配特定的 API 契约，或提供一个更具描述性的名称）。

#### 参数描述

`description` 和 `value` 可以互换——它们都用于设置 LLM 将看到的参数描述。
当只需要描述时，使用简写的 `value` 形式：
```java
@Tool
void getWeather(@P("The city name") String city) { ... }
```

当名称和描述都需要时，使用命名字段：
```java
@Tool
void getWeather(@P(name = "city", description = "The city name") String city) { ... }
```

### `@Description`
可以使用 `@Description` 注解指定类和字段的描述：

```java
@Description("Query to execute")
class Query {

  @Description("Fields to select")
  private List<String> select;

  @Description("Conditions to filter on")
  private List<Condition> where;
}

@Tool
Result executeQuery(Query query) {
  ...
}
```

!!! note
  请注意，放在 `enum` 值上的 `@Description` **_没有任何效果_**，并且**_不会_**被包含
  在生成的 JSON schema 中：
  ```java
  enum Priority {

      @Description("Critical issues such as payment gateway failures or security breaches.") // this is ignored
      CRITICAL,
      
      @Description("High-priority issues like major feature malfunctions or widespread outages.") // this is ignored
      HIGH,
      
      @Description("Low-priority issues such as minor bugs or cosmetic problems.") // this is ignored
      LOW
  }
  ```

### `InvocationParameters`
如果你希望在调用 AI 服务时向工具传递额外数据，可以使用 `InvocationParameters`：
```java

interface Assistant {
    String chat(@UserMessage String userMessage, InvocationParameters parameters);
}

class Tools {
    @Tool
    String getWeather(String city, InvocationParameters parameters) {
        String userId = parameters.get("userId");
        UserPreferences preferences = getUserPreferences(userId);
        return weatherService.getWeather(city, preferences.temperatureUnits());
    }
}

InvocationParameters parameters = InvocationParameters.from(Map.of("userId", "12345"));
String response = assistant.chat("What is the weather in London?", parameters);
```

在这种情况下，LLM 并不知道这些参数；
它们只对 LangChain4j 和用户代码可见。

`InvocationParameters` 也可以在其他 AI 服务组件内访问，例如：
- [`ToolProvider`](tools.md#动态指定工具)：在 `ToolProviderRequest` 内部
- [`ToolArgumentsErrorHandler`](tools.md#处理工具参数错误)
以及 [`ToolExecutionErrorHandler`](https://docs.langchain4j.dev/tutorials/tools#handling-tool-execution-errors)：
在 `ToolErrorContext` 内部
- [RAG 组件](rag.md)：在 `Query` -> `Metadata` 内部

参数存储在一个可变的、线程安全的 `Map` 中。

在单次 AI 服务调用期间，可以在 AI 服务组件之间
通过 `InvocationParameters` 传递数据
（例如，从一个工具到另一个工具，或从 RAG 组件到工具）。

### `InvocationContext`

与 `InvocationParameters` 类似，带 `@Tool` 注解的方法
可以接受一个 `InvocationContext` 参数，以获取关于
AI 服务调用的信息。

```java
class Tools {
    @Tool
    String getWeather(String city, InvocationContext context) {
        UUID invocationId = context.invocationId();
        String aiServiceInterfaceName = context.interfaceName();
        ...
    }
}
```

在这种情况下，LLM 并不知道这些参数；
它们只对 LangChain4j 和用户代码可见。

### `@ToolMemoryId`
如果你的 AI 服务方法有一个带 `@MemoryId` 注解的参数，
你也可以用 `@ToolMemoryId` 来注解 `@Tool` 方法的一个参数：

```java
interface Assistant{
    String chat(@UserMessage String userMessage, @MemoryId memoryId);
}

class Tools {
    @Tool
    String addCalendarEvent(CalendarEvent event, @ToolMemoryId memoryId) {
        ...
    }
}

String answer = assistant.chat("Tomorrow I will have a meeting with Klaus at 14:00", "12345");
```

提供给 AI 服务方法的值会被自动传递给 `@Tool` 方法。
如果你拥有多个用户，和/或每个用户拥有多个聊天/记忆，
并希望在 `@Tool` 方法内部将它们区分开来，那么这个功能会很有用。

### 并发执行工具

默认情况下，当 LLM 一次调用**_多个_**工具（也称为并行工具调用）时，
AI 服务会顺序执行它们。如果你希望工具被并发执行，
可以在构建 AI 服务时调用 `executeToolsConcurrently()` 或 `executeToolsConcurrently(Executor)`。
如果你启用了其中任一选项，工具将会被并发执行（有一个例外——见下文），
使用默认的或指定的 `Executor`。

#### 使用 `ChatModel` 时：
- 当 LLM 调用多个工具时，它们会在不同的线程中并发执行，
使用 `Executor`。
- 当 LLM 调用单个工具时，它会在同一个（调用者）线程中执行，
**_不会_**使用 `Executor`，以避免浪费资源。

#### 使用 `StreamingChatModel` 时：
- 当 LLM 调用多个工具时，它们会在不同的线程中并发执行，
使用 `Executor`。
每个工具都会在 `StreamingChatResponseHandler.onCompleteToolCall(CompleteToolCall)`
被调用时立即执行，而不会等待其他工具或等待响应流式传输完成。
- 当 LLM 调用单个工具时，它会使用 `Executor` 在一个单独的线程中执行。
我们不能在同一个线程中执行它，因为在那个时刻，
我们还不知道 LLM 将会调用多少个工具。

### 访问已执行的工具
如果你想访问在 AI 服务调用期间执行的工具，可以通过将返回类型包装在 `Result` 类中轻松做到这一点：
```java
interface Assistant {

    Result<String> chat(String userMessage);
}

Result<String> result = assistant.chat("Cancel my booking 123-456");

String answer = result.content();
List<ToolExecution> toolExecutions = result.toolExecutions();

ToolExecution toolExecution = toolExecutions.get(0);
ToolExecutionRequest request = toolExecution.request();
String result = toolExecution.result(); // tool execution result as text
List<Content> resultContents = toolExecution.resultContents(); // tool execution result as content list (may include images)
Object resultObject = toolExecution.resultObject(); // actual value returned by the tool
Map<String, Object> attributes = toolExecution.attributes(); // attributes of the tool execution result, see below
```

在流式模式下，你可以通过指定 `onToolExecuted` 回调来做到这一点：
```java
interface Assistant {

    TokenStream chat(String message);
}

TokenStream tokenStream = assistant.chat("Cancel my booking");

tokenStream
    .onToolExecuted((ToolExecution toolExecution) -> System.out.println(toolExecution))
    .onPartialResponse(...)
    .onCompleteResponse(...)
    .onError(...)
    .start();
```

### 工具结果属性

工具执行结果可以携带属性：一个**不会**发送给 LLM 的 `Map<String, Object>`。
属性对于只有你的应用才需要的数据非常有用，例如工具已创建的记录的 ID，
或者你的 UI 应渲染的小组件。

自定义的 `ToolExecutor` 可以设置属性：
```java
ToolExecutor toolExecutor = (toolExecutionRequest, context) -> ToolExecutionResult.builder()
        .resultText("Sunny, 22 degrees") // sent to the LLM
        .attributes(Map.of("widget", weatherWidget)) // not sent to the LLM
        .build();
```
对于 [MCP](mcp.md) 工具，属性来源于工具调用响应中的 `_meta` 字段。
对于这些工具，需要为工具提供商配置
[`returnToolResultAttributes(true)`](mcp.md#mcp-工具结果元数据)。

你可以从 `ToolExecution` 中读取属性（见上文[访问已执行的工具](#访问已执行的工具)）。
它们还会传播到 `ToolExecutionResultMessage.attributes()` 中，
因此会与消息一起存储在 [`ChatMemory`](chat-memory.md) 中。

!!! note
    如果你使用会持久化消息的 `ChatMemoryStore`，消息会被序列化为 JSON。
    请确保所有属性值都能序列化为 JSON，并且在反序列化后仍然有用：
    - 无法序列化的值（例如 `InputStream`）会导致整个存储操作失败。
    - 值会被反序列化为普通的 JSON 类型，因此作为属性存储的自定义对象
    会返回为 `Map`，再也无法转换回其原始类型。

    属性也会为每条消息存储，因此如果对话被持久化，请避免在其中放入大值。

### 以编程方式指定工具

在使用 AI 服务时，工具也可以通过编程方式指定。
这种方式提供了很大的灵活性，因为工具可以从
数据库和配置文件等外部来源加载。

工具的名称、描述、参数名称及其描述
都可以通过 `ToolSpecification` 进行配置：
```java
ToolSpecification toolSpecification = ToolSpecification.builder()
        .name("get_booking_details")
        .description("Returns booking details")
        .parameters(JsonObjectSchema.builder()
                .properties(Map.of(
                        "bookingNumber", JsonStringSchema.builder()
                                .description("Booking number in B-12345 format")
                                .build()
                ))
                .build())
        .build();
```

对于每个 `ToolSpecification`，都需要提供一个 `ToolExecutor` 实现，
由它来处理由 LLM 生成的工具执行请求：
```java
ToolExecutor toolExecutor = (toolExecutionRequest, memoryId) -> {
    Map<String, Object> arguments = fromJson(toolExecutionRequest.arguments());
    String bookingNumber = arguments.get("bookingNumber").toString();
    Booking booking = getBooking(bookingNumber);
    return booking.toString();
};
```

LangChain4j 还提供了 `DefaultToolExecutor`，它可以自动调用 Java 对象上的方法并处理
参数映射：
```java
class BookingTools {
    String getBookingDetails(String bookingNumber) {
        Booking booking = loadBookingFromDatabase(bookingNumber);
        return booking.toString();
    }
}

BookingTools tools = new BookingTools();
Method method = BookingTools.class.getMethod("getBookingDetails", String.class);
ToolExecutor toolExecutor = new DefaultToolExecutor(tools, method);
```

一旦你有了一个或多个（`ToolSpecification`, `ToolExecutor`）对，
就将每一对包装在 `AiServiceTool` 中，并将列表传递给 AI 服务：
```java
AiServiceTool tool = AiServiceTool.builder()
        .toolSpecification(toolSpecification)
        .toolExecutor(toolExecutor)
        .build();

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(List.of(tool))
    .build();
```

#### 为编程工具配置立即返回

如果你需要为某个工具指定
[立即返回行为](tools.md#立即返回工具执行请求的结果)，
请在 `AiServiceTool` 构建器上设置其 `ReturnBehavior`：

```java
AiServiceTool bookingTool = AiServiceTool.builder()
        .toolSpecification(bookingToolSpec)
        .toolExecutor(bookingExecutor)
        .returnBehavior(IMMEDIATE)
        .build();

AiServiceTool closeTool = AiServiceTool.builder()
        .toolSpecification(closeToolSpec)
        .toolExecutor(closeExecutor)
        .returnBehavior(IMMEDIATE_IF_LAST)
        .build();

AiServiceTool weatherTool = AiServiceTool.builder()
        .toolSpecification(weatherToolSpec)
        .toolExecutor(weatherExecutor)
        // ReturnBehavior.TO_LLM by default
        .build();

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(List.of(bookingTool, closeTool, weatherTool))
    .build();
```

### 动态指定工具

在使用 AI 服务时，工具也可以为每次调用动态指定。
你可以配置一个 `ToolProvider`，它会在每次调用 AI 服务时被调用，
并提供应包含在当前对 LLM 的请求中的工具。
`ToolProvider` 接收一个 `ToolProviderRequest`
（其中包含 `UserMessage`、聊天记忆 ID 以及 [`InvocationParameters`](tools.md#invocationparameters)），
并返回一个包含当前 AI 服务调用所用工具的 `ToolProviderResult`。

下面是一个示例，展示如何仅在用户消息中包含 "booking" 一词时才添加 `get_booking_details` 工具：
```java
ToolProvider toolProvider = (toolProviderRequest) -> {
    if (toolProviderRequest.userMessage().singleText().contains("booking")) {
        ToolSpecification toolSpecification = ToolSpecification.builder()
            .name("get_booking_details")
            .description("Returns booking details")
            .parameters(JsonObjectSchema.builder()
                .addStringProperty("bookingNumber")
                .build())
            .build();
        return ToolProviderResult.builder()
            .add(toolSpecification, toolExecutor)
            .build();
    } else {
        return null;
    }
};

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(model)
    .toolProvider(toolProvider)
    .build();
```

在同一次 AI 服务调用中，可以混合使用静态指定（包括使用 `@Tool` 注解的方法和以编程方式配置的工具）
和动态指定的工具。
在这种情况下，所有静态工具和动态工具会被合并在一起。

#### 为动态工具配置立即返回

在构建 `ToolProviderResult` 时，你可以使用 `ToolProviderResult.builder()`
为工具标记[立即返回](tools.md#立即返回工具执行请求的结果)。
`add(ToolSpecification, ToolExecutor, ReturnBehavior)` 重载方法
接受 `TO_LLM`、`IMMEDIATE` 或 `IMMEDIATE_IF_LAST` 中的任意一个：

```java
ToolProvider toolProvider = (toolProviderRequest) -> {
    return ToolProviderResult.builder()
        .add(bookingToolSpec, bookingExecutor, ReturnBehavior.IMMEDIATE)
        .add(closeToolSpec, closeExecutor, ReturnBehavior.IMMEDIATE_IF_LAST)
        .add(weatherToolSpec, weatherExecutor) // ReturnBehavior.TO_LLM by default
        .build();
};
```

### 工具搜索

在处理大量工具时，
每次请求都发送所有工具会显著增加 token 用量并降低模型性能。
为解决这一问题，LangChain4j 提供了一种工具搜索机制，
允许由 LLM 本身动态地发现工具，
而不是预先全部暴露。

其核心思想很简单：
- 最初，LLM 只被暴露一个或多个特殊的工具搜索工具
- LLM 可以调用这些工具来搜索相关的工具
- 一旦找到相关工具，它们就会包含在后续发给 LLM 的请求中

这使得工具发现过程具备可扩展性、token 高效性，且由模型驱动。

#### 工具搜索如何工作

典型的工具搜索流程如下：
1. 初始请求：
   - LLM 只能看到工具搜索工具（而非完整的工具集）
2. 工具搜索
   - LLM 调用工具搜索工具，描述它需要什么样的工具
   - 工具搜索策略将请求与可用工具进行匹配
4. 工具暴露
   - 匹配的工具会被添加到下一次发给 LLM 的请求中
5. 工具执行
   - LLM 现在可以像往常一样调用找到的工具

之前找到的工具会在多次工具搜索调用之间累积。
每当 LLM 调用工具搜索工具时，
新匹配的工具都会被添加到 LLM 可见的现有工具集合中（它们是合并，而非替换）。
这意味着 LLM 可见的工具列表可能会随时间增长。
找到的工具会保持对 LLM 可见，直到其对应的 `ToolExecutionResultMessage`
从 `ChatMemory` 中被逐出，并且至少会保持到 AI 服务调用结束。

如果没有配置 `ChatMemory`，找到的工具只会保持对 LLM 可见
到 AI 服务调用结束。

#### ToolSearchStrategy

工具搜索通过 `ToolSearchStrategy` 接口实现：

```java
@Experimental
public interface ToolSearchStrategy {

    List<ToolSpecification> getToolSearchTools(InvocationContext invocationContext);

    ToolSearchResult search(ToolSearchRequest toolSearchRequest);
}
```

一个 `ToolSearchStrategy` 负责：
- 向 LLM 暴露工具搜索工具
- 执行由 LLM 生成的工具搜索请求
- 返回匹配的工具名称，这些名称随后会被解析并暴露

LangChain4j 目前提供 3 种开箱即用的实现：
- `SimpleToolSearchStrategy` – 基于关键词的匹配
- `VectorToolSearchStrategy` – 使用嵌入进行语义搜索
- `DecisionModelToolSearchStrategy` – 由[决策模型](decision-models.md#选择工具)决定哪些工具匹配搜索

有关更多详细信息，请参阅这些类的 Javadoc。

你也可以实现自定义策略。

#### 在 AI 服务中配置工具搜索

工具搜索在 AI 服务层面进行配置：

```java
Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .chatMemory(chatMemory)
    .tools(tools) // tool search works for static tools
    .toolProvider(mcpToolProvider) // tool search works for tools provided dynamically (e.g., MCP)
    .toolSearchStrategy(new SimpleToolSearchStrategy())
    .build();
```

配置完成后：
- LLM 不再预先看到所有工具
- 工具发现成为一个显式的、由模型驱动的步骤
- token 用量降低，尤其是在工具集很大的情况下

#### 何时使用工具搜索

工具搜索在以下情况下特别有用：
- 你有大量工具（数十个或数百个）
- 工具是特定领域的或很少使用
- 工具的可用性取决于上下文、用户或权限
- 你希望 LLM 推理出它需要哪些工具，而不是从长长的列表中猜测

如果你只有少量工具，或者所有工具始终相关，
使用常规方法可能更简单。

#### 始终可见的工具

启用工具搜索后，工具通常会对 LLM 隐藏，直到通过工具搜索调用被发现。
然而，在某些情况下，你可能希望某些工具始终对 LLM 可见。

典型的使用场景：
- 应始终可访问的核心工具
- 频繁使用的工具，无需搜索开销
- 实用工具

LangChain4j 通过 `ALWAYS_VISIBLE` 工具搜索行为支持这一点。

##### 工作原理

当一个工具被标记为 `ALWAYS_VISIBLE` 时：
- 它会在第一个请求中就被暴露给 LLM
- 它不需要通过工具搜索来发现
- 它在整个 AI 服务调用期间保持可见
- 它不会被包含在可搜索的工具候选中

所有其他工具仍然遵循常规的工具搜索流程。

##### 使用 `@Tool` 注解

你可以通过 @Tool 注解将工具标记为始终可见：
```java
@Tool(searchBehavior = ALWAYS_VISIBLE)
String getWeather(String city) {
    return weatherService.getWeather(city);
}
```

##### 使用 `McpToolProvider`

在使用 MCP 工具（通过 `McpToolProvider`）时，始终可见的工具可以通过 `alwaysVisibleToolNames` 配置：

```java
McpToolProvider.builder()
    .mcpClients(mcpClient)
    .alwaysVisibleToolNames("getWeather")
    .build();
```

##### 使用 `ToolSpecification`

如果你以编程方式配置工具，可以使用 `metadata` 将它们标记为始终可见：
```java
ToolSpecification toolSpecification = ToolSpecification.builder()
    .name("getWeather")
    .parameters(JsonObjectSchema.builder()
        .addStringProperty("city")
        .required("city")
        .build())
    .metadata(Map.of(ToolSpecification.METADATA_SEARCH_BEHAVIOR, SearchBehavior.ALWAYS_VISIBLE))
    .build();
```

#### 注意事项与限制

!!! note
    工具搜索依赖于 LLM 理解何时以及如何搜索工具的能力。
    该功能的效果在很大程度上取决于所选的模型。

!!! note
    工具搜索目前被标记为实验性功能，可能会在未来版本中演进。

### 立即返回工具执行请求的结果

默认情况下，工具执行请求的结果会被发送回 LLM，
由 LLM 使用该结果并进一步重新处理它。然而，在某些情况下，
该工具执行请求产生的结果已经代表了 AI 服务调用的预期结果。
在这种情况下，可以配置工具
立即/直接返回其结果，跳过由 LLM 进行的浪费且消耗资源的
重新处理。这可以通过配置 `@Tool` 注解的 `returnBehavior` 字段来实现，
如下面的示例所示：

```java
class CalculatorWithImmediateReturn {
    
    @Tool(returnBehavior = ReturnBehavior.IMMEDIATE)
    double add(int a, int b) {
        return a + b;
    }
}
```

这样，一个如下所示的 `Assistant` 服务

```java
interface Assistant {
    Result<String> chat(String userMessage);
}
```

被配置为使用上面的 `CalculatorWithImmediateReturn` 工具

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(model)
        .tools(new CalculatorWithImmediateReturn())
        .build();
```

将直接从工具调用返回响应。例如，向助手发送如下提示：

```java
Result<String> result = assistant.chat("How much is 37 plus 87?");
```

将产生一个 `Result.content() == null` 的 `Result`，
而实际的响应 `124` 则必须从 `result.toolExecutions()` 中获取。
如果没有立即返回，LLM 将不得不重新处理 `add` 工具执行请求的结果，
从而返回如下响应：`The result of adding 37 and 87 is 124.`

#### 非 `Result` 类型的 AI 服务方法返回类型

如果你的 AI 服务方法签名不返回 `Result` 类型，那么当存在立即工具调用时，
你的聊天方法调用可能会成功也可能会失败，具体基于以下规则：

* 如果 AI 服务方法的返回类型是 void，请求将成功。
* 如果存在任何非立即的工具调用，请求将抛出 `IllegalConfigurationException` 异常而失败。
* 如果所有工具执行的结果都是 null（或 void）且返回类型不是基本类型，请求将成功，返回值将为 `null`。
* 如果恰好有一个非 null 的工具执行结果，并且该结果可以解析为返回类型，则请求将成功并返回该工具结果。
* 如果存在多个非 null 的工具执行结果，请求将抛出 `IllegalConfigurationException` 异常而失败。
* 如果有一个工具执行结果且其无法解析为返回类型，请求将抛出 `IllegalConfigurationException` 异常而失败。

#### 单次响应中多次工具调用的立即返回规则

当 LLM 在单个响应中返回多个工具调用时，
只有当以下**两个**条件同时成立时，循环才会立即返回（不将结果发送回 LLM）：

1. **没有任何工具出错。** 任何工具调用中的任何错误都会强制重新处理，以便 LLM 能在下一轮对错误做出反应。
2. **要么** 响应中的每个工具都是 `IMMEDIATE`（没有混入 `TO_LLM` 工具）**要么** 最后一个工具是 `IMMEDIATE_IF_LAST`（参见下一节）。

示例（工具按 LLM 在单个响应中返回的顺序列出；
`(err)` 标记执行出错的工具）：

| 响应中的工具调用 | 结果 | 原因 |
|---|---|---|
| `[IMMEDIATE]` | 立即返回 | 唯一工具是 `IMMEDIATE` |
| `[IMMEDIATE, IMMEDIATE]` | 立即返回 | 每个工具都是 `IMMEDIATE`/`IMMEDIATE_IF_LAST` |
| `[IMMEDIATE, TO_LLM]` | 重新处理 | `TO_LLM` 使全部立即返回规则失效 |
| `[IMMEDIATE_IF_LAST]` | 立即返回 | 最后一个工具是 `IMMEDIATE_IF_LAST` |
| `[TO_LLM, IMMEDIATE_IF_LAST]` | 立即返回 | 最后一个工具是 `IMMEDIATE_IF_LAST` |
| `[IMMEDIATE_IF_LAST, TO_LLM]` | 重新处理 | 不是最后一个，且 `TO_LLM` 使全部立即返回规则失效 |
| `[IMMEDIATE, IMMEDIATE_IF_LAST]` | 立即返回 | 最后一个工具是 `IMMEDIATE_IF_LAST` |
| `[IMMEDIATE_IF_LAST, IMMEDIATE]` | 立即返回 | 每个工具都是 `IMMEDIATE`/`IMMEDIATE_IF_LAST` |
| `[TO_LLM, IMMEDIATE_IF_LAST, IMMEDIATE]` | 重新处理 | 不是最后一个，且 `TO_LLM` 使全部立即返回规则失效 |
| `[IMMEDIATE_IF_LAST(err)]` | 重新处理 | 任何错误都会禁用立即返回 |
| `[TO_LLM(err), IMMEDIATE_IF_LAST]` | 重新处理 | 任何错误都会禁用立即返回 |

有关完整的立即返回与重新处理对照矩阵，请参阅 `ReturnBehavior` 的 Javadoc。

#### 用于显式结束动作序列的 `IMMEDIATE_IF_LAST`

`ReturnBehavior.IMMEDIATE_IF_LAST` 专为 LLM 用来显式标示
多步骤动作结束的工具而设计——例如，LLM 在一连串点击、导航等操作
之后追加的 `endExecutionAndGetFinalResult` 工具。

如果没有 `IMMEDIATE_IF_LAST`，LLM 通常需要两轮才能结束执行：
第一轮将工作工具（`TO_LLM`）与结束工具混合使用，
第二轮 LLM 在看到所有结果后，
单独调用结束工具。循环只在第二轮才会立即返回。

有了 `IMMEDIATE_IF_LAST`，只要 LLM 将该工具放在其响应的最后，
循环就会立即返回——每次调用节省一个完整的 LLM 往返。

```java
class ScreenAutomation {

    @Tool
    String leftMouseClick(int x, int y) { /* ... */ }

    @Tool
    String typeText(String text) { /* ... */ }

    @Tool(returnBehavior = ReturnBehavior.IMMEDIATE_IF_LAST)
    String endExecutionAndGetFinalResult(String summary) { return summary; }
}
```

对于 `[leftMouseClick, typeText, endExecutionAndGetFinalResult]` 这样的 LLM 响应，
循环在执行完全部三个工具后立即返回。
如果 LLM 将结束工具放在除最后以外的任何位置
（例如 `[endExecutionAndGetFinalResult, leftMouseClick]`），
循环将继续执行并将所有结果发送回 LLM。

`IMMEDIATE_IF_LAST` 也计入 `IMMEDIATE` 的全部立即返回规则：
仅由 `IMMEDIATE` 和/或 `IMMEDIATE_IF_LAST` 工具组成的响应会立即返回，
无论哪个在最后（仍受无错误规则约束）。

与 `IMMEDIATE` 一样，`IMMEDIATE_IF_LAST` 只允许用于返回类型为 `Result<T>` 的 AI 服务。

### 错误处理

!!! note
    以下默认行为适用于同步模式和 `TokenStream` 模式。异步模式和响应式模式
    已经按照默认行为的计划方式运行：工具*执行*错误会使调用失败，
    除非异常指明了可以告知 LLM 的内容；而工具*参数解析*错误会被发送给 LLM，
    而不是使调用失败。你显式配置的处理器会被所有模式使用。
    请参阅 [非阻塞与响应式](non-blocking.md#工具错误)。

#### 现成的处理器

两个处理器接口都为最常见的情形提供了现成的实现，
因此在这些情形下你无需自己编写处理器：

| 处理器 | 工具失败时会发生什么 |
|---|---|
| `ToolArgumentsErrorHandler.sendExceptionMessageToLlm()` | 错误的消息会被发送给 LLM，以便它能纠正参数并重试。AI 服务调用将继续。⚠️ 参见下方的警告。 |
| `ToolArgumentsErrorHandler.failInvocation()` | 错误会被重新抛出：AI 服务调用失败，且不会向 LLM 发送任何内容。 |
| `ToolExecutionErrorHandler.sendExceptionMessageToLlm()` | 工具抛出的异常的消息会被发送给 LLM（如果异常实现了 `ToolErrorVisibleToLlm`，则为 `messageForLlm()` 的文本），以便 LLM 对其做出反应。AI 服务调用将继续。⚠️ 参见下方的警告。 |
| `ToolExecutionErrorHandler.failInvocationUnlessVisibleToLlm()` | 只有实现了 `ToolErrorVisibleToLlm` 的异常会以它们提供的文本显示给 LLM。其他所有异常都会使 AI 服务调用失败。参见[逐异常决定 LLM 看到什么](#逐异常决定-llm-看到什么)。 |
| `ToolExecutionErrorHandler.sendGenericMessageToLlmUnlessVisibleToLlm(String)` | 实现了 `ToolErrorVisibleToLlm` 的异常会以它们提供的文本显示给 LLM。对于其他所有异常，会将给定的通用消息发送给 LLM，并以 WARN 级别记录该异常。AI 服务调用将继续。 |
| `ToolExecutionErrorHandler.failInvocation()` | 异常会被重新抛出：AI 服务调用失败，且不会向 LLM 发送任何内容。 |

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolArgumentsErrorHandler(ToolArgumentsErrorHandler.sendExceptionMessageToLlm())
        .toolExecutionErrorHandler(ToolExecutionErrorHandler.failInvocation())
        .build();
```

对于其他任何情况——在向 LLM 展示之前净化错误，或者基于错误类型做出决定——
请按照下面各节的说明自行编写处理器。

!!! warning 将异常消息发送给 LLM 可能会暴露敏感数据
    异常的消息通常是写给开发者的，而不是写给 LLM 的：它可能包含内部
    应用细节，例如文件路径、SQL、嵌入在错误字符串中的凭据、下游
    服务的响应或个人数据。所有发送给 LLM 的内容都会到达 LLM 提供商，
    被存储在聊天记忆中，
    并可能最终出现在用户读取的回答中、日志中以及可观测性管道中。

    只有当你确信所有工具的异常消息都是带着这一考量编写的，
    才使用 `sendExceptionMessageToLlm()`。否则请向 LLM 发送失败的
    通用或已净化的描述，
    并将详细信息保留在你的日志中。

!!! note
    当 AI 服务配置了工具，但未显式配置错误处理器时，
    LangChain4j 会在每个 JVM 中记录一次警告。显式配置处理器
    （使用本页面的任意选项）会消除该警告，并使你的应用不受
    计划的默认行为变更的影响。
    也可以通过将 `dev.langchain4j.service.ToolErrorHandlingNotice` 日志记录器的日志级别设置为 `OFF`
    来关闭该警告。

##### 在 Quarkus 中配置处理器

本页面的示例使用 `AiServices.builder(...)`。在 Quarkus 中，AI 服务通过
`@RegisterAiService` 声明，处理器通过接口上的静态方法配置：

```java
@RegisterAiService
public interface Assistant {

    String chat(String userMessage);

    @HandleToolExecutionError
    static ToolErrorHandlerResult onToolError(Throwable error, ToolErrorContext context) {
        return ToolExecutionErrorHandler.failInvocationUnlessVisibleToLlm().handle(error, context);
    }
}
```

对于整个应用，声明一个实现 `ToolExecutionErrorHandler` 的类，并用
`@DefaultToolExecutionErrorHandler` 注解它（限定符放在类型上，而不是放在生产者方法上）。

请注意，Quarkus 自行构建其 AI 服务，因此上述警告不会在那里被记录。
Quarkus 还使用其自己的默认工具执行错误处理器，该处理器将异常的消息
发送给 LLM，并且不查看 `ToolErrorVisibleToLlm`。要使其遵守该接口，请显式
配置 `failInvocationUnlessVisibleToLlm()` 或 `sendExceptionMessageToLlm()`，如上所示。

##### 在 Spring Boot 中配置处理器

使用 Spring Boot starter 时，AI 服务通过 `@AiService` 声明，处理器作为 bean 声明：

```java
@Configuration
class ToolErrorHandlingConfig {

    @Bean
    ToolExecutionErrorHandler toolExecutionErrorHandler() {
        return ToolExecutionErrorHandler.failInvocationUnlessVisibleToLlm();
    }

    @Bean
    ToolArgumentsErrorHandler toolArgumentsErrorHandler() {
        return ToolArgumentsErrorHandler.sendExceptionMessageToLlm();
    }
}
```

在默认（自动）装配模式下，这些 bean 会被每个 `@AiService` 使用。
在显式装配模式下，每个 AI 服务会指明其使用的 bean：

```java
@AiService(
        wiringMode = EXPLICIT,
        chatModel = "openAiChatModel",
        tools = "bookingTools",
        toolExecutionErrorHandler = "toolExecutionErrorHandler",
        toolArgumentsErrorHandler = "toolArgumentsErrorHandler")
interface Assistant {

    String chat(String userMessage);
}
```

有关装配模式的更多详细信息，请参阅
[Spring Boot 集成](spring-boot-integration.md#显式组件装配)。


#### 处理工具名称错误

LLM 可能会在工具调用上产生幻觉，
换句话说，即它要求使用一个名称不存在的工具。
在这种情况下，默认情况下 LangChain4j 会抛出一个报告该问题的异常，
但你也可以为 AI 服务提供在此情形下使用的策略，从而配置不同的行为。

该策略是 `Function<ToolExecutionRequest, ToolExecutionResultMessage>` 的一个实现，
它定义了对于包含调用不可用工具请求的 `ToolExecutionRequest`，应产生哪个 `ToolExecutionResultMessage` 作为结果。
例如，可以为 AI 服务配置一种策略，该策略向 LLM 返回一个响应，希望该响应能促使 LLM 在得知之前所需的工具不存在的情况下重试不同的工具调用，如下面的示例所示：

```java
AssistantHallucinatedTool assistant = AiServices.builder(AssistantHallucinatedTool.class)
        .chatModel(chatModel)
        .tools(new HelloWorld())
        .hallucinatedToolNameStrategy(toolExecutionRequest -> ToolExecutionResultMessage.from(
                toolExecutionRequest, "Error: there is no tool called " + toolExecutionRequest.name()))
        .build();
```

#### 处理工具参数错误

默认情况下，当工具参数出现问题时（例如 LLM 生成了无效的 JSON
或遗漏了必需参数），AI 服务将无法执行该工具，因此会
以异常失败。

!!! caution 建议：将参数错误反馈给 LLM
    当前的默认行为（抛出异常）很少是你想要的。
    参数错误通常来自 LLM，而当 LLM 得到清晰的
    错误消息时，通常能够自我纠正。配置一个返回错误文本的 `ToolArgumentsErrorHandler`，以便 LLM
    可以用更正后的参数重试。

    我们计划在未来的版本中将默认行为更改为这种行为。如果这一计划中的
    变更会影响你的使用场景，请[提交一个 issue](https://github.com/langchain4j/langchain4j/issues)，
    以便我们在其落地之前听到你的反馈。

你可以通过在 AI 服务上配置 `ToolArgumentsErrorHandler` 来自定义此行为：

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolArgumentsErrorHandler((error, errorContext) -> ...)
        .build();
```

目前，在 `ToolArgumentsErrorHandler` 内部处理错误有两种方式：

- 返回一条文本消息（例如错误描述），它会发送回 LLM，使其能够适当地响应（例如纠正错误并重试）。
- 抛出异常：这将停止 AI 服务流程。

**推荐（让 LLM 重试）：**

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolArgumentsErrorHandler(ToolArgumentsErrorHandler.sendExceptionMessageToLlm())
        .build();
```

**严格（遇到任何参数错误都停止流程）：**

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolArgumentsErrorHandler(ToolArgumentsErrorHandler.failInvocation())
        .build();
```

如果你希望 AI 服务以你自己类型的异常失败，就从处理器中抛出它：

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolArgumentsErrorHandler((error, errorContext) -> { throw MyCustomException(error); })
        .build();

try {
    assistant.chat(...);
} catch (MyCustomException e) {
    // handle e
}
```

##### 访问原始异常

当工具抛出一个包装了另一个异常的异常时（例如 `ToolGuardrailException` 包装了 `SecurityException`），
LangChain4j 会通过 `getCause()` 提取内部原因，并将其作为 `error` 参数传递。
使用 `errorContext.rawError()` 可以访问最初抛出的外层异常——当包装器类型
（而非原因）决定错误应如何处理时，这很有用。

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolArgumentsErrorHandler((error, errorContext) -> {
            if (errorContext.rawError() instanceof MyCriticalException) {
                throw (MyCriticalException) errorContext.rawError();
            }
            return ToolErrorHandlerResult.text(error.getMessage());
        })
        .build();
```

#### 处理工具执行错误

默认情况下，当用 `@Tool` 注解的方法抛出 `Exception` 时，
该 `Exception` 的消息（`e.getMessage()`）会作为该工具执行的结果发送给 LLM。
这允许 LLM 在认为必要时纠正其错误并重试。

!!! warning 建议：在生产环境中不要将原始异常消息发送给 LLM
    当前的默认行为会将原始异常消息发送回 LLM。在生产环境中，这可能会泄漏
    内部应用数据：堆栈跟踪、文件路径、嵌入在错误字符串中的凭据、
    下游 API 响应、错误消息中的个人身份信息（PII）等。
    一旦喂给 LLM，这些内容可能会流入响应、聊天历史、可观测性管道
    以及 LLM 提供商的日志。

    请配置一个 `ToolExecutionErrorHandler`，返回通用消息或经过整理/净化的
    失败描述，并依赖你自己的日志和可观测性事件来获取底层细节。
    请注意，一旦你配置了处理器，LangChain4j 就不再替你记录工具失败日志——那条日志的存在
    只是为了向你警告默认行为。

    我们计划在未来的版本中更改默认行为，
    改为 [`failInvocationUnlessVisibleToLlm()`](#逐异常决定-llm-看到什么)：AI 服务调用失败，
    除非异常本身指明了可以告知 LLM 的内容。如果这一计划中的变更会影响你的
    使用场景，请[提交一个 issue](https://github.com/langchain4j/langchain4j/issues)，以便我们在其
    落地之前听到你的反馈。

你可以通过在 AI 服务上配置 `ToolExecutionErrorHandler` 来自定义此行为。

**推荐（让每个异常自行决定，参见[下文](#逐异常决定-llm-看到什么)）：**

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolExecutionErrorHandler(ToolExecutionErrorHandler.failInvocationUnlessVisibleToLlm())
        .build();
```

**严格（任何失败都不会到达 LLM）：**

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolExecutionErrorHandler(ToolExecutionErrorHandler.failInvocation())
        .build();
```

**让 LLM 对失败做出反应，但不暴露异常消息：**

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolExecutionErrorHandler((error, errorContext) -> ToolErrorHandlerResult.text("Tool execution failed."))
        .build();
```

**当前默认行为（将异常的消息发送给 LLM）- ⚠️ 参见上方关于暴露敏感数据的警告：**

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolExecutionErrorHandler(ToolExecutionErrorHandler.sendExceptionMessageToLlm())
        .build();
```

与 `ToolArgumentsErrorHandler` 一样，在 `ToolExecutionErrorHandler` 中处理错误有两种方式：
返回文本消息或抛出异常。在决定如何处理时，你可以使用 `errorContext.rawError()`
在解包原因之前检查原始错误。

##### 逐异常决定 LLM 看到什么

把每个异常都发送给 LLM 是有风险的，而在每个异常上都失败又会剥夺 LLM
从本可绕过的故障中恢复的能力。通常你想要的是介于两者之间的方案：
LLM 应该知道它编造的 ID 没有对应的订单，但不应该知道
你的数据库名为 `ORDERS_V2` 并且拒绝了该查询。

要表达这一点，请让你的异常实现 `ToolErrorVisibleToLlm`，并在
`messageForLlm()` 中确切地写明应该告知 LLM 的内容：

```java
public class OrderNotFoundException extends RuntimeException implements ToolErrorVisibleToLlm {

    private final String orderId;

    public OrderNotFoundException(String orderId) {
        super("Order " + orderId + " not found");
        this.orderId = orderId;
    }

    @Override
    public String messageForLlm() {
        return "There is no order with ID " + orderId + ". Ask the user to check the order number.";
    }
}
```

如果你不想声明异常类，可以改抛一个现成的异常。
如果需要，自行记录原始错误：它会被保留为原因（cause），但不会被发送给 LLM。

```java
@Tool("Returns the status of an order")
String orderStatus(String orderId) {
    try {
        return orderService.status(orderId);
    } catch (SQLException e) {
        // the LLM is told only what it needs to know; the cause is not sent to it
        log.warn("Could not read the order database", e);
        throw ToolErrorVisibleToLlm.from("The order database is temporarily unavailable.", e);
    }
}
```

然后配置遵守它的处理器：

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .tools(tools)
        .toolExecutionErrorHandler(ToolExecutionErrorHandler.failInvocationUnlessVisibleToLlm())
        .build();
```

这样一来，`OrderNotFoundException` 会以 "There is no order with ID ..." 的形式到达 LLM，
而 `NullPointerException` 或失败的数据库连接会使 AI 服务调用失败，
于是你会察觉到问题，而不是 LLM 悄悄地向你的用户道歉。

LangChain4j 提供的工具，例如 [技能](skills.md)、工具搜索以及
[MCP](mcp.md) 工具，对于 LLM 可以采取行动的（例如缺少
参数或未知的技能名称），会用实现了 `ToolErrorVisibleToLlm` 的
`LlmVisibleToolExecutionException` 来报告这些错误，因此使用这个处理器时，
LLM 也仍然能看到这些错误。

对于你无法修改的异常——通常是库抛出的异常——请自行编写处理器，
并在那里决定告知 LLM 的内容：

```java
.toolExecutionErrorHandler((error, errorContext) -> {
    if (error instanceof EntityNotFoundException) {
        return ToolErrorHandlerResult.text("That record does not exist.");
    }
    throw new RuntimeException(error);
})
```

!!! note
    不要将库异常的消息原样传递给 LLM：它是写给开发者的，可能
    包含内部细节，就像你自己异常的消息一样。

!!! note
    `failInvocationUnlessVisibleToLlm()` 是我们计划在未来的
    版本中设为默认的行为。现在就显式配置它，意味着该变更不会影响你的应用。

### 补偿工具动作

当 AI 服务使用多个工具来完成一项任务时，其中一个工具的
失败可能使系统处于不一致的状态——一些工具已经
成功执行，而其他工具还没有。例如，在银行转账中，LLM 可能
先向收款人的账户贷记，然后由于余额不足而从付款人的
账户取款失败，导致收款人账户多出钱来。

为处理这种情况，你可以启用**工具错误时的补偿**。启用后，
如果任何工具执行失败，所有声明了补偿动作且之前
成功的工具调用都会按相反顺序自动撤销。

#### 使用 `@CompensateFor` 声明补偿动作

在方法上使用 `@CompensateFor` 注解，将其声明为某个 `@Tool` 的
补偿动作。`value` 必须与暴露给 LLM 的工具名称相匹配——
如果设置了 `@Tool(name = ...)` 属性，则为该属性值；否则为 `@Tool`
方法名（默认用作工具名称）。
补偿方法必须与工具具有相同的参数类型，
或者接受单个 `ToolExecution` 参数。

**选项 1：相同的参数类型** —— 补偿方法接收传递给
原始工具的相同参数：

```java
class BankAccountService {

    @Tool("credits money to a bank account")
    void credit(String name, double amount) {
        accounts.merge(name, amount, Double::sum);
    }

    @CompensateFor("credit")
    void uncredit(String name, double amount) {
        accounts.merge(name, -amount, Double::sum);
    }

    @Tool("withdraws money from a bank account")
    void withdraw(String name, double amount) {
        if (accounts.getOrDefault(name, 0.0) < amount) {
            throw new RuntimeException("Insufficient funds");
        }
        accounts.merge(name, -amount, Double::sum);
    }

    @CompensateFor("withdraw")
    void unwithdraw(String name, double amount) {
        accounts.merge(name, amount, Double::sum);
    }
}
```

**选项 2：`ToolExecution` 参数** —— 补偿方法接收完整的
`ToolExecution`，从而可以同时访问原始参数和工具的
**返回值**。当撤销某个动作需要原始执行
所产生的信息（例如交易 ID）时，这很有用：

```java
class BankAccountService {

    @Tool("credits money to a bank account")
    String credit(String name, double amount) {
        accounts.merge(name, amount, Double::sum);
        return createTransactionRecord(name, amount); // e.g. "TX-42"
    }

    @CompensateFor("credit")
    void uncredit(ToolExecution toolExecution) {
        String transactionId = toolExecution.result(); // "TX-42"
        reverseTransaction(transactionId);
    }
}
```

#### 启用补偿

在构建 AI 服务时调用 `.compensateOnToolErrors(true)`：

```java
Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(model)
        .tools(new BankAccountService())
        .compensateOnToolErrors(true)
        .build();
```

在此配置下，如果 LLM 调用 `credit("Dmytro", 100)`，然后
调用失败的 `withdraw("Mario", 100)`，框架会自动调用
`uncredit("Dmytro", 100)` 来撤销该贷记。框架不会抛出异常，
而是为每个工具向 LLM 发送信息性的结果消息：
被回滚的工具会得到类似 _"Tool 'credit' was executed successfully but
was rolled back due to failure of tool 'withdraw'"_ 的消息，而失败的工具会
得到其常规错误消息。这使 `ChatMemory` 保持一致，并让 LLM
决定接下来要做什么——重试、告知用户，或采取不同的方法。

如果没有 `.compensateOnToolErrors(true)`，错误会像往常一样发送回 LLM，并且不会
发生补偿——即使存在 `@CompensateFor` 注解也是如此。

#### 校验

启用 `.compensateOnToolErrors(true)` 时，每个 `@CompensateFor` 都会被校验：
- 所引用的工具必须（按名称）存在于同一个对象上。
- 补偿方法必须与工具具有完全相同的参数类型，
  或者接受单个 `ToolExecution` 参数。

如果任一检查失败，会立即抛出 `IllegalConfigurationException`，
从而在启动时（而非运行时）捕获配置错误。
如果未启用 `.compensateOnToolErrors(true)`，`@CompensateFor` 注解
会被静默忽略，并且不会执行任何校验。

#### 注意事项与限制

!!! note
    补偿是尽力而为的：如果补偿动作本身抛出异常，它会被
    以 WARN 级别记录，剩余的补偿动作会继续执行。

!!! note
    `@CompensateFor` 方法不会暴露给 LLM —— 它们是内部补偿
    基础设施，不出现在工具规范中。

!!! note
    补偿动作始终按相反顺序顺序执行，即使通过 `.executeToolsConcurrently()`
    将工具执行配置为并行运行也是如此。

!!! note
    `@CompensateFor` 方法可以从超类继承，这与
    `@Tool` 方法的发现方式一致。

!!! note
    `@CompensateFor` 仅适用于使用 `@Tool` 注解的方法。以编程方式
    或动态定义的工具（例如 MCP 工具、通过 `ToolSpecification` 注册的工具）
    不受支持。

!!! note
    补偿工具动作目前被标记为实验性功能，可能会在
    未来版本中演进。

## 模型上下文协议（MCP）

你还可以从 [MCP 服务器导入工具](https://modelcontextprotocol.io/docs/concepts/tools)。
有关此功能的更多信息，可以查看[这里](mcp.md#创建-mcp-工具提供器)。

!!! note
    在异步和响应式 AI 服务模式下，工具的行为有所不同：它们始终在 `Executor` 上运行，
    因此**默认并发执行**（向
    `executeToolsConcurrently(Executor)` 传递单线程 `Executor` 即可串行化它们），工具**执行**错误会使调用失败，而工具
    **参数解析**错误会被发送回 LLM，并且手写的 `ToolExecutor` 应实现
    `executeAsync(...)`，否则它会直接报错失败，而不是阻塞一个线程。
    请参阅 [非阻塞与响应式](non-blocking.md)。

## 相关教程

- [关于工具的绝佳指南](https://www.youtube.com/watch?v=cjI_6Siry-s)
  由 [Tales from the jar side (Ken Kousen)](https://www.youtube.com/@talesfromthejarside) 制作

## 示例

- [带工具的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithToolsExample.java)
- [带动态工具的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithDynamicToolsExample.java)
@

